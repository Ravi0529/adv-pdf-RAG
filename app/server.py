from fastapi import FastAPI, UploadFile
from .utils.file import save_to_disk
from .db.collections.files import files_collection, FileSchema
from .queue.q import q
from .queue.workers import process_file

app = FastAPI()


@app.get("/")
def hello():
    return {"Status": "healthy"}


@app.post("/upload")
async def upload_file(file: UploadFile):
    db_file = await files_collection.insert_one(
        document=FileSchema(
            name=file.filename,
            status="saving"
        )
    )
    file_path = f"/mnt/uploads/{str(db_file.inserted_id)}/{file.filename}"
    # mounting storage in production(HDD, SSD, etc.)
    await save_to_disk(file=await file.read(), path=file_path)

    # Push to Queue
    q.enqueue(process_file, str(db_file.inserted_id), file_path)

    # MongoDB save
    await files_collection.update_one({"_id": db_file.inserted_id}, {
        "$set": {
            "status": "queued"
        }
    })

    return {"file_id": str(db_file.inserted_id)}
