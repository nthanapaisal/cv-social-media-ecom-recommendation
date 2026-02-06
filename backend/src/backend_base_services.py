from fastapi import HTTPException
import pandas as pd

from backend.src.database.db_utils import upload_video_database, upload_product_database, update_parquet_table, \
    download_video, download_video_metadata, download_product, download_product_metadata, download_random_videos
from backend.src.detection_classification.detect_classify import load_json, classify_video_genre, get_video_duration_ms_from_path


MAPPED_LABELS = load_json("./backend/configs/mapped_labels_buckets.json")
BUCKETS = load_json("./backend/configs/buckets.json")

def upload_video_service(
    genre_clf_model, vid_id, video, request_payload
):
    status = "process"

    video_metadata = {
        "video_id": vid_id,
        "video_path": None,
        "duration_ms": None,
        "caption": request_payload.caption,
        "bucket_num": None,
        "bucket_name": None
    }

    try:
        video_path = upload_video_database(vid_id, video)
        video_metadata["video_path"] = video_path
        video_metadata["duration_ms"] = get_video_duration_ms_from_path(video_path)
        status = "uploaded"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed_upload: {e}")
    
    try:
        # classification
        classify_payload = classify_video_genre(genre_clf_model, video_path)

        # map to ecom bucket
        predicted_label = classify_payload[0]["label"]
        bucket_info = MAPPED_LABELS.get(predicted_label, ("13", "other"))
        video_metadata["bucket_num"] = bucket_info[0]
        video_metadata["bucket_name"] = bucket_info[1]

        # object detection 

        # update parquet table
        out_path = update_parquet_table(video_metadata, "video")

        status = "completed"
    except Exception as e:
        status = "uploaded_successful_but_failed_detect_classify"

    return {**video_metadata, "status": status, "parquet_path": out_path}

def upload_product_service(
    product_id, image, request_payload
):
    status = "process"

    bucket_num = BUCKETS["buckets"].get(request_payload.category.value, "13")

    product_metadata = {
        "product_id": product_id,
        "product_path": None,
        "title": request_payload.title,
        "product_details": request_payload.description,
        "bucket_num": bucket_num,
        "bucket_name": request_payload.category.value
    }

    try:
        product_path = upload_product_database(product_id, image)
        product_metadata["product_path"] = product_path
        out_path = update_parquet_table(product_metadata, "product")
        status = "completed"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed_upload: {e}")

    return {**product_metadata, "status": status, "parquet_path": out_path}

def get_vid_by_id_service(video_id):
    return download_video(video_id)

def get_vid_metadata_by_id_service(video_id):
    return download_video_metadata(video_id)

def get_vids_by_genre_service(genre):
    return download_videos_genre(genre)

def get_product_by_id_service(product_id):
    return download_product(product_id)

def get_product_metadata_by_id_service(product_id):
    return download_product_metadata(product_id)

def get_products_by_category_service(category):
    return download_products_genre(category)

def update_user_interaction_service(video_id, watch_time_ms):
    user_interaction = {
        "video_id": video_id,
        "watch_time_ms": watch_time_ms
    }
    out_path = update_parquet_table(user_interaction , "user")
    return {**user_interaction, "parquet_path": out_path}

def get_feed_service(n):
    df = download_random_videos()

    if len(df) == 0:
        return []

    # If fewer than n rows exist, return all
    if len(df) <= n:
        return df.to_dict(orient="records")

    sampled = df.sample(n=n, random_state=None)
    return {"videos": sampled.to_dict(orient="records")}
