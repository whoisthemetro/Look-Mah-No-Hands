"""One-shot camera diagnostic: why does a clearly-visible face read as 'no face'?

Grabs a few frames from the camera, reports the frame format, runs IMAGE-mode
face detection directly on a real frame, and saves it to /tmp so we can inspect
what actually reaches MediaPipe.

    detector/.venv/bin/python detector/diag_cam.py --cam 1
    detector/.venv/bin/python detector/diag_cam.py --cam 1 --rotate 90
"""

from __future__ import annotations

import argparse

import cv2

from landmarker import BlendshapeReader
from mediapipe.tasks.python import vision

_ROTATIONS = {
    90: cv2.ROTATE_90_CLOCKWISE,
    180: cv2.ROTATE_180,
    270: cv2.ROTATE_90_COUNTERCLOCKWISE,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cam", type=int, default=1)
    ap.add_argument("--rotate", type=int, default=0, choices=[0, 90, 180, 270])
    args = ap.parse_args()

    cap = cv2.VideoCapture(args.cam)
    if not cap.isOpened():
        print(f"Could not open camera index {args.cam}.")
        return

    # Warm up — first frames from virtual cameras are often blank.
    bgr = None
    for _ in range(15):
        ok, bgr = cap.read()
    cap.release()

    if bgr is None:
        print("No frame captured.")
        return
    if args.rotate in _ROTATIONS:
        bgr = cv2.rotate(bgr, _ROTATIONS[args.rotate])

    print("=== frame report ===")
    print(f"  shape       : {bgr.shape}  (h, w, channels)")
    print(f"  dtype       : {bgr.dtype}")
    print(f"  pixel range : min={int(bgr.min())} max={int(bgr.max())} mean={bgr.mean():.1f}")
    if bgr.mean() < 5:
        print("  WARNING: frame is essentially black — camera delivered no image.")

    out_path = "/tmp/cam_frame.jpg"
    cv2.imwrite(out_path, bgr)
    print(f"  saved frame : {out_path}")

    # Normalize to 3-channel BGR, then RGB, exactly like the probe does.
    if bgr.ndim == 3 and bgr.shape[2] == 4:
        print("  note: frame had 4 channels (BGRA) — dropping alpha.")
        bgr = cv2.cvtColor(bgr, cv2.COLOR_BGRA2BGR)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    reader = BlendshapeReader(running_mode=vision.RunningMode.IMAGE)
    try:
        scores = reader.from_image(rgb)
    finally:
        reader.close()

    print("=== detection (IMAGE mode on this frame) ===")
    if not scores:
        print("  NO FACE detected in the saved frame.")
        print("  -> Open /tmp/cam_frame.jpg: is your face clearly visible & upright there?")
    else:
        top = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:5]
        print(f"  FACE detected, {len(scores)} blendshapes.")
        print("  top 5:", ", ".join(f"{n}={v:.2f}" for n, v in top))


if __name__ == "__main__":
    main()
