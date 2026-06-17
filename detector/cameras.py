"""Shared camera enumeration used by the detector and the camera picker."""

from __future__ import annotations

import cv2

MAX_INDEX = 8
WARMUP = 8


def find_cameras() -> list[tuple[int, str]]:
    """Return [(opencv_index, 'label')] for indices that deliver a frame."""
    found = []
    for i in range(MAX_INDEX):
        cap = cv2.VideoCapture(i)
        ok, frame = False, None
        if cap.isOpened():
            for _ in range(WARMUP):
                ok, frame = cap.read()
        cap.release()
        if ok and frame is not None:
            h, w = frame.shape[:2]
            found.append((i, f"Camera {i} ({w}x{h})"))
    return found
