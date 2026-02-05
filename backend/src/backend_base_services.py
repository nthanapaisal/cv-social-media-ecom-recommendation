from backend.src.database.db_utils import upload_video_database#, upload_product_database
from backend.src.detection_classification.detect_classify import classify_video_genre, object_detect_video

def upload_video_service(
    genre_clf, vid_id, video, request_payload
):
    classify_payload = {}
    detect_payload = {}
    status = "process"
    video_path = None

    try:
        video_path = upload_video_database(video_id, video)
        status = "uploaded"
    except Exception as e:
        status = "failed_upload"
        return {
            "video_id": vid_id,
            "video_path": None,
            "caption": request_payload.caption,
            "status": status,
            "genre": classify_payload,
            "objects": detect_payload
        }
    
    try:
        classify_payload = classify_video_genre(genre_clf, video_path)
        # detect_payload = object_detect_video(video_path,)
        status = "completed"
    except Exception as e:
        status = "failed_detect_classify"

    return_payload = {
        "video_id": vid_id,
        "video_path": video_path,
        "caption": request_payload.caption,
        "status": status,
        "genre": classify_payload,
        "objects": detect_payload
    }

    # update video table

    return return_payload

# def upload_product_service(vid_id, video, request_payload):

#     # upload video to database
#     product_path = upload_product_database(prod_id, image, request_payload)

#     # detect objects

#     # update product table
    
#     return return_payload

def re_classify_detections_service():
    pass 

def product_recommendation_service():
    pass

def video_recommendation_service():
    pass

def user_interaction_service()
    pass
