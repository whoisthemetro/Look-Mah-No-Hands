# Look Mah, No Hands

Hands-free transport control for **Ableton Live**, built for guitarists who
record themselves. Deliberate facial expressions drive Play/Stop, jump-to-start,
record-arm, and undo — so your hands never leave the instrument.

See the design plan in [`docs/plans/`](docs/plans/).

## How it works

Two decoupled parts that talk over local OSC (UDP):

```
detector/  Python: webcam → MediaPipe Face Landmarker (blendshapes)
           → gesture classifier → OSC client
                       │  OSC /transport/* on 127.0.0.1:7400
                       ▼
device/    Max for Live device: udpreceive → Live Object Model transport calls
```

The OSC address scheme is the only coupling point — see `detector/config.py`.

## Setup (detector)

Requires Python 3.11+ (developed on 3.13). From the repo root:

```bash
python3 -m venv detector/.venv
detector/.venv/bin/python -m pip install -r detector/requirements.txt
```

The Face Landmarker model lives at `models/face_landmarker.task` (not committed —
download it once):

```bash
curl -sSL -o models/face_landmarker.task \
  "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
```

> macOS will prompt for camera access the first time the detector runs. Grant it
> to your terminal app (System Settings → Privacy & Security → Camera).

## Phase 1 — signal path (complete, machine-verified)

The detector → OSC → receiver path is built and tested. Scripts (run from repo root):

```bash
# Verify the CV pipeline on a still image (no webcam needed):
detector/.venv/bin/python detector/probe_blendshape.py --image <face.jpg>

# Live webcam: print one blendshape value (Ctrl-C to stop):
detector/.venv/bin/python detector/probe_blendshape.py --shape browInnerUp

# OSC round-trip without Max — listener in one terminal:
detector/.venv/bin/python detector/osc_listen.py
# ...sender in another:
detector/.venv/bin/python detector/send_test_osc.py
```

**Two hands-on confirmations need your hardware:**
1. **Webcam** — run the live `probe_blendshape.py` and watch the bar move when you
   raise your eyebrows. (Grant camera permission when macOS prompts.)
2. **Max** — open `device/maxpat/transport_phase1.maxpat`, open the Max Console,
   run `send_test_osc.py`, and confirm the `RX`/route lines print (see
   `device/README.md`).

## Phase 2 — gesture classifier (built; tuning is per-user)

The detector maps deliberate facial expressions to transport OSC. Gestures are
defined in `detector/gestures.json` (blendshape, threshold, hysteresis, hold,
cooldown, OSC address) and resist false triggers via hold-time, hysteresis,
per-gesture cooldown, and single-active gating.

Default map (3 gestures): both-brows-raise → Play/Stop · tilt-right → record-arm ·
tilt-left → undo. More channels are available to add/swap in `gestures.json`:
head pose `lookUp`/`lookDown`/`turnLeft`/`turnRight` (pitch/yaw) and `tiltLeft`/
`tiltRight` (roll); face `jawOpen`, `smile`, `browUpLeft`/`browUpRight`,
`winkLeft`/`winkRight`. Avoid `lookDown` for guitarists (fretboard glances).

```bash
# Choose your camera from a live preview (saves to settings.json):
./pick-camera

# Watch the gestures live without sending OSC (recommended first run):
./detect --no-osc

# Tune thresholds to your face/lighting (writes detector/gestures.json):
./calibrate

# Run for real (sends OSC to the device on 127.0.0.1:7400):
./detect
```

The detector window shows each gesture's live value, threshold tick, hold
progress, arm/cooldown state, and flashes "FIRED" on trigger. Tests for the
classifier: `detector/.venv/bin/python detector/test_classifier.py`.

Next: Phase 3 (the Max for Live device drives Live's transport). See `docs/plans/`.
