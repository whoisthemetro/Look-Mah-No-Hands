"""Scan camera indices, report which deliver frames, and save a snapshot of each.

Useful when several virtual cameras are registered (OBS, EpocCam, Elgato,
Continuity) and you need to find the one actually showing your iPad feed.

    detector/.venv/bin/python detector/list_cameras.py

Then open the saved snapshots (/tmp/cam_<index>.jpg) — whichever shows YOUR face
is the index to use:
    detector/.venv/bin/python detector/probe_blendshape.py --cam <index>
"""

from __future__ import annotations

import cv2

MAX_INDEX = 8
WARMUP_FRAMES = 12  # virtual cameras often send blank/placeholder frames first


def probe_index(index: int):
    cap = cv2.VideoCapture(index)
    try:
        if not cap.isOpened():
            return None
        frame = None
        for _ in range(WARMUP_FRAMES):
            ok, f = cap.read()
            if ok and f is not None:
                frame = f
        if frame is None:
            print(f"  index {index}: opened but no frame")
            return None
        h, w = frame.shape[:2]
        mean = float(frame.mean())
        path = f"/tmp/cam_{index}.jpg"
        cv2.imwrite(path, frame)
        note = "  (very dark — likely blank/standby)" if mean < 8 else ""
        print(f"  index {index}: {w}x{h}  brightness={mean:.0f}  -> {path}{note}")
        return index
    finally:
        cap.release()


def main():
    print(f"Scanning camera indices 0..{MAX_INDEX - 1} and saving snapshots...\n")
    found = [i for i in range(MAX_INDEX) if probe_index(i) is not None]

    print()
    if not found:
        print("No usable camera found.")
        print("  - Is your iPad/EpocCam/Elgato feed actually live on the Mac?")
        print("  - Check Photo Booth: can it see the feed?")
        return

    print(f"Cameras found at indices: {found}")
    print("Open these snapshots and pick the one showing YOUR face:")
    for i in found:
        print(f"    open /tmp/cam_{i}.jpg")
    print("\nThen run, with that index:")
    print("    detector/.venv/bin/python detector/probe_blendshape.py --cam <index>")


if __name__ == "__main__":
    main()
