import boto3
import psycopg2
from typing import List
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import gzip
import io
from threading import Thread


S3_BUCKET_NAME = "test-videos-123"

class VideoModel(BaseModel):
    id: int
    video_name: str
    video_url: str
    is_deleted: bool


app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def upload_and_add_video(file: UploadFile, video_name: str):
    print("Upload and add video endpoint hit!!")
    print(file.filename)
    print(file.content_type)

    # Compress file using gzip
    compressed_file = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed_file, mode='w') as gz:
        gz.write(file.file.read())

    # Upload compressed file to AWS S3
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(S3_BUCKET_NAME)
    bucket.upload_fileobj(compressed_file, f"{video_name}.gz", ExtraArgs={"ACL": "public-read"})

    uploaded_file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{video_name}.gz"

    # Store URL in database
    conn = psycopg2.connect(
        database="accounting", user="postgres", password="546546", host="0.0.0.0"
    )
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO video (video_name, video_url) VALUES ('{video_name}', '{uploaded_file_url}' )"
    )
    conn.commit()
    cur.close()
    conn.close()

@app.get("/status")
async def check_status():
    return "Hello World!"


@app.post("/videos", status_code=201)
async def add_video(file: UploadFile):
    video_name = file.filename.split('.')[0]
    Thread(target=upload_and_add_video, args=(file, video_name)).start()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)