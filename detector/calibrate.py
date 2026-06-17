"""Interactive threshold calibration: tune gestures.json to your face + lighting.

For each gesture it records your RELAXED face, then the GESTURE held, and picks a
threshold/release between the two. Writes the results back into gestures.json
(keeping hold_ms / cooldown_ms / osc untouched).

    detector/.venv/bin/python detector/calibrate.py

Controls (in the preview window):
    SPACE  start the 2-second capture for the current step
    s      skip this gesture (keep its existing values)
    q      quit (saves everything calibrated so far)
"""

from __future__ import annotations

import json
import time

import cv2
import numpy as np

import config
import gestures_config
from landmarker import BlendshapeReader
from mediapipe.tasks.python import vision

_ROTATIONS = {90: cv2.ROTATE_90_CLOCKWISE, 180: cv2.ROTATE_180,
              270: cv2.ROTATE_90_COUNTERCLOCKWISE}

CAPTURE_SEC = 2.0
MIN_SEPARATION = 0.08  # warn if peak barely rises above rest


def capture(reader, cap, rotate, blendshape, seconds, label, draw_hud):
    """Collect blendshape samples for `seconds`, drawing a live HUD."""
    samples = []
    start = time.monotonic()
    while time.monotonic() - start < seconds:
        ok, bgr = cap.read()
        if not ok:
            continue
        if rotate in _ROTATIONS:
            bgr = cv2.rotate(bgr, _ROTATIONS[rotate])
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        ts = int((time.monotonic()) * 1000)
        scores = reader.from_video_frame(rgb, ts)
        v = scores.get(blendshape, 0.0)
        samples.append(v)
        remaining = seconds - (time.monotonic() - start)
        draw_hud(bgr, f"{label}  capturing {remaining:0.1f}s   value={v:0.2f}", v)
        cv2.imshow(WIN, bgr)
        cv2.waitKey(1)
    return samples


WIN = "Look Mah, No Hands - calibrate"


def make_hud(blendshape):
    def draw(frame, text, value):
        cv2.putText(frame, text, (14, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, blendshape, (14, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (220, 220, 220), 2, cv2.LINE_AA)
        w = frame.shape[1] - 28
        cv2.rectangle(frame, (14, 66), (14 + w, 86), (60, 60, 60), -1)
        cv2.rectangle(frame, (14, 66), (14 + int(value * w), 86), (0, 200, 255), -1)
    return draw


def wait_for_key(reader, cap, rotate, blendshape, prompt, draw_hud):
    """Show a prompt and live value until the user presses a key."""
    while True:
        ok, bgr = cap.read()
        if not ok:
            continue
        if rotate in _ROTATIONS:
            bgr = cv2.rotate(bgr, _ROTATIONS[rotate])
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        ts = int(time.monotonic() * 1000)
        v = reader.from_video_frame(rgb, ts).get(blendshape, 0.0)
        draw_hud(bgr, prompt, v)
        cv2.imshow(WIN, bgr)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord(" "), ord("s"), ord("q")):
            return key


def calibrate_gesture(reader, cap, rotate, g):
    hud = make_hud(g.blendshape)
    key = wait_for_key(reader, cap, rotate, g.blendshape,
                       f"{g.name}: RELAX face. SPACE=capture rest, s=skip, q=quit", hud)
    if key == ord("s"):
        print(f"  {g.name}: skipped")
        return None
    if key == ord("q"):
        return "quit"
    rest = capture(reader, cap, rotate, g.blendshape, CAPTURE_SEC,
                   f"{g.name}: REST", hud)

    key = wait_for_key(reader, cap, rotate, g.blendshape,
                       f"{g.name}: MAKE THE FACE & hold. SPACE=capture, s=skip, q=quit", hud)
    if key == ord("s"):
        print(f"  {g.name}: skipped")
        return None
    if key == ord("q"):
        return "quit"
    peak = capture(reader, cap, rotate, g.blendshape, CAPTURE_SEC,
                   f"{g.name}: GESTURE", hud)

    rest_hi = float(np.percentile(rest, 90))   # top of resting noise
    peak_lo = float(np.percentile(peak, 10))   # bottom of held gesture
    if peak_lo - rest_hi < MIN_SEPARATION:
        print(f"  {g.name}: WARNING weak separation (rest~{rest_hi:.2f}, "
              f"peak~{peak_lo:.2f}). Consider a different blendshape or more light.")
    threshold = round(rest_hi + 0.5 * (peak_lo - rest_hi), 2)
    release = round(rest_hi + 0.25 * (peak_lo - rest_hi), 2)
    threshold = min(max(threshold, 0.05), 0.95)
    release = min(max(release, 0.02), threshold - 0.02)
    print(f"  {g.name}: rest~{rest_hi:.2f} peak~{peak_lo:.2f} "
          f"-> threshold={threshold} release={release}")
    return {"threshold": threshold, "release": release}


def main() -> int:
    cfg = gestures_config.load()
    cap = cv2.VideoCapture(config.CAM_INDEX)
    if not cap.isOpened():
        print(f"Could not open camera index {config.CAM_INDEX}.")
        return 1
    reader = BlendshapeReader(running_mode=vision.RunningMode.VIDEO)

    print("Calibration. Follow the prompts in the window.")
    results = {}
    try:
        for g in cfg.gestures:
            r = calibrate_gesture(reader, cap, config.CAM_ROTATE, g)
            if r == "quit":
                break
            if r:
                results[g.name] = r
    finally:
        cap.release()
        cv2.destroyAllWindows()
        reader.close()

    if not results:
        print("Nothing calibrated; gestures.json unchanged.")
        return 0

    raw = json.loads(config.GESTURE_CONFIG.read_text())
    for gesture in raw["gestures"]:
        if gesture["name"] in results:
            gesture.update(results[gesture["name"]])
    config.GESTURE_CONFIG.write_text(json.dumps(raw, indent=2) + "\n")
    print(f"Updated {len(results)} gesture(s) in {config.GESTURE_CONFIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
