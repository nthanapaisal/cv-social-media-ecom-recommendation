import os
import pandas as pd
import shutil
import numpy as np
from fastapi.encoders import jsonable_encoder

VIDEO_DIR = "data/videos"
PRODUCT_DIR = "data/products"
VIDEO_PARQUET_DIR = "data/video_parquet"
PRODUCT_PARQUET_DIR = "data/product_parquet"
USER_INTERACTION_PARQUET_DIR = "data/user_interaction_parquet"

########################################## Upload and Update ########################################## 
def upload_video_database(vid_id, video):
    os.makedirs(VIDEO_DIR, exist_ok=True)

    ext = os.path.splitext(video.filename)[1].lower() or ".mp4"
    video_path = os.path.join(VIDEO_DIR, f"{vid_id}{ext}")

    with open(video_path, "wb") as f:
        shutil.copyfileobj(video.file, f)  

    return video_path

def upload_product_database(product_id, image):
    os.makedirs(PRODUCT_DIR, exist_ok=True)

    product_path = os.path.join(PRODUCT_DIR, f"{product_id}.jpg")

    if image.mode != "RGB":
        image = image.convert("RGB")

    image.save(product_path, format="JPEG", quality=95, optimize=True)
    return product_path 


def update_parquet_table(data_dict: dict, item_type: str)->str:
    """
    Inserts a parquet file into its corresponding directory
    
    :param data_dict: actual data you want to store.
    :param item_type: database type to be updated.
    """
    id_key_map = {
        "video": "video_id",
        "product": "product_id",
        "user": "video_id"
    }

    path_map = {
        "video": VIDEO_PARQUET_DIR,
        "product": PRODUCT_PARQUET_DIR,
        "user": USER_INTERACTION_PARQUET_DIR
    }

    id_key = id_key_map[item_type]
    path = path_map[item_type]
    
    os.makedirs(path, exist_ok=True)
    df = pd.DataFrame([data_dict])
    out_path = os.path.join(path, f"part-{data_dict[id_key]}.parquet")
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

def download_product(product_id: str):
    path = os.path.join(PRODUCT_DIR, f"{product_id}.jpg")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Product image {product_id} not found")
    return path

def download_product_metadata(product_id: str):
    df = pd.read_parquet(PRODUCT_PARQUET_DIR)
    row = df[df["product_id"] == product_id]
    print(row)
    if row.empty:
        raise FileNotFoundError(f"Product metadata {product_id} not found")
    return row.iloc[0].to_dict()

def download_all_videos_metadata():
    df = pd.read_parquet(VIDEO_PARQUET_DIR)
    if df.empty:
        raise FileNotFoundError(f"Video metadata not found")
    return df

def download_user_interactions()-> pd.DataFrame:
    df = pd.read_parquet(USER_INTERACTION_PARQUET_DIR)
    if df.empty:
        return pd.DataFrame("")
    return df

def download_all_products_metadata()->pd.DataFrame:
    df = pd.read_parquet(PRODUCT_PARQUET_DIR)
    if df.empty:
        raise FileNotFoundError(f"Product metadata not found")
    return df






