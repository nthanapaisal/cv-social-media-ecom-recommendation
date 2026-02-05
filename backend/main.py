import os
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from enum import Enum
from pydantic import BaseModel
from transformers import pipeline
from ultralytics import YOLO
from PIL import Image
import uuid

from backend.src.backend_base_services import upload_video_service, upload_product_service

app = FastAPI()

class VideoUploadRequest(BaseModel):
    caption: str

    @classmethod
    def as_form(
        cls,
        caption: str = Form(...)
    ):
        return cls(caption=caption)

class ProductCategory(str, Enum):
    fashion = "fashion"
    beauty = "beauty"
    electronics = "electronics"
    home = "home"
    fitness = "fitness"
    food = "food"
    baby = "baby"
    automotive = "automotive"
    pets = "pets"
    gaming = "gaming"
    
class ProductUploadRequest(BaseModel):
    title: str
    description: str
    category: ProductCategory

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        description: str = Form(...),
        category: ProductCategory = Form(...)
    ):
        return cls(title=title, description=description, category=category)

@app.on_event("startup")
def startup():
    app.state.genre_classifier = pipeline(
        task="video-classification",
        model="MCG-NJU/videomae-small-finetuned-kinetics",
        device=-1  # CPU (Docker on Mac)
    )
    print("main.py: Loaded models")

def get_genre_classifier():
    return app.state.genre_classifier

@app.post("/videos/upload")
async def upload_video(
    video: UploadFile = File(...),
    request_payload: VideoUploadRequest = Depends(VideoUploadRequest.as_form),
    genre_clf_model= Depends(get_genre_classifier)
):  
    vid_id = str(uuid.uuid4())
    print(f"main.py: /videos/upload id: {vid_id}")

    if not video.filename.lower().endswith((".mp4", ".mov", ".mkv", ".webm", ".avi")):
        raise HTTPException(status_code=400, detail="Unsupported video format")
    try:
        upload_payload = upload_video_service(
            genre_clf_model, 
            vid_id, 
            video, 
            request_payload
        )
        print(f"main.py: uploaded video to database, applied classification and object detection: {vid_id}")
        return upload_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/products/upload")
async def upload_product(
    image: UploadFile = File(...),
    request_payload: ProductUploadRequest = Depends(ProductUploadRequest.as_form)
):
    prod_id = str(uuid.uuid4())
    print(f"main.py: /products/upload id: {prod_id}")
    try:
        img_bytes = await image.read()
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        upload_payload = upload_product_service(prod_id, img, request_payload)
        print(f"main.py: uploaded product to database, applied classification and object detection: {prod_id}")
        return upload_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_video_by_id(video_id: str):
    pass

def get_video_genre_by_id(video_id: str):
    pass

def get_videos_by_genre(genre: str):
    pass


def get_product_by_id(product_id: str):
    pass

def get_product_category_by_id(product_id: str):
    pass

def get_products_by_category(category: str):
    pass

