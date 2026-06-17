"""Thin wrapper around MediaPipe Face Landmarker with blendshapes enabled.

Isolates all MediaPipe API details so the rest of the detector deals only in
plain {blendshape_name: score} dicts. Used by both the webcam loop and the
static-image test path.
"""

from __future__ import annotations

import os

# Quiet MediaPipe/absl C++ logging (INFO/WARNING + analytics noise). Must be set
# before mediapipe imports its native libs.
os.environ.setdefault("GLOG_minloglevel", "2")
os.environ.setdefault("GLOG_logtostderr", "0")

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

import derived
from config import MODEL_PATH


class BlendshapeReader:
    """Runs Face Landmarker and returns the latest blendshape scores."""

    def __init__(self, running_mode: vision.RunningMode = vision.RunningMode.VIDEO):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Face Landmarker model not found at {MODEL_PATH}. "
                "Download it (see README.md)."
            )
        options = vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(MODEL_PATH)),
            running_mode=running_mode,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True,  # for head pitch/yaw
            num_faces=1,
        )
        self._landmarker = vision.FaceLandmarker.create_from_options(options)
        self._mode = running_mode
        # Normalized (x, y) of the most recent detection's landmarks (or []).
        self.last_landmarks: list[tuple[float, float]] = []
        # 4x4 facial transformation matrix of the most recent detection (or None).
        self.last_matrix = None

    @staticmethod
    def _to_mp_image(frame_rgb):
        return mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

    def _scores(self, result) -> dict[str, float]:
        # Stash landmarks for the overlay broadcast (independent of blendshapes).
        if result.face_landmarks:
            self.last_landmarks = [(lm.x, lm.y) for lm in result.face_landmarks[0]]
        else:
            self.last_landmarks = []
        if result.facial_transformation_matrixes:
            self.last_matrix = result.facial_transformation_matrixes[0]
        else:
            self.last_matrix = None
        if not result.face_blendshapes:
            return {}
        scores = {c.category_name: c.score for c in result.face_blendshapes[0]}
        return derived.augment(scores, self.last_landmarks, self.last_matrix)

    def from_image(self, frame_rgb) -> dict[str, float]:
        """IMAGE mode: classify a single still RGB frame."""
        result = self._landmarker.detect(self._to_mp_image(frame_rgb))
        return self._scores(result)

    def from_video_frame(self, frame_rgb, timestamp_ms: int) -> dict[str, float]:
        """VIDEO mode: classify a webcam frame with a monotonic timestamp."""
        result = self._landmarker.detect_for_video(
            self._to_mp_image(frame_rgb), timestamp_ms
        )
        return self._scores(result)

    def close(self):
        self._landmarker.close()
