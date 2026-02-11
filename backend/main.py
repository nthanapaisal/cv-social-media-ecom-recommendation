import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from enum import Enum
from pydantic import BaseModel
from transformers import pipeline
from PIL import Image
import uuid

from backend.src.backend_base_services import upload_video_service, upload_product_service, \
    get_vid_by_id_service, get_vid_metadata_by_id_service, get_vids_by_genre_service, \
    get_product_by_id_service, get_product_metadata_by_id_service, get_products_by_category_service, \
    update_user_interaction_service, get_feed_service, product_recommendation_service

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

@app.post("/upload/video/")
async def upload_video(
    video: UploadFile = File(...),
    request_payload: VideoUploadRequest = Depends(VideoUploadRequest.as_form),
    genre_clf_model= Depends(get_genre_classifier)
):  
    vid_id = str(uuid.uuid4())
    print(f"main.py: /upload/video id: {vid_id}")

    if not video.filename.lower().endswith((".mp4", ".mov", ".mkv", ".webm", ".avi")):
        raise HTTPException(status_code=400, detail="Unsupported video format")
    try:
        upload_payload = upload_video_service(
            genre_clf_model, 
            vid_id, 
            video, 
            request_payload
        )
        print(f"main.py: /upload/video/ uploaded video to database, applied classification and object detection: {vid_id}")
        return upload_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/product/")
async def upload_product(
    image: UploadFile = File(...),
    request_payload: ProductUploadRequest = Depends(ProductUploadRequest.as_form)
):
    prod_id = str(uuid.uuid4())
    print(f"main.py: /upload/product/ id: {prod_id}")
    try:
        img_bytes = await image.read()
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        upload_payload = upload_product_service(prod_id, img, request_payload)
        print(f"main.py: /upload/product/ uploaded product to database, applied classification and object detection: {prod_id}")
        return upload_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/video/{video_id}")
def get_video_by_id(video_id: str):
    try:
        return_payload = get_vid_by_id_service(video_id)
        return return_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_video_by_id failed: {str(e)}")

@app.get("/video/metadata/{video_id}") ##3
def get_video_metadata_by_id(video_id: str):
    try:
        return_payload = get_vid_metadata_by_id_service(video_id)
        return return_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_video_metadata_by_id failed: {str(e)}")

@app.get("/product/{product_id}")
def get_product_by_id(product_id: str):
    try:
        return_payload = get_product_by_id_service(product_id)
        return return_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_product_by_id failed: {str(e)}")

@app.get("/product/metadata/{product_id}")
def get_product_metadata_by_id(product_id: str):
    try:
        return_payload = get_product_metadata_by_id_service(product_id)
        return return_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_product_metadata_by_id failed: {str(e)}")

@app.post("/video/interactions/")
async def update_video_interactions(
    video_id: str,
    watch_time_ms: int
):
    try:
        return_payload = update_user_interaction_service(video_id, watch_time_ms)
        return return_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"update_video_interactions failed: {str(e)}")

# return 10 video paths randomly selected from DB
@app.get("/feed/videos")
def get_feed_videos(vids_num: int = 5):
    try:
        return_payload = get_feed_service(vids_num)
        return return_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_feed_videos failed: {str(e)}")

# Recommendation portion; return top 20 products (its metadata) after calling recommendation system and product selections
@app.get("/shop/products")
def get_shop_products():
    try:
        return_payload = product_recommendation_service()
        return return_payload
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"get_shop_products failed: {str(e)}")


# TODO: add refresh button for shop and videos 