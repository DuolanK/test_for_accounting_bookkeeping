import boto3
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List


BUCKET_NAME = "your_bucket"

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload-files")
async def create_upload_files(request: Request, files: List[UploadFile] = File(...)):
    s3 = boto3.client('s3',
                      aws_access_key_id='YCAJEIvsReyJ218Z4X-FRrYRT', #данный ключ удален, здесь для наглядности, в проде его нужно поместить в .env файл
                      aws_secret_access_key='YCPHYmyFlcyFCkjRuXOVSVcf0ii_kVlhxpmdd0fF',
                      region_name='ru-central1',
                      endpoint_url='https://s3.yandexcloud.net')
    for file in files:
        contents = await file.read()
        # save the file to S3
        s3.put_object(Bucket=BUCKET_NAME, Key=file.filename, Body=contents)









