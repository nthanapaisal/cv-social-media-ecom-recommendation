import json
import subprocess
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

    if fps and frame_count:
        duration_ms = int((frame_count / fps) * 1000)
        if duration_ms > 0:
            return duration_ms

    return _get_video_duration_ms_with_ffprobe(video_path)


def _get_video_duration_ms_with_ffprobe(video_path: str) -> int:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_path,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    duration_seconds = float(result.stdout.strip())
    return int(duration_seconds * 1000)


def _extract_frame_with_ffmpeg(video_path: str, timestamp_seconds: float):
    result = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-ss",
            f"{timestamp_seconds:.3f}",
            "-i",
            video_path,
            "-frames:v",
            "1",
            "-f",
            "image2pipe",
            "-vcodec",
            "mjpeg",
            "-",
        ],
        check=True,
        capture_output=True,
    )

    img_array = np.frombuffer(result.stdout, dtype=np.uint8)
    if img_array.size == 0:
        return None

    frame_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if frame_bgr is None:
        return None

    return cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)


def _get_base_frames_with_ffmpeg(video_path: str, num_frames: int):
    duration_ms = get_video_duration_ms_from_path(video_path)
    if duration_ms <= 0:
        raise ValueError("Video duration could not be determined")

    duration_seconds = duration_ms / 1000
    sample_end = max(duration_seconds - 0.001, 0.0)
    timestamps = np.linspace(0.0, sample_end, num_frames)

    frames = []
    for timestamp in timestamps:
        try:
            frame_rgb = _extract_frame_with_ffmpeg(video_path, float(timestamp))
        except subprocess.CalledProcessError:
            continue

        if frame_rgb is not None:
            frames.append(frame_rgb)

    return frames

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

    if base_frames:
        return base_frames

    return _get_base_frames_with_ffmpeg(video_path, num_frames)

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

def get_top3_objects_min_conf(detected, min_conf=0.0):
    # group by label and pick max conf of each label then pick BEST 3 LABELS
    IGNORE = {
        "person", "face", "hand", "foot",
        "wall", "floor", "ceiling",
    }

    result = {}
    for label, conf in detected:
        if label not in IGNORE and conf >= min_conf:
            result[label] = max(result.get(label, 0.0), conf)

    return sorted(result.items(), key=lambda x: x[1], reverse=True)[:3]
