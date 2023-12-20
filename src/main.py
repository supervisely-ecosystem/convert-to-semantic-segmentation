import os
from distutils.util import strtobool

from dotenv import load_dotenv
from tqdm import tqdm

import supervisely as sly

if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))


@sly.handle_exceptions
def main():
    api = sly.Api.from_env()

    # check the workspace exists
    workspace_id = sly.env.workspace_id()
    project_id = sly.env.project_id()
    need_rasterize = bool(strtobool(os.getenv("modal.state.needRasterize")))
    need_add_bg = bool(strtobool(os.getenv("modal.state.addBackgroundMask")))

    _bg_class_name = "__bg__"
    _bg_obj_class = sly.ObjClass(_bg_class_name, sly.Bitmap, color=[0, 0, 0])

    src_project = api.project.get_info_by_id(project_id)
    src_project_meta_json = api.project.get_meta(src_project.id)
    src_project_meta = sly.ProjectMeta.from_json(src_project_meta_json)

    # create new project
    dst_project = api.project.create(
        workspace_id,
        name=f"{src_project.name}-sematic-segmentation",
        description=f"Converted {src_project.name} project labels to semantic segmentation tasks.",
        change_name_if_conflict=True,
    )

    dst_project_meta, dst_mapping = src_project_meta.to_segmentation_task(
        [sly.Bitmap, sly.Polygon, sly.AnyGeometry]
    )

    if need_add_bg and dst_project_meta.obj_classes.get(_bg_class_name) is None:
        dst_project_meta = dst_project_meta.add_obj_class(_bg_obj_class)
        dst_mapping[_bg_obj_class] = _bg_obj_class

    api.project.update_meta(dst_project.id, dst_project_meta.to_json())
    api.project.update_custom_data(dst_project.id, {"src_project": src_project.id})

    src_project_datasets = api.dataset.get_list(src_project.id)
    for dataset in src_project_datasets:
        sly.logger.info(f"Dataset {dataset.name} has {dataset.items_count} images")
        images = api.image.get_list(dataset.id)

        # create new dataset
        dst_dataset = api.dataset.create(dst_project.id, name=dataset.name)
        sly.logger.info(f"Dataset has been sucessfully created, id={dst_dataset.id}")

        ds_progress = tqdm(total=len(images), desc=f"Processing dataset: {dataset.name}")
        for batch in sly.batched(images):
            new_anns = []
            img_names, image_ids, img_metas = zip(*((x.name, x.id, x.meta) for x in batch))
            annotations = api.annotation.download_json_batch(dataset.id, image_ids)

            new_img_infos = api.image.upload_ids(
                dst_dataset.id, img_names, image_ids, metas=img_metas
            )
            new_img_ids = [x.id for x in new_img_infos]

            for ann_json in annotations:
                anno = sly.Annotation.from_json(ann_json, src_project_meta)

                if need_add_bg:
                    anno = anno.add_bg_object(_bg_obj_class)

                if need_rasterize:
                    anno = anno.to_nonoverlapping_masks(dst_mapping)
                else:
                    new_labels = []
                    for label in anno.labels:
                        if label.geometry.geometry_name() in ["bitmap", "polygon"]:
                            new_labels.extend(label.convert(dst_mapping[label.obj_class]))
                    anno = anno.clone(labels=new_labels)
                new_anno = anno.to_segmentation_task()

                new_anns.append(new_anno)

            api.annotation.upload_anns(new_img_ids, new_anns)
            ds_progress.update(len(batch))

        sly.logger.info(f"Dataset {dataset.name} has been sucessfully processed")


if __name__ == "__main__":
    sly.main_wrapper("main", main)
