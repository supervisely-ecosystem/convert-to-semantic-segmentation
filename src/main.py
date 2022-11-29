import os
import PIL
import cv2
import zlib
import base64
import numpy as np
import supervisely as sly
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np


def base64_2_mask(s):
    z = zlib.decompress(base64.b64decode(s))
    n = np.fromstring(z, np.uint8)
    mask = cv2.imdecode(n, cv2.IMREAD_UNCHANGED)[:, :, 3].astype(bool)
    return mask


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

################################    Part 1    ######################################
###################    create empty project and dataset    #########################
################################    ------    ######################################

initial_project = api.project.get_info_by_id(os.environ["modal.state.slyProjectId"])
meta_json = api.project.get_meta(initial_project.id)
initial_project_meta = sly.ProjectMeta.from_json(meta_json)

sem_seg_project = api.project.get_info_by_name(653, name="Sem-seg")
if not sem_seg_project:
    # create empty project and dataset on server
    sem_seg_project = api.project.create(workspace.id, name="Sem-seg")

sem_seg_dataset = api.dataset.create(
    sem_seg_project.id,
    name="lemons SS",
    change_name_if_conflict=True,
)

# export all classes with bitmap type
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
            mask_images = {}
            for anno in ann_json["objects"]:
                current_class = anno["classTitle"]
                geometry_type = anno["geometryType"]

                if mask_images.get(current_class) is None and geometry_type in (
                    "bitmap",
                    "polygon",
                ):
                    mask_images[current_class] = np.zeros((image.height, image.width))

                if geometry_type == "polygon":
                    mask_images[current_class] = cv2.fillPoly(
                        mask_images[current_class],
                        pts=np.array([anno["points"]["exterior"]]),
                        color=1,
                    )
                elif geometry_type == "bitmap":
                    bitmap = base64_2_mask(anno["bitmap"]["data"])
                    x0, y0 = anno["bitmap"]["origin"]
                    x1, y1 = x0 + bitmap.shape[1], y0 + bitmap.shape[0]
                    mask_images[current_class][y0:y1, x0:x1] = bitmap
                else:
                    continue

            image_annos = []
            for mask_class, mask_arr in mask_images.items():
                # supports masks with values (0, 1) or (0, 255) or (False, True)
                mask = sly.Bitmap(mask_arr)
                label = sly.Label(geometry=mask, obj_class=objects_dict[mask_class])
                image_annos.append(label)

            ann = sly.Annotation(
                img_size=[image.height, image.width], labels=image_annos
            )
            new_anns.append(ann)
        api.annotation.upload_anns(new_img_ids, new_anns)
