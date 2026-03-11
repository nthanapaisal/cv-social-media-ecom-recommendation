import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum
from pydantic import BaseModel
from transformers import pipeline
from PIL import Image
import uuid
import easyocr

from backend.src.backend_base_services import upload_video_service, upload_product_service, \
    get_vid_by_id_service, get_vid_metadata_by_id_service, get_vids_by_genre_service, \
    get_product_by_id_service, get_product_metadata_by_id_service, get_products_by_category_service, \
    update_user_interaction_service, get_feed_service, get_shop_service
from backend.src.product_recommendation.personalized_recommendation import _products_recommendation_cache


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoUploadRequest(BaseModel):
    description: str

    @classmethod
    def as_form(
        cls,
        description: str = Form(...)
    ):
        return cls(description=description)

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
    price: float

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        description: str = Form(...),
        category: ProductCategory = Form(...),
        price: float = Form(...)
    ):
        return cls(title=title, description=description, category=category, price=price)

@app.on_event("startup")
def startup():
    app.state.genre_classifier = pipeline(
        task="video-classification",
        model="MCG-NJU/videomae-small-finetuned-kinetics",
        device=-1  # CPU (Docker on Mac)
    )
    app.state.ocr_reader = easyocr.Reader(["en"], gpu=False)
    
    app.state.zero_shot_ocr_classification = pipeline(
        task="zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=-1,  # CPU
    )

    app.state.caption_model = pipeline(
        task="image-text-to-text",
        model="Salesforce/blip-image-captioning-base",
        device=-1  # CPU
    ) 

    print("main.py: Loaded models")

@app.get("/health")
def health_check():
    return {"status": "ok"}

def get_genre_classifier():
    return app.state.genre_classifier

def get_ocr_reader():
    return app.state.ocr_reader

def get_bart_mnli():
    return app.state.zero_shot_ocr_classification

def get_caption_model():
    return app.state.caption_model

@app.post("/upload/video")
async def upload_video(
    video: UploadFile = File(...),
    request_payload: VideoUploadRequest = Depends(VideoUploadRequest.as_form),
    genre_clf_model= Depends(get_genre_classifier),
    ocr_reader = Depends(get_ocr_reader),
    bart_mnli = Depends(get_bart_mnli),
    caption_model = Depends(get_caption_model)
):  
    vid_id = str(uuid.uuid4())
    print(f"main.py: /upload/video id: {vid_id}")

    if not video.filename.lower().endswith((".mp4", ".mov", ".mkv", ".webm", ".avi")):
        raise HTTPException(status_code=400, detail="Unsupported video format")
    try:
        upload_payload = upload_video_service(
            genre_clf_model, 
            ocr_reader,
            bart_mnli,
            caption_model,
            vid_id, 
            video, 
            request_payload
        )
        print(f"main.py: /upload/video/ uploaded video to database, applied classification and object detection: {vid_id}")
        return upload_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/product")
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

@app.post("/video/interactions")
async def update_video_interactions(
    video_id: str,
    watch_time_ms: int
):
    try:
        return_payload = update_user_interaction_service(video_id, watch_time_ms)
        return return_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"update_video_interactions failed: {str(e)}")

# return 10 video paths randomly selected from DB.

@app.get("/feed/videos")
def get_feed_videos(vids_num: int = 10):
    """
    No cache, everytime you call this API it will recommend new videos.
    """
    try:
        return_payload = get_feed_service(vids_num)
        return return_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_feed_videos failed: {str(e)}")

# Recommendation portion; return top 20 products (its metadata) after calling recommendation system and product selections
@app.get("/shop/products")
def get_shop_products(num_products: int = 20):
    """
    Cached. if you call this API multiple times with same num_products for 5 minutes it will return the same products. 

    If you want different products recommended:
    a) call the refresh_shop API below.
    b) call this API with a different num_products.
    c) wait 5 minutes (Configurable inside get_shop_service function).
    """
    try:
        return_payload = get_shop_service(num_products)
        return return_payload
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"get_shop_products failed: {str(e)}")


# for refresh button that clears the products cache
# in frontend when refresh button is pressed we can call this API then call the get_shop_products API above 
@app.post("/shop/refresh")
def refresh_shop():
    try:
        _products_recommendation_cache["data"] = None
        _products_recommendation_cache["timestamp"] = 0
        return {"status": "completed"}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"refresh shop failed {str(e)}")
