import os
import numpy as np
import supervisely as sly
from dotenv import load_dotenv
from collections import defaultdict

# init api for communicating with Supervisely Instance
load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))
api = sly.Api.from_env()

# check the workspace exists
workspace_id = sly.env.workspace_id()
workspace = api.workspace.get_info_by_id(workspace_id)
if workspace is None:
    print("you should put correct workspaceId value to local.env")
    raise ValueError(f"Workspace with id={workspace_id} not found")

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
objects_dict = {
    obj_class.name: sly.ObjClass(obj_class.name, sly.Bitmap)
    for obj_class in src_project_meta.obj_classes
}

datasets = api.dataset.get_list(src_project.id)
for dataset in datasets:
    print(f"Dataset {dataset.name} has {dataset.items_count} images")
    images = api.image.get_list(dataset.id)

    # create new dataset
    dst_dataset = api.dataset.create(dst_project.id, name=dataset.name)
    print(f"Dataset has been sucessfully created, id={dst_dataset.id}")

    new_anns = []
    for batch in sly.batched(images):
        img_names, image_ids, img_metas = zip(*((x.name, x.id, x.meta) for x in batch))
        annotations = api.annotation.download_json_batch(dataset.id, image_ids)

        new_img_infos = api.image.upload_ids(
            dst_dataset.id, img_names, image_ids, metas=img_metas
        )
        new_img_ids = [x.id for x in new_img_infos]

        for image, ann_json in zip(batch, annotations):
            image_annotations = sly.Annotation.from_json(ann_json, src_project_meta)

            mask_images = defaultdict(
                lambda: np.zeros(image_annotations.img_size, bool)
            )
            for index, label in enumerate(image_annotations.labels, start=1):
                current_class = label.obj_class.name
                geometry_type = label.obj_class.geometry_type

                if geometry_type in (
                    sly.Bitmap,
                    sly.Polygon,
                ):
                    label.draw(mask_images[current_class], 1)
                else:
                    continue

            new_labels = []
            for mask_class, mask_arr in mask_images.items():
                mask = sly.Bitmap(mask_arr)
                label = sly.Label(geometry=mask, obj_class=objects_dict[mask_class])
                new_labels.append(label)

            ann = sly.Annotation.clone(image_annotations, labels=new_labels)
            new_anns.append(ann)

        dst_project_meta = src_project_meta.clone(
            obj_classes=list(
                filter(lambda x: x.name in mask_images.keys(), objects_dict.values())
            )
        )
        api.project.update_meta(dst_project.id, dst_project_meta.to_json())
        api.project.update_custom_data(dst_project.id, {"src_project": src_project.id})
        api.annotation.upload_anns(new_img_ids, new_anns)
