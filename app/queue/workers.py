# rq worker --with-scheduler --url redis://valkey:6379
# for starting the worker
from ..db.collections.files import files_collection
from bson import ObjectId


async def process_file(id: str):
    await files_collection.update_one({"_id", ObjectId(id)}, {
        "$set": {
            "status": "processing"
        }
    })
