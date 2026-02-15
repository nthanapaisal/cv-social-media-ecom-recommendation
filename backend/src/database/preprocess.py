import argparse
from html import parser
import json
from pathlib import Path
from typing import List
from transformers import pipeline

try:
	from backend.src.detection_classification.detect_classify import (classify_video_genre, load_json, get_video_duration_ms_from_path)
	from backend.src.database.db_utils import update_parquet_table
except ModuleNotFoundError:
	import sys
	from pathlib import Path as _Path

	repo_root = _Path(__file__).resolve().parents[3]
	if str(repo_root) not in sys.path:
		sys.path.insert(0, str(repo_root))
	from backend.src.detection_classification.detect_classify import (classify_video_genre, load_json, get_video_duration_ms_from_path)
	from backend.src.database.db_utils import update_parquet_table

try:
	repo_root = Path(__file__).resolve().parents[3]
	mapped_path = str(repo_root / "backend" / "configs" / "mapped_labels_buckets.json")
	MAPPED_LABELS = load_json(mapped_path)
except Exception:
	MAPPED_LABELS = {}

VIDEO_EXTENSIONS = (".mp4", ".mov", ".mkv", ".webm", ".avi")

def list_video_files(folder: str) -> List[str]:
	p = Path(folder)
	if not p.exists():
		raise FileNotFoundError(f"Folder not found: {folder}")
	return [str(f) for f in p.iterdir() if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS]

def classify_videos_in_folder(folder: str, genre_clf_model) -> None:
	files = list_video_files(folder)
	if not files:
		print(f"No video files found in {folder}")
		return

	for video_path in files:
		video_id = Path(video_path).stem
		video_metadata = {
			"video_id": video_id,
			"video_path": video_path,
			"duration_ms": None,
			"caption": None,
			"bucket_num": None,
			"bucket_name": None,
		}

		try:
			try:
				video_metadata["duration_ms"] = get_video_duration_ms_from_path(video_path)
			except Exception:
				video_metadata["duration_ms"] = None

			preds = classify_video_genre(genre_clf_model, video_path)
			print(f"File: {video_path}\nPredictions: {json.dumps(preds, ensure_ascii=False)}\n")

			if preds and isinstance(preds, list) and len(preds) > 0:
				predicted_label = preds[0].get("label")
				bucket_info = MAPPED_LABELS.get(predicted_label, ("13", "other"))
				video_metadata["bucket_num"] = bucket_info[0]
				video_metadata["bucket_name"] = bucket_info[1]
				print(video_id, bucket_info)

			try:
				out_path = update_parquet_table(video_metadata, "video")
				print(f"Updated parquet: {out_path}\n")
			except Exception as e:
				print(f"Failed to update parquet for {video_path}: {e}")
        
		except Exception as e:
			print(f"Failed to classify {video_path}: {e}")

def build_genre_classifier(device: int = -1):
    return pipeline(task="video-classification", model="MCG-NJU/videomae-small-finetuned-kinetics", device=device)

# to run: python ./backend/src/database/preprocess.py /path/to/video/folder
def main():
    parser = argparse.ArgumentParser(description="Classify videos in a folder and print predictions.")
    parser.add_argument("folder", help="Path to folder containing videos")
    parser.add_argument("--device", type=int, default=-1, help="Device for classifier (default -1 CPU)")
    args = parser.parse_args()

    clf = build_genre_classifier(device=args.device)
    classify_videos_in_folder(args.folder, clf)

if __name__ == "__main__":
    main()
