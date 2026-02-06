import os
from fastapi.encoders import jsonable_encoder
import numpy as np
import shutil
import pandas as pd

VIDEO_DIR = "data/videos"
PRODUCT_DIR = "data/products"
VIDEO_PARQUET_DIR = "data/video_parquet"
PRODUCT_PARQUET_DIR = "data/product_parquet"

########################################## Upload ########################################## 
def upload_video_database(vid_id, video):
    os.makedirs(VIDEO_DIR, exist_ok=True)

    ext = os.path.splitext(video.filename)[1].lower() or ".mp4"
    video_path = os.path.join(VIDEO_DIR, f"{vid_id}{ext}")

    with open(video_path, "wb") as f:
        shutil.copyfileobj(video.file, f)  

    return video_path

def normalize_video_row(payload: dict):
    vid_id = payload.get("video_id")
    vid_path = payload.get("video_path")

    if not vid_id:
        raise ValueError("video_id is required (vid_id cannot be null)")
    if not vid_path:
        raise ValueError("video_path is required (vid_path cannot be null)")

    genre_preds = payload.get("genre") or []
    labels = []
    if isinstance(genre_preds, list):
        for p in genre_preds:
            if isinstance(p, dict) and p.get("label") is not None:
                labels.append(str(p["label"]))

    return {
        "video_id": payload.get("video_id"),
        "video_path": payload.get("video_path"),
        "caption": payload.get("caption"),
        "genres": labels if labels else None
    }

def update_video_parquet_table(video_metadata_json):
    os.makedirs(VIDEO_PARQUET_DIR, exist_ok=True)

    row = normalize_video_row(video_metadata_json)
    df = pd.DataFrame([row])
    out_path = os.path.join(VIDEO_PARQUET_DIR, f"part-{row['video_id']}.parquet")
    df.to_parquet(out_path, engine="pyarrow", index=False)
    
    return out_path

def upload_product_database(product_id, image):
    os.makedirs(PRODUCT_DIR, exist_ok=True)

    product_path = os.path.join(PRODUCT_DIR, f"{product_id}.jpg")

    if image.mode != "RGB":
        image = image.convert("RGB")

    image.save(product_path, format="JPEG", quality=95, optimize=True)
    return product_path 

def update_product_parquet_table(product_metadata_json):
    os.makedirs(PRODUCT_PARQUET_DIR, exist_ok=True)

    df = pd.DataFrame([product_metadata_json])
    out_path = os.path.join(PRODUCT_PARQUET_DIR, f"part-{product_metadata_json['product_id']}.parquet")
    df.to_parquet(out_path, engine="pyarrow", index=False)
    
    return out_path

########################################## Download ########################################## 
def download_video(video_id: str):
    for fname in os.listdir(VIDEO_DIR):
        if fname.startswith(video_id):
            return os.path.join(VIDEO_DIR, fname)
    raise FileNotFoundError(f"Video {video_id} not found")

def download_video_metadata(video_id: str):
    df = pd.read_parquet(VIDEO_PARQUET_DIR)
    row = df[df["video_id"] == video_id]
    if row.empty:
        raise FileNotFoundError(f"Product metadata {video_id} not found")
    result = row.iloc[0].to_dict()
    for k, v in result.items():
        if isinstance(v, np.ndarray):
            result[k] = v.tolist()

    return jsonable_encoder(result)

def download_videos_genre(genre: str): # need to test
    df = pd.read_parquet(VIDEO_PARQUET_DIR)
    return df[df["genres"].apply(lambda g: genre in g if isinstance(g, list) else False)].to_dict("records")

def download_product(product_id: str):
    path = os.path.join(PRODUCT_DIR, f"{product_id}.jpg")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Product image {product_id} not found")
    return path

def download_product_metadata(product_id: str):
    df = pd.read_parquet(PRODUCT_PARQUET_DIR)
    row = df[df["product_id"] == product_id]
    if row.empty:
        raise FileNotFoundError(f"Product metadata {product_id} not found")
    return row.iloc[0].to_dict()

def download_products_genre(category: str): # need to test
    df = pd.read_parquet(PRODUCT_PARQUET_DIR)
    return df[df["category"] == category].to_dict("records")
