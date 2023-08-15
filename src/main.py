import os
import numpy as np
import supervisely as sly
from dotenv import load_dotenv
from collections import defaultdict
from tqdm import tqdm

load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))

app = sly.Application()
api = sly.Api.from_env()

# check the workspace exists
workspace_id = sly.env.workspace_id()
workspace = api.workspace.get_info_by_id(workspace_id)
if workspace is None:
    print("you should put correct workspaceId value to local.env")
    raise ValueError(f"Workspace with id={workspace_id} not found")


@sly.handle_exceptions
def main():
    # ERROR TEST CODE!
    team_id = sly.env.team_id()
    print(f"team_id: {team_id}")
    bad_path = "/bad/path/not_exists.tar"
    api.file.get_info_by_path(team_id, bad_path).sizeb
    # ERROR TEST CODE!

    # create new project
    src_project = api.project.get_info_by_id(os.environ["modal.state.slyProjectId"])
    src_project_meta_json = api.project.get_meta(src_project.id)
    src_project_meta = sly.ProjectMeta.from_json(src_project_meta_json)

    dst_project = api.project.create(
        workspace.id,
        name=f"{src_project.name}-sematic-segmentation",
        description=f"Converted {src_project.name} project labels to semantic segmentation tasks.",
        change_name_if_conflict=True,
    )

    # export all classes from initial project to new project with bitmap type
    objects_dict = {}
    for obj_class in src_project_meta.obj_classes:
        if obj_class.geometry_type in (sly.Bitmap, sly.Polygon, sly.AnyGeometry):
            objects_dict[obj_class.name] = sly.ObjClass(
                obj_class.name, sly.Bitmap, color=obj_class.color
            )

    dst_project_meta = src_project_meta.clone(obj_classes=list(objects_dict.values()))
    api.project.update_meta(dst_project.id, dst_project_meta.to_json())
    api.project.update_custom_data(dst_project.id, {"src_project": src_project.id})

    src_project_datasets = api.dataset.get_list(src_project.id)
    for dataset in src_project_datasets:
        print(f"Dataset {dataset.name} has {dataset.items_count} images")
        images = api.image.get_list(dataset.id)

        ds_progress = tqdm(
            total=len(images), desc=f"Processing dataset: {dataset.name}"
        )
        # create new dataset
        dst_dataset = api.dataset.create(dst_project.id, name=dataset.name)
        print(f"Dataset has been sucessfully created, id={dst_dataset.id}")

        for batch in sly.batched(images):
            new_anns = []
            img_names, image_ids, img_metas = zip(
                *((x.name, x.id, x.meta) for x in batch)
            )
            annotations = api.annotation.download_json_batch(dataset.id, image_ids)

            new_img_infos = api.image.upload_ids(
                dst_dataset.id, img_names, image_ids, metas=img_metas
            )
            new_img_ids = [x.id for x in new_img_infos]

            for image, ann_json in zip(batch, annotations):
                anno = sly.Annotation.from_json(ann_json, src_project_meta)

                mask_images = defaultdict(lambda: np.zeros(anno.img_size, bool))
                for index, label in enumerate(anno.labels, start=1):
                    current_class = label.obj_class.name
                    geometry_type = label.geometry.geometry_name()

                    if geometry_type in ("bitmap", "polygon"):
                        label.draw(mask_images[current_class], 1)
                    else:
                        continue

                new_labels = []
                for mask_class, mask_arr in mask_images.items():
                    mask = sly.Bitmap(mask_arr)
                    label = sly.Label(geometry=mask, obj_class=objects_dict[mask_class])
                    new_labels.append(label)

                new_anno = anno.clone(labels=new_labels)
                new_anns.append(new_anno)

            api.annotation.upload_anns(new_img_ids, new_anns)
            ds_progress.update(len(batch))


main()
app.shutdown()
