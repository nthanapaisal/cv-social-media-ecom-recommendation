import os
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from pydantic import BaseModel
from transformers import pipeline
from PIL import Image
import uuid

from backend.src.backend_base_services import upload_video_service#, upload_product_service

app = FastAPI()

class UploadRequest(BaseModel):
    caption: str

    @classmethod
    def as_form(
        cls,
        caption: str = Form(...)
    ):
        return cls(caption=caption)

@app.on_event("startup")
def startup():
    app.state.genre_classifier = pipeline(
        task="video-classification",
        model="MCG-NJU/videomae-small-finetuned-kinetics",
        device=-1  # CPU (Docker on Mac)
    )
    print("Genre classification model loaded")

def get_genre_classifier():
    return app.state.genre_classifier

@app.post("/videos/upload")
async def upload_video(
    video: UploadFile = File(...),
    request_payload: UploadRequest = Depends(UploadRequest.as_form),
    genre_clf = Depends(get_genre_classifier)
):  
    vid_id = str(uuid.uuid4())
    print(f"/videos/upload id: {vid_id}")

    if not video.filename.lower().endswith((".mp4", ".mov", ".mkv", ".webm", ".avi")):
        raise HTTPException(status_code=400, detail="Unsupported video format")
    try:
        upload_payload = upload_video_service(genre_clf, vid_id, video, request_payload)
        return upload_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.post("/products/upload")
# async def upload_product(
#     image: UploadFile = File(...), model: YOLO = Depends(get_damage_detection_model),
#     request_payload: UploadRequest = Depends(UploadRequest.as_form)
# ):
#     prod_id = str(uuid.uuid4())
#     print(f"/products/upload id: {prod_id}")
#     try:
#         img_bytes = await image.read()
#         img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
#         upload_payload = upload_product_service(prod_id, img, request_payload)
#         return upload_payloads
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
