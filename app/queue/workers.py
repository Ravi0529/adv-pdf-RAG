# rq worker --with-scheduler --url redis://valkey:6379
# for starting the worker
from ..db.collections.files import files_collection
from bson import ObjectId
from pdf2image import convert_from_path
import os


async def process_file(id: str, file_path: str):
    await files_collection.update_one({"_id", ObjectId(id)}, {
        "$set": {
            "status": "processing"
        }
    })

    # Step-1: Convert PDF to image
    pages = convert_from_path(file_path)

    for i, page in enumerate(pages):
        image_save_path = f"/mnt/uploads/images/{id}/image-{i}.jpg"
        os.makedirs(os.path.dirname(image_save_path), exist_ok=True)
        page.save(image_save_path, 'JPEG')

    await files_collection.update_one({"_id": ObjectId(id)}, {
        "status": "Image conversion succeeded."
    })
