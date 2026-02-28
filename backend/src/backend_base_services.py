import os
from fastapi import HTTPException
from backend.src.database.db_utils import upload_video_database, upload_product_database, update_parquet_table, \
    download_video, download_video_metadata, download_product, download_product_metadata, download_all_videos_metadata, download_user_interactions
from backend.src.detection.detect_modules import classify_video_genre, ocr_read_frames, zero_shot_classification, capping_video
from backend.src.detection.detect_utils import load_json, get_video_duration_ms_from_path, get_base_frames, weighted_fusion
import logging
logger = logging.getLogger(__name__)
from backend.src.product_recommendation.personalized_recommendation import video_recommendation, product_recommendation

MAPPED_LABELS = load_json("./backend/configs/mapped_labels_buckets.json")
BUCKETS = load_json("./backend/configs/buckets.json")


def upload_video_service(
    genre_clf_model, ocr_reader, bart_mnli, caption_model, vid_id, video, request_payload
):
    status = "process"
    out_path = None

    video_metadata = {
        "video_id": vid_id,
        "video_path": None,
        "duration_ms": None,
        "description": request_payload.description,
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
        all_signal_outputs_list = []

        # SIGNAL 1: classification
        top_k = 3
        classify_payload = classify_video_genre(genre_clf_model, video_path, top_k)

        # SIGNAL 1: map classification signal to ecom bucket
        for prediction in classify_payload:  
            bucket_info = MAPPED_LABELS.get(prediction["label"], ["13", "other"])
            all_signal_outputs_list.append(("classification", bucket_info[1], float(prediction.get("score", 0.0))))

        # Get base frames to extract extra signals from vid
        # Per frame: (element has H x W x RGB(3))  
        base_frames = get_base_frames(video_path)

        # SIGNAL 2: OCR
        ocr_text, ocr_quality = ocr_read_frames(base_frames, ocr_reader)
        
        # SIGNAL 2: zero shot classfication OCR signal to ecom bucket
        ocr_signal_bucket, zeroshot_conf = zero_shot_classification(bart_mnli, list(BUCKETS["buckets"].keys()), ocr_text)
        ocr_conf = ocr_quality * zeroshot_conf
        all_signal_outputs_list.append(("ocr", ocr_signal_bucket, ocr_conf * 1.5))

        # SIGNAL 3: Video description and scaled conf since description conf could be wrong 
        description_signal_bucket, description_zeroshot_conf = zero_shot_classification(bart_mnli, list(BUCKETS["buckets"].keys()), video_metadata["caption"])
        all_signal_outputs_list.append(("description", description_signal_bucket, description_zeroshot_conf * 0.5))

        # SIGNAL 4: Capptioning video
        vid_caption = capping_video(base_frames, caption_model)
   
        # SIGNAL 4: Zeroshot on vid capping
        vid_caption_bucket, vid_caption_conf = zero_shot_classification(bart_mnli, list(BUCKETS["buckets"].keys()), vid_caption)
        all_signal_outputs_list.append(("vid_caption", vid_caption_bucket, vid_caption_conf * 0.7))

        # Combine all signals outputs and weights fusion to pick best bucket
        print(f"all_signal_outputs_list: {all_signal_outputs_list}")
        final_bucket = weighted_fusion(all_signal_outputs_list)
        print(f"Final Bucket Selection: {final_bucket}")

        video_metadata["bucket_num"] = BUCKETS["buckets"][final_bucket] 
        video_metadata["bucket_name"] = final_bucket

        # update parquet table
        out_path = update_parquet_table(video_metadata, "video")

        status = "completed"
    except Exception as e:
        print(f"Error during video analysis: {e}")
        status = "uploaded_successful_but_failed_detect_classify"
        out_path = None

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
        "bucket_name": request_payload.category.value,
        "price": request_payload.price,
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

def update_user_interaction_service(video_id: int, watch_time_ms:int):
    user_interaction = {
        "video_id": video_id,
        "watch_time_ms": watch_time_ms,
    }
    out_path = update_parquet_table(user_interaction , "user")
    return {**user_interaction, "parquet_path": out_path}

def get_feed_service(n_recommended = 10):
    """ Wrapper to get recommended video metadata dataframe and return as serialized list of dict"""
    recommended_videos = video_recommendation(n_recommended)
    return {"videos": recommended_videos}

def get_shop_service(n_recommended = 10):
    """ Wrapper to get recommended video metadata dataframe and return as serialized list of dict"""
    recommended_products = product_recommendation(n_recommended)
    return {"products": recommended_products}
