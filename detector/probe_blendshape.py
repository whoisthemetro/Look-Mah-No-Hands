"""Phase 1 probe: confirm the CV pipeline produces blendshape values.

Webcam mode (default): opens the camera and prints one blendshape per frame.
    python detector/probe_blendshape.py
    python detector/probe_blendshape.py --shape jawOpen

Image mode (no camera; for testing the pipeline headless):
    python detector/probe_blendshape.py --image path/to/face.jpg
"""

from __future__ import annotations

import argparse
import sys
import time

import cv2

import config
from landmarker import BlendshapeReader
from mediapipe.tasks.python import vision


def run_image(path: str, shape: str) -> int:
    bgr = cv2.imread(path)
    if bgr is None:
        print(f"Could not read image: {path}", file=sys.stderr)
        return 1
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    reader = BlendshapeReader(running_mode=vision.RunningMode.IMAGE)
    try:
        scores = reader.from_image(rgb)
    finally:
        reader.close()
    if not scores:
        print("No face detected in image.")
        return 2
    print(f"Detected face with {len(scores)} blendshapes.")
    print(f"  {shape} = {scores.get(shape, float('nan')):.3f}")
    top = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:5]
    print("  top 5:", ", ".join(f"{n}={v:.2f}" for n, v in top))
    return 0


_ROTATIONS = {
    90: cv2.ROTATE_90_CLOCKWISE,
    180: cv2.ROTATE_180,
    270: cv2.ROTATE_90_COUNTERCLOCKWISE,
}


def run_webcam(shape: str, cam_index: int, show: bool, rotate: int) -> int:
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print(f"Could not open camera index {cam_index}.", file=sys.stderr)
        return 1
    reader = BlendshapeReader(running_mode=vision.RunningMode.VIDEO)
    print(f"Reading webcam. Watching '{shape}'. "
          f"{'Press q in the window or ' if show else ''}Ctrl-C to stop.")
    start = time.monotonic()
    try:
        while True:
            ok, bgr = cap.read()
            if not ok:
                continue
            if rotate in _ROTATIONS:
                bgr = cv2.rotate(bgr, _ROTATIONS[rotate])
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            ts_ms = int((time.monotonic() - start) * 1000)
            scores = reader.from_video_frame(rgb, ts_ms)
            value = scores.get(shape)

            if value is None:
                print("no face", end="\r")
                status, color = "no face", (0, 0, 255)
            else:
                bar = "#" * int(value * 40)
                print(f"{shape:>14} {value:0.3f} |{bar:<40}|", end="\r")
                status, color = f"{shape} {value:0.3f}", (0, 255, 0)

            if show:
                h, w = bgr.shape[:2]
                cv2.putText(bgr, status, (12, 36), cv2.FONT_HERSHEY_SIMPLEX,
                            1.0, color, 2, cv2.LINE_AA)
                if value is not None:
                    cv2.rectangle(bgr, (12, 52), (12 + int(value * (w - 24)), 80),
                                  color, -1)
                    cv2.rectangle(bgr, (12, 52), (w - 12, 80), (200, 200, 200), 1)
                cv2.imshow("Look Mah, No Hands - probe (q to quit)", bgr)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except KeyboardInterrupt:
        print("\nstopped.")
    finally:
        cap.release()
        if show:
            cv2.destroyAllWindows()
        reader.close()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe one face blendshape value.")
    ap.add_argument("--shape", default="browInnerUp", help="blendshape name to print")
    ap.add_argument("--image", help="run on a static image instead of the webcam")
    ap.add_argument("--cam", type=int, default=config.CAM_INDEX,
                    help=f"webcam index (default {config.CAM_INDEX})")
    ap.add_argument("--no-show", action="store_true", help="disable the preview window")
    ap.add_argument("--rotate", type=int, default=config.CAM_ROTATE,
                    choices=[0, 90, 180, 270],
                    help="rotate frames (for sideways virtual-camera feeds)")
    args = ap.parse_args()

    if args.image:
        return run_image(args.image, args.shape)
    return run_webcam(args.shape, args.cam, show=not args.no_show, rotate=args.rotate)


if __name__ == "__main__":
    raise SystemExit(main())
