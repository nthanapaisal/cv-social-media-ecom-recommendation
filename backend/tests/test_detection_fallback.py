import unittest
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
from backend.src.backend_base_services import upload_video_service
from backend.src.database.db_utils import download_video_metadata

from backend.src.detection.detect_modules import capping_video, detect_objects_from_frames
from backend.src.detection.detect_utils import get_base_frames


class DetectModulesTests(unittest.TestCase):
    def test_detect_objects_from_frames_returns_empty_when_no_frames(self):
        detector = Mock()

        detected = detect_objects_from_frames([], detector)

        self.assertEqual(detected, [])
        detector.assert_not_called()


class GetBaseFramesTests(unittest.TestCase):
    @patch("backend.src.detection.detect_utils._get_base_frames_with_ffmpeg")
    @patch("backend.src.detection.detect_utils.cv2.cvtColor")
    @patch("backend.src.detection.detect_utils.cv2.VideoCapture")
    def test_get_base_frames_falls_back_to_ffmpeg_when_opencv_decodes_no_frames(
        self,
        video_capture_mock,
        cvt_color_mock,
        ffmpeg_fallback_mock,
    ):
        cap = Mock()
        cap.isOpened.return_value = True
        cap.get.return_value = 4
        cap.read.return_value = (False, None)
        video_capture_mock.return_value = cap

        fallback_frame = np.zeros((4, 4, 3), dtype=np.uint8)
        ffmpeg_fallback_mock.return_value = [fallback_frame]
        cvt_color_mock.side_effect = lambda frame, _: frame

        frames = get_base_frames("data/test_videos/fireship.mp4", num_frames=4)

        self.assertEqual(len(frames), 1)
        self.assertTrue(np.array_equal(frames[0], fallback_frame))
        ffmpeg_fallback_mock.assert_called_once_with(
            "data/test_videos/fireship.mp4",
            4,
        )


class UploadVideoServiceTests(unittest.TestCase):
    @patch("backend.src.backend_base_services.update_parquet_table")
    @patch("backend.src.backend_base_services.get_top3_objects_min_conf")
    @patch("backend.src.backend_base_services.detect_objects_from_frames")
    @patch("backend.src.backend_base_services.capping_video")
    @patch("backend.src.backend_base_services.zero_shot_classification")
    @patch("backend.src.backend_base_services.ocr_read_frames")
    @patch("backend.src.backend_base_services.get_base_frames")
    @patch("backend.src.backend_base_services.classify_video_genre")
    @patch("backend.src.backend_base_services.get_video_duration_ms_from_path")
    @patch("backend.src.backend_base_services.upload_video_database")
    def test_upload_video_service_completes_when_captioning_fails(
        self,
        upload_video_database_mock,
        get_duration_mock,
        classify_video_genre_mock,
        get_base_frames_mock,
        ocr_read_frames_mock,
        zero_shot_classification_mock,
        capping_video_mock,
        detect_objects_mock,
        get_top_objects_mock,
        update_parquet_mock,
    ):
        upload_video_database_mock.return_value = "data/videos/test.mp4"
        get_duration_mock.return_value = 1000
        classify_video_genre_mock.return_value = [{"label": "surfing water", "score": 0.9}]
        get_base_frames_mock.return_value = [np.zeros((2, 2, 3), dtype=np.uint8)]
        ocr_read_frames_mock.return_value = ("console text", 0.8)
        zero_shot_classification_mock.side_effect = [
            ("electronics", 0.7),
            ("gaming", 0.6),
            ("gaming", 0.5),
        ]
        capping_video_mock.side_effect = RuntimeError("caption pipeline broken")
        detect_objects_mock.return_value = [("laptop", 0.8)]
        get_top_objects_mock.return_value = [("laptop", 0.8)]
        update_parquet_mock.return_value = "data/video_parquet/part-test.parquet"

        request_payload = Mock(description="fireship")
        result = upload_video_service(
            genre_clf_model=Mock(),
            ocr_reader=Mock(),
            bart_mnli=Mock(),
            caption_model=Mock(),
            object_detector=Mock(),
            vid_id="video-123",
            video=Mock(),
            request_payload=request_payload,
        )

        self.assertEqual(result["status"], "completed")
        self.assertIn("gaming", result["bucket_name"])
        self.assertIn("electronics", result["bucket_name"])
        update_parquet_mock.assert_called_once()


class DownloadVideoMetadataTests(unittest.TestCase):
    @patch("backend.src.database.db_utils.download_all_videos_metadata")
    def test_download_video_metadata_uses_normalized_aggregate_dataframe(
        self,
        download_all_videos_metadata_mock,
    ):
        download_all_videos_metadata_mock.return_value = pd.DataFrame(
            [
                {
                    "video_id": "video-123",
                    "bucket_name": ["gaming", "outdoor"],
                    "bucket_num": ["10", "11"],
                }
            ]
        )

        result = download_video_metadata("video-123")

        self.assertEqual(result["video_id"], "video-123")
        self.assertEqual(result["bucket_name"], ["gaming", "outdoor"])
        download_all_videos_metadata_mock.assert_called_once()


class CaptioningTests(unittest.TestCase):
    def test_capping_video_passes_empty_prompt_to_caption_pipeline(self):
        caption_model = Mock(return_value=[{"generated_text": "caption"}])
        frame = np.zeros((4, 4, 3), dtype=np.uint8)

        result = capping_video([frame], caption_model)

        self.assertEqual(result, "caption")
        _, kwargs = caption_model.call_args
        self.assertIn("images", kwargs)
        self.assertEqual(kwargs["text"], "")


if __name__ == "__main__":
    unittest.main()
