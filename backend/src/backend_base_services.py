from fastapi import HTTPException
from backend.src.database.db_utils import upload_video_database, update_video_parquet_table, upload_product_database, update_product_parquet_table
from backend.src.detection_classification.detect_classify import classify_video_genre

def upload_video_service(
    genre_clf_model, vid_id, video, request_payload
):
    status = "process"

    video_metadata = {
        "video_id": vid_id,
        "video_path": None,
        "caption": request_payload.caption,
        "genre": []
    }

    try:
        video_path = upload_video_database(vid_id, video)
        video_metadata["video_path"] = video_path
        status = "uploaded"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed_upload: {e}")
    
    try:
        classify_payload = classify_video_genre(genre_clf_model, video_path)
        video_metadata["genre"] = classify_payload
        update_video_parquet_table(video_metadata)
        status = "completed"
    except Exception as e:
        status = "uploaded_successful_but_failed_detect_classify"

    return {**video_metadata, "status": status}

def upload_product_service(
    product_id, image, request_payload
):
    status = "process"

    product_metadata = {
        "product_id": product_id,
        "product_path": None,
        "title": request_payload.title,
        "product_details": request_payload.description,
        "category": request_payload.category.value
    }

    try:
        product_path = upload_product_database(product_id, image)
        product_metadata["product_path"] = product_path
        update_product_parquet_table(product_metadata)
        status = "completed"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed_upload: {e}")

    return {**product_metadata, "status": status}



