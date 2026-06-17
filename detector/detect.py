"""Main detector: webcam -> face blendshapes -> gesture classifier -> OSC.

This is the runnable Phase 2 product. A preview window shows each gesture's live
value, threshold, hold progress, arm/cooldown state, and flashes when it fires.

    detector/.venv/bin/python detector/detect.py
    detector/.venv/bin/python detector/detect.py --no-osc      # test without sending
    detector/.venv/bin/python detector/detect.py --no-show     # headless

Press q in the window (or Ctrl-C) to stop.
"""

from __future__ import annotations

import argparse
import time

import threading

import cv2
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer

import cameras
import config
import gestures_config
from classifier import GestureClassifier
from landmarker import BlendshapeReader
from mediapipe.tasks.python import vision
from osc_out import TransportOSC

_ROTATIONS = {
    90: cv2.ROTATE_90_CLOCKWISE,
    180: cv2.ROTATE_180,
    270: cv2.ROTATE_90_COUNTERCLOCKWISE,
}

FLASH_MS = 600


class CameraControl:
    """Shared state for the device->Python camera handshake (thread-safe enough:
    only simple assignments, guarded by the GIL)."""

    def __init__(self, camera_list):
        self.camera_list = camera_list          # [(cv2_index, label), ...]
        self.pending_index = None               # set by OSC thread on /camera/select
        self.resend = True                      # resend the list to the device

    def on_select(self, _addr, position):
        try:
            pos = int(position)
        except (TypeError, ValueError):
            return
        if 0 <= pos < len(self.camera_list):
            self.pending_index = self.camera_list[pos][0]

    def on_refresh(self, _addr, *_args):
        self.resend = True


def start_control_server(control: CameraControl):
    disp = Dispatcher()
    disp.map(config.ADDR_CAMERA_SELECT, control.on_select)
    disp.map(config.ADDR_CAMERA_REFRESH, control.on_refresh)
    ThreadingOSCUDPServer.allow_reuse_address = True
    server = ThreadingOSCUDPServer((config.OSC_HOST, config.CONTROL_PORT), disp)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def _color(st, threshold):
    if st.cooling_ms > 0:
        return (150, 150, 150)        # cooling down (gray)
    if not st.armed:
        return (0, 200, 255)          # relax to re-arm (yellow)
    if st.value >= threshold:
        return (0, 165, 255)          # counting toward fire (orange)
    return (220, 220, 220)            # idle (light gray)


def draw_overlay(frame, clf, last_fire, now_ms):
    bar_w = 320
    x = 14
    for i, g in enumerate(clf.cfg.gestures):
        st = clf.status[g.name]
        y = 26 + i * 62
        color = _color(st, g.threshold)

        label = f"{g.name}  [{g.blendshape}]  {st.value:0.2f}"
        cv2.putText(frame, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, color, 2, cv2.LINE_AA)

        # value bar
        by0, by1 = y + 8, y + 26
        cv2.rectangle(frame, (x, by0), (x + bar_w, by1), (60, 60, 60), -1)
        cv2.rectangle(frame, (x, by0), (x + int(st.value * bar_w), by1), color, -1)
        # threshold tick
        tx = x + int(g.threshold * bar_w)
        cv2.line(frame, (tx, by0 - 3), (tx, by1 + 3), (255, 255, 255), 1)
        # hold progress underline
        if st.progress > 0:
            cv2.rectangle(frame, (x, by1 + 2), (x + int(st.progress * bar_w), by1 + 5),
                          (0, 255, 0), -1)

        # fire flash
        if now_ms - last_fire.get(g.name, -10**9) < FLASH_MS:
            cv2.putText(frame, "FIRED", (x + bar_w + 16, y + 18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)


def main() -> int:
    ap = argparse.ArgumentParser(description="Facial gesture -> Ableton transport.")
    ap.add_argument("--cam", type=int, default=config.CAM_INDEX)
    ap.add_argument("--rotate", type=int, default=config.CAM_ROTATE,
                    choices=[0, 90, 180, 270])
    ap.add_argument("--no-show", action="store_true", help="disable preview window")
    ap.add_argument("--no-osc", action="store_true", help="do not send OSC (dry run)")
    args = ap.parse_args()

    cfg = gestures_config.load()
    clf = GestureClassifier(cfg)
    osc = None if args.no_osc else TransportOSC()

    # Enumerate cameras and start the device->Python control server.
    camera_list = cameras.find_cameras()
    control = CameraControl(camera_list)
    if osc is not None:
        start_control_server(control)
    cur_index = args.cam
    if camera_list and cur_index not in [i for i, _ in camera_list]:
        cur_index = camera_list[0][0]  # requested cam not found; use first available

    cap = cv2.VideoCapture(cur_index)
    if not cap.isOpened():
        print(f"Could not open camera index {cur_index}.")
        return 1
    reader = BlendshapeReader(running_mode=vision.RunningMode.VIDEO)

    print(f"Detector running. camera {cur_index}, {len(cfg.gestures)} gestures. "
          f"OSC {'OFF (dry run)' if args.no_osc else f'-> {config.OSC_HOST}:{config.OSC_PORT}'}.")
    for g in cfg.gestures:
        print(f"  {g.name:10} {g.blendshape:14} -> {g.osc}")

    last_fire: dict[str, int] = {}
    show = not args.no_show
    start = time.monotonic()
    status_interval = 1000 // config.STATUS_HZ
    last_status_ms = -10**9
    last_list_ms = -10**9
    try:
        while True:
            # Live camera switch requested by the device dropdown.
            if control.pending_index is not None and control.pending_index != cur_index:
                cur_index = control.pending_index
                control.pending_index = None
                cap.release()
                cap = cv2.VideoCapture(cur_index)
                print(f"switched to camera {cur_index}")

            ok, bgr = cap.read()
            if not ok:
                continue
            if args.rotate in _ROTATIONS:
                bgr = cv2.rotate(bgr, _ROTATIONS[args.rotate])
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            now_ms = int((time.monotonic() - start) * 1000)
            scores = reader.from_video_frame(rgb, now_ms)

            for ev in clf.update(scores, now_ms):
                last_fire[ev.name] = now_ms
                tag = "[dry]" if args.no_osc else "[osc]"
                print(f"{tag} FIRE {ev.name:10} {ev.osc:22} (held {ev.held_ms}ms)")
                if osc is not None:
                    osc.send_osc(ev.osc)

            # Throttled status/landmark broadcast for the device overlay.
            if osc is not None and now_ms - last_status_ms >= status_interval:
                last_status_ms = now_ms
                osc.send_face(bool(reader.last_landmarks))
                osc.send_meters([clf.status[g.name].value for g in cfg.gestures])
                for g in cfg.gestures:
                    st = clf.status[g.name]
                    osc.send_gesture_status(g.name, st.value, g.threshold,
                                            st.progress, st.armed)
                if reader.last_landmarks:
                    osc.send_landmarks(reader.last_landmarks[::config.LANDMARK_STRIDE])

            # Resend the camera list on request or every ~2s (so a freshly loaded
            # device populates its dropdown).
            if osc is not None and (control.resend or now_ms - last_list_ms >= 2000):
                control.resend = False
                last_list_ms = now_ms
                osc.send_camera_list([label for _, label in control.camera_list])

            if show:
                draw_overlay(bgr, clf, last_fire, now_ms)
                cv2.imshow("Look Mah, No Hands - detector (q to quit)", bgr)
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


if __name__ == "__main__":
    raise SystemExit(main())
