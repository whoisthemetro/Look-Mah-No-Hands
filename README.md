# Look Mah, No Hands

Hands-free transport control for **Ableton Live**, built for guitarists who
record themselves. Deliberate facial expressions drive Play/Stop, jump-to-start,
record-arm, and undo — so your hands never leave the instrument.

> **Status:** working end-to-end on macOS and in daily use by the author. Rough
> edges remain (setup is manual, macOS-only, no signed app yet). Great for a
> technical friend with Ableton + Max for Live; not yet a one-click install for
> non-technical folks. See [`docs/plans/`](docs/plans/) for the roadmap.

## How it works

Two decoupled parts that talk over local OSC (UDP):

```
detector/  Python: webcam → MediaPipe Face Landmarker (blendshapes)
           → gesture classifier → OSC client
                   │  ▲
   /transport/* ,  │  │  /camera/select , /camera/refresh   (device → Python, 7500)
   /status/* ,     │  │
   /camera/list    ▼  │                                     (Python → device, 7400)
device/    Max for Live device "LookMahNoHands.amxd":
           udpreceive → Live Object Model transport calls,
           a face-mesh + gesture-meter overlay, and an
           in-device camera dropdown + start/stop buttons.
```

Python is the brain (owns the camera, runs the ML). The Max device drives Live's
transport and shows what the detector sees. The OSC address scheme is the only
coupling point — see `detector/config.py` and [`device/README.md`](device/README.md).

## Prerequisites

- **macOS** (developed on Darwin; camera + threading specifics are macOS-only).
- **Ableton Live with Max for Live** (Max 9). Required to run the device.
- A **webcam** (built-in, USB, or an iPhone/iPad via Continuity Camera).
- **Python 3.11+** (developed on 3.13). Note: `mediapipe` wheels can be fussy
  across Python versions and Apple-Silicon-vs-Intel — if `pip install` fails,
  that's usually why.

## Setup (detector)

From the repo root:

```bash
python3 -m venv detector/.venv
detector/.venv/bin/python -m pip install -r detector/requirements.txt
```

Download the Face Landmarker model (not committed) to `models/face_landmarker.task`:

```bash
mkdir -p models
curl -sSL -o models/face_landmarker.task \
  "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
```

> macOS will prompt for camera access the first time the detector runs. Grant it
> to your terminal app (System Settings → Privacy & Security → Camera). If you
> launch the detector from the device's **start** button instead, the prompt is
> for **Ableton Live** — see `device/README.md`.

## Pick a camera and tune (per user)

```bash
./pick-camera          # choose your camera from a live preview (writes settings.json)
./detect --no-osc      # watch gestures live without sending OSC (good first run)
./calibrate            # tune thresholds to your face/lighting (writes gestures.json)
```

Each person's camera index and thresholds differ, so these are first-run steps.
`settings.json` is per-machine and not committed.

## Run

```bash
./detect               # webcam → gestures → OSC to the device on 127.0.0.1:7400
./detect --no-show     # headless (no preview window; the device shows the overlay)
```

Then load the Max device (next section) and play. The detector window shows each
gesture's live value, threshold tick, hold progress, arm/cooldown state, and
flashes "FIRED" on trigger.

## One-click app (no Python needed)

For sharing with people who don't want to touch a terminal, the detector can be
bundled into a double-clickable macOS app. **Build it once** (needs the dev setup
above + the model downloaded):

```bash
./build_app.sh        # → dist/LookMahNoHands-Detector.app (~270 MB, self-contained)
```

The `.app` bundles Python, mediapipe, OpenCV, the model, and `gestures.json` — a
tester just needs the app and the Max device; **no Python, venv, or download.**
They pick their camera from the device's dropdown inside Ableton.

First-run on a tester's Mac (it's unsigned for now):
1. **Right-click the app → Open** (Gatekeeper warns on unsigned apps; this
   approves it once).
2. **Allow camera access** when macOS prompts (the prompt is for the app itself).
3. A preview window opens showing the face mesh + meters; close it / press `q` to
   quit.

> Distribute the built `.app` via a **GitHub Release** (zip it and attach) — it's
> too big for git and isn't committed. Code-signing + notarization (to skip the
> Gatekeeper step) is a later task; see `docs/plans/2026-06-17-01-*`.

## The Max for Live device

A prebuilt **`device/LookMahNoHands.amxd`** is included. It depends on the scripts
beside it (`transport.js`, `face_overlay.js`, `launch_detector.js`), so **keep the
`device/` folder together** — dropping just the `.amxd` elsewhere breaks it (or
*freeze* the device to embed the scripts; see below).

Full assembly, the OSC contract, the camera dropdown, the start/stop launch
buttons, and the known Max gotchas (threading, why `undo` uses native objects)
are documented in **[`device/README.md`](device/README.md)**.

## Gestures (default map)

Defined in `detector/gestures.json` (blendshape, threshold, hysteresis, hold,
cooldown, OSC address). False triggers are resisted via hold-time, hysteresis,
per-gesture cooldown, and single-active gating.

| Gesture                          | Action       |
|----------------------------------|--------------|
| Both brows raise                 | Play / Stop  |
| Head tilt **right** (ear→shoulder) | Record-arm |
| Head tilt **left**               | Undo         |

More channels are available to add/swap in `gestures.json`: head pose
`lookUp`/`lookDown`/`turnLeft`/`turnRight` and `tiltLeft`/`tiltRight`; face
`jawOpen`, `smile`, `browUpLeft`/`browUpRight`, `winkLeft`/`winkRight`. Avoid
`lookDown` for guitarists (constant fretboard glances would false-fire).

## Repo layout

```
detector/   Python: camera, ML, classifier, OSC, camera picker, tests
device/     Max for Live device + scripts (see device/README.md)
models/     face_landmarker.task (downloaded, not committed)
docs/plans/ design + roadmap
```
