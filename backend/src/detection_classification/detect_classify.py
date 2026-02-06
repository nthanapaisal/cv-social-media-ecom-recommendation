import json
import av
from fastapi import UploadFile

def load_json(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_video_duration_ms_from_path(video_path: str) -> int:
    with av.open(video_path) as container:
        if container.duration is None:
            raise ValueError("Could not determine video duration")
        return int((container.duration / av.time_base) * 1000)

def classify_video_genre(genre_clf, video_path):
    if not video_path:
        raise ValueError("video_path is required")
    preds = genre_clf(video_path, top_k=5)
    return preds
