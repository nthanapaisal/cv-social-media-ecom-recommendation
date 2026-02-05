import os
import shutil
from fastapi import UploadFile

VIDEO_DIR = "data/videos"

def upload_video_database(video: UploadFile, vid_id: str) -> str:
    os.makedirs(VIDEO_DIR, exist_ok=True)

    ext = os.path.splitext(video.filename)[1].lower()
    video_path = os.path.join(VIDEO_DIR, f"{vid_id}{ext}")

    with open(video_path, "wb") as f:
        shutil.copyfileobj(video.file, f)  

    return video_path
