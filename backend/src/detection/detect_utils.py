import json
from fastapi import UploadFile
import numpy as np
import cv2
import nltk
from nltk.corpus import words

try:
    words.words()
except LookupError:
    nltk.download("words")
ENGLISH_WORDS = set(words.words())

def load_json(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_video_duration_ms_from_path(video_path: str) -> int:
    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    cap.release()

    duration_ms = int((frame_count / fps) * 1000)

    return duration_ms

# extract n frames for uniform sampling
def get_base_frames(video_path: str, num_frames: int = 10):

    # open vid
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video")

    # count frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        raise ValueError("Video has no frames")

    # compute frame position; create even space spaces num_frames idxs
    idxs = np.linspace(0, total_frames - 1, num_frames).astype(int)

    # read frames
    base_frames = []
    for idx in idxs:

        # jump to frame idx
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)

        # read frame
        ok, frame = cap.read()

        # convert BGR to RGB
        if ok:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            base_frames.append(frame_rgb)

    cap.release()

    return base_frames

def weighted_fusion(all_signal_outputs):
    scores = {}
    
    for signal_name, bucket_name, confidence in all_signal_outputs:
        if signal_name == "classification" and bucket_name in scores:
            continue

        weight = confidence if confidence else 0.1
        scores[bucket_name] = scores.get(bucket_name, 0) + weight

    if not scores:
        return ["other"]

    print(f"Fusion Result: {scores}")

    # Multi labels 
    
    # sort dict into list
    categories_tuple_list = list(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    
    # filter for > 0.1 threshold only
    categories_list = [k for k, v in categories_tuple_list if v >= 0.1]
    
    # if none are > 0.1 just return the highest one
    if not categories_list:
        return [categories_tuple_list[0][0]]
    
    # else return list of multi labels
    return categories_list

def clean_input(text):

    if not text:
        return ""

    clean = []
    seen = set()

    for t in text.split():

        w = t.lower().strip(".,!?")

        if len(w) < 3:
            continue

        if not w.isalpha():   # keep only real words
            continue

        if w not in seen:
            clean.append(w)
            seen.add(w)

    return " ".join(clean)
    
def get_top3_objects_min_conf(obj_dict, min_conf=0.0):
    IGNORE = {
        "person", "face", "hand", "foot",
        "wall", "floor", "ceiling",
    }

    filtered = [
        (label, conf)
        for label, conf in obj_dict.items()
        if conf >= min_conf and label not in IGNORE
    ]

    filtered.sort(key=lambda x: x[1], reverse=True)

    return filtered[:3]