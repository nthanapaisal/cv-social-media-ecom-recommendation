import json
import base64, io
from PIL import ImageDraw, ImageFont

def load_json(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

def convert_pil_base64(pil_img):
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=90, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("utf-8")
