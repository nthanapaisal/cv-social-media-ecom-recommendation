from PIL import Image
from backend.src.detection.detect_utils import clean_input

def classify_video_genre(genre_clf, video_path, top_k:int = 5):
    if not video_path:
        raise ValueError("video_path is required")
    preds = genre_clf(video_path, top_k=top_k)
    print(f"classification_prediction: {preds}")
    return preds

def ocr_read_frames(base_frames, reader, min_conf=0.4):
    texts = []
    confs = []

    for frame_rgb in base_frames:
        # EasyOCR accepts numpy arrays; RGB is okay
        results = reader.readtext(frame_rgb)

        # result format: (bbox, text, confidence)
        for _, text, conf in results:
            if conf >= min_conf and text.strip():
                texts.append(text.strip())
                confs.append(float(conf))

    # combine
    ocr_text = " ".join(texts)
    ocr_quality = sum(confs) / len(confs) if confs else 0.0

    return ocr_text, ocr_quality

def zero_shot_classification(bart_mnli, buckets, input_txt):

    if not input_txt or not input_txt.strip():
        return ("other", 0.0)

    cleaned_input = clean_input(input_txt)
    print(f"Raw input before zeroshot: {input_txt}, cleaned_input: {cleaned_input}")

    if not cleaned_input:
        return ("other", 0.0)

    result = bart_mnli(input_txt, buckets, multi_label=True, hypothesis_template="This item belongs to the shopping category: {}")
    bucket_key = result["labels"][0]
    confidence = float(result["scores"][0])

    if bucket_key not in buckets:
        return ("other", 0.0)

    return (bucket_key, confidence)


def capping_video(base_frames, caption_model, caption_mode="best"):
    if len(base_frames) == 0:
        return ""

    frame_captions = []
    
    for frame in base_frames:

        # numpy RGB → PIL
        img = Image.fromarray(frame)

        result = caption_model(images=img, text="")

        caption = result[0]["generated_text"].strip()

        frame_captions.append(caption)

    if not frame_captions:
        return ""

    if caption_mode == "concat":
        return " ".join(frame_captions)

    if caption_mode == "best":

        # choose longest caption (usually most descriptive)
        best_caption = max(frame_captions, key=len)

        return best_caption

    raise ValueError("Invalid caption_mode")

def detect_objects_from_frames(frames, object_detector):
    results = object_detector(frames, verbose=False)

    detected = []

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = r.names[cls_id]
            conf = float(box.conf[0])

            detected.append((label, conf))

    # group by label and pick max conf
    result = {}
    for label, conf in detected:
        if label not in result or conf > result[label]:
            result[label] = conf

    return result