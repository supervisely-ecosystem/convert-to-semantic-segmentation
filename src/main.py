import os
import numpy as np
import supervisely as sly
from dotenv import load_dotenv

# init api for communicating with Supervisely Instance
load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))
api = sly.Api.from_env()

# check the workspace exists
workspace_id = int(os.environ["WORKSPACE_ID"])
workspace = api.workspace.get_info_by_id(workspace_id)
if workspace is None:
    print("you should put correct workspaceId value to local.env")
    raise ValueError(f"Workspace with id={workspace_id} not found")

# get or create new project
initial_project = api.project.get_info_by_id(os.environ["modal.state.slyProjectId"])
meta_json = api.project.get_meta(initial_project.id)
initial_project_meta = sly.ProjectMeta.from_json(meta_json)

sem_seg_project = api.project.get_info_by_name(653, name="Sem-seg")
if not sem_seg_project:
    sem_seg_project = api.project.create(workspace.id, name="Sem-seg")

# create new dataset
sem_seg_dataset = api.dataset.create(
    sem_seg_project.id,
    name="lemons",
    change_name_if_conflict=True,
)

# export all classes from initial project to new project with bitmap type
objects_dict = {
    k: sly.ObjClass(k, sly.Bitmap) for k in initial_project_meta.obj_classes.keys()
}
sem_seg_project_meta = sly.ProjectMeta(obj_classes=list(objects_dict.values()))
api.project.update_meta(sem_seg_project.id, sem_seg_project_meta.to_json())
print(f"Dataset has been sucessfully created, id={sem_seg_dataset.id}")


datasets = api.dataset.get_list(initial_project.id)
for dataset in datasets:
    print(f"Dataset {dataset.name} has {dataset.items_count} images")
    images = api.image.get_list(dataset.id)

    new_anns = []
    for batch in sly.batched(images):
        img_names, image_ids, img_metas = zip(*((x.name, x.id, x.meta) for x in batch))
        annotations = api.annotation.download_json_batch(dataset.id, image_ids)

        new_img_infos = api.image.upload_ids(
            sem_seg_dataset.id, img_names, image_ids, metas=img_metas
        )
        new_img_ids = [x.id for x in new_img_infos]

        for new_img_id, image, ann_json in zip(new_img_ids, batch, annotations):
            image_annotations = sly.Annotation.from_json(ann_json, initial_project_meta)

            mask_images = {}
            for index, anno in enumerate(image_annotations.labels, start=1):
                current_class = anno.obj_class.name
                geometry_type = anno.obj_class.geometry_type

                if mask_images.get(current_class) is None and geometry_type in (
                    sly.Bitmap,
                    sly.Polygon,
                ):
                    mask_images[current_class] = np.zeros(
                        image_annotations.img_size, bool
                    )

                if geometry_type is sly.Polygon:
                    anno.convert(sly.ObjClass(current_class, sly.Bitmap))
                    anno.draw(mask_images[current_class], 1)
                elif geometry_type is sly.Bitmap:
                    anno.draw(mask_images[current_class], 1)
                else:
                    continue

            image_annos = []
            for mask_class, mask_arr in mask_images.items():
                mask = sly.Bitmap(mask_arr)
                label = sly.Label(geometry=mask, obj_class=objects_dict[mask_class])
                image_annos.append(label)

            ann = sly.Annotation(
                img_size=[image.height, image.width], labels=image_annos
            )
            new_anns.append(ann)
        api.annotation.upload_anns(new_img_ids, new_anns)
