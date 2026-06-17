"""Shared configuration for the facial transport detector.

Single source of truth for the OSC contract between the Python detector and the
Max for Live device. Keep the OSC addresses here in sync with device/README.md.
"""

from pathlib import Path

# --- Paths ---
REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = REPO_ROOT / "models" / "face_landmarker.task"
GESTURE_CONFIG = Path(__file__).resolve().parent / "gestures.json"

# --- Camera ---
# Defaults; overridden by settings.json (written by camera_picker.py) so each
# user can choose their own camera without editing code. OpenCV's index differs
# from Max/jit.grab's vdevice numbering.
CAM_INDEX = 0
CAM_ROTATE = 0  # degrees; set if the feed comes in sideways

SETTINGS_PATH = Path(__file__).resolve().parent / "settings.json"


def _load_user_settings():
    global CAM_INDEX, CAM_ROTATE
    if not SETTINGS_PATH.exists():
        return
    try:
        import json
        s = json.loads(SETTINGS_PATH.read_text())
        CAM_INDEX = int(s.get("cam_index", CAM_INDEX))
        CAM_ROTATE = int(s.get("cam_rotate", CAM_ROTATE))
    except Exception:
        pass  # bad/edited settings file -> fall back to defaults


_load_user_settings()

# --- OSC ports ---
OSC_HOST = "127.0.0.1"
OSC_PORT = 7400          # Python -> device (transport, status, camera list)
CONTROL_PORT = 7500      # device -> Python (camera selection, list refresh)

# --- OSC address scheme (the contract with the device) ---
# v1 transport actions. Extend by adding a row here, a route in the device,
# and a gesture mapping in the classifier (Phase 2).
ADDR_PLAY = "/transport/play"
ADDR_STOP = "/transport/stop"
ADDR_PLAYSTOP = "/transport/playstop"  # toggle; device decides play vs stop from Live state
ADDR_RETURN = "/transport/return"
ADDR_RECORDARM = "/transport/recordarm"
ADDR_UNDO = "/transport/undo"

# Raw gesture passthrough for debugging / device-side status display.
ADDR_GESTURE = "/gesture"  # e.g. /gesture/browInnerUp <float confidence>

# --- Status broadcast (detector -> device overlay) ---
ADDR_STATUS_FACE = "/status/face"          # <int 0|1> face detected
ADDR_STATUS_METERS = "/status/meters"      # <v0> <v1> ... gesture values in config order
ADDR_STATUS_GESTURE = "/status/gesture"    # <name> <value> <threshold> <progress> <armed>
ADDR_STATUS_LANDMARKS = "/status/landmarks"  # x0 y0 x1 y1 ... (normalized 0..1)

# --- Camera selection handshake (detector <-> device) ---
ADDR_CAMERA_LIST = "/camera/list"      # detector -> device: label0 label1 ... (umenu items)
ADDR_CAMERA_SELECT = "/camera/select"  # device -> detector: <int menu position>
ADDR_CAMERA_REFRESH = "/camera/refresh"  # device -> detector: please resend the list
STATUS_HZ = 20              # how often to push status/landmarks to the device
LANDMARK_STRIDE = 3        # send every Nth landmark to keep messages small
