import base64, io
from PIL import ImageDraw, ImageFont
from backend.src.utils import load_json, convert_pil_base64

def classify_video_genre(genre_clf, video_path):
    if not video_path:
        raise ValueError("video_path is required")
    preds = genre_clf(video_path, top_k=5)
    return preds




