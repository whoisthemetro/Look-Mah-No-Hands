# Hands-free facial transport control for Ableton Live

**Date:** 2026-06-16
**Status:** Draft (awaiting go-ahead)

## Goal

Let a guitarist control Ableton Live's transport and navigation entirely with
deliberate facial expressions, so their hands never leave the instrument while
recording. v1 actions: **Play/Stop**, **Back to start**, **Record arm/punch**,
**Undo last take** — with a gesture→action map that is trivial to extend.

## Why it matters

Tracking guitar solo means a constant break in flow: get into position, put the
guitar down (or contort) to hit Play/Record, do the take, stop, jump back, undo
a bad take, repeat. Removing the hands-off-instrument step keeps the player in
the performance and makes re-takes frictionless.

## Constraints & realities

- **Not a conventional plugin.** VST/AU plugins cannot drive a host's transport.
  The transport control must come from a **Max for Live** device (has full Live
  Object Model access) — user confirmed they have M4L.
- **CV can't run in a device.** Webcam access + ML inference run as a separate
  **Python** process (user-confirmed stack), communicating over local OSC/UDP.
- **False-trigger risk is the hard part.** Guitarists make many involuntary
  faces while playing. Gestures must be deliberate (hold + cooldown) and avoid
  natural expressions (e.g. don't use plain blinks). This is the main design
  effort, not the plumbing.
- macOS (Darwin) — webcam permission must be granted to the Python host
  (Terminal/Python). No IAC/MIDI needed since we go OSC → M4L directly.

## Architecture fit

Two decoupled components in this repo:

```
detector/   Python: webcam → MediaPipe Face Landmarker (blendshapes)
            → gesture classifier (hold/cooldown/debounce)
            → python-osc client → UDP :<port>

device/     Max for Live (.amxd): udpreceive :<port> → route OSC addresses
            → live.path/live.object calls on live_set (transport/LOM)
```

Contract between them = the OSC address scheme (the only coupling point):

| OSC address            | Action                         | LOM call (device side)                          |
|------------------------|--------------------------------|-------------------------------------------------|
| `/transport/play`      | Start playback/record          | `live_set call start_playback`                  |
| `/transport/stop`      | Stop                           | `live_set call stop_playback`                   |
| `/transport/return`    | Playhead to 1.1.1              | `live_set set current_song_time 0`              |
| `/transport/recordarm` | Toggle arrangement record      | toggle `live_set record_mode`                   |
| `/transport/undo`      | Undo last take                 | `live_set call undo`                            |
| `/gesture/<name>` (raw)| Debug/visualization passthrough| (status display only)                           |

Adding an action later = one row here + one route in the device + one mapping in
the detector's config. No protocol changes.

## Proposed gesture vocabulary (v1 — tune in Phase 2)

Chosen for being deliberate and distinct from playing-face noise. All require a
~400–600 ms hold and a ~800 ms cooldown; only one gesture active at a time.

- **Eyebrows raise + hold** (`browInnerUp`) → Play/Stop toggle
- **Mouth pucker / "kiss" hold** (`mouthPucker`) → Record arm
- **Jaw open + hold** (`jawOpen`) → Back to start
- **Cheek puff** (`cheekPuff`) → Undo
- Optional master **arm/disarm** gesture (e.g. wink-hold) to freeze detection
  during a take if false-triggers prove troublesome.

## Phases

### Phase 1 — Skeleton + end-to-end signal path  ✅ COMPLETE (2026-06-16)
- ✅ Repo layout (`detector/`, `device/`), Python venv, `requirements.txt`
  (mediapipe, opencv-python, python-osc), README run steps.
- ✅ Minimal Python: webcam → Face Landmarker → print one blendshape value
  (`detector/probe_blendshape.py`, machine-verified on a static face image:
  52 blendshapes returned, sensible scores).
- ✅ Minimal M4L device: `udpreceive 7400` → `print` + `route`
  (`device/maxpat/transport_phase1.maxpat`, JSON-validated).
- ✅ OSC path machine-verified: Python sender → standalone listener, 5/5
  messages received with correct addresses/args.
- Built on Python 3.13 (mediapipe 0.10.35 imports & runs; no 3.11 fallback needed).
- ✅ Live webcam blendshape confirmed by user: `browInnerUp` reads ~0.05 at rest,
  ~0.85 on eyebrow-raise (iPad via Continuity at camera index 2). Excellent
  separation — sets the threshold baseline for Phase 2.
- **Still optional:** confirm OSC in the Max console (the wire is already
  machine-verified via the standalone listener; will recheck when the real
  device is built in Phase 3).

Camera note: index 2 = iPad feed; index 1 = OBS Virtual Camera standby; defaults
captured in `detector/config.py` (CAM_INDEX=2).

### Phase 2 — Gesture classifier
- Blendshape thresholding + hold timer + cooldown + single-active lock.
- Externalized config (`gestures.toml`/`.json`): gesture → threshold/hold/cooldown
  → OSC address. Live on-screen debug overlay (which gesture, confidence, armed).
- **Verify:** each gesture fires its OSC address reliably; no fire from neutral
  playing faces over a 2-min guitar-playing test; cooldown prevents double-fire.

### Phase 3 — M4L transport device  (built; user assembly + test pending)
- ✅ `device/transport.js` — LiveAPI logic (playstop toggle from is_playing, rtz,
  recordarm toggle, undo). Built as a Max MIDI Effect on a dedicated MIDI track
  (no audio passthrough risk). JS syntax-checked.
- ✅ `device/maxpat/transport.maxpat` — `udpreceive 7400` → `route` → message
  boxes → `js transport.js`; JSON + wiring validated.
- ✅ Assembly + test instructions in `device/README.md`.
- Toggle decisions live in the device (read Live's real state) so detector/Live
  can't drift.
- **Pending user (Live-dependent):** assemble the `.amxd` in a Live set and
  confirm each gesture drives the right action; Back-to-start lands at 1.1.1.

### Phase 3.5 — In-device camera + face-tracking display  (NEW, in progress)
Goal: when the device loads, it shows the live camera with a face-tracking
overlay, and lets the user pick their camera — all inside Ableton.
- **Rejected: Syphon.** `syphon-python` builds on 3.13 but ships no Syphon.framework
  ("Bundle could not be loaded"); needs a hand-built native framework + an
  untestable Max Syphon path. Too fragile (validated 2026-06-16).
- **Chosen: native `jit.grab` in the device** for live video + built-in camera
  picker. No Python video deps.
- **Camera sharing** (Max + Python on one camera) solved by routing the iPad
  through **OBS Virtual Camera** (multi-consumer), which the user already has.
- **Face mesh overlay:** Python broadcasts face-detected + landmark points +
  per-gesture state over OSC; the device draws them over the jit.grab video.
  Start with detected/meters, then literal landmark dots.
- Python brain unchanged; add a landmark/status OSC sender + an inbound channel
  for camera selection.
- **Verify:** load device → see live feed + overlay; pick camera from a dropdown;
  overlay reacts to real face/gestures.
- **Status 2026-06-16:** DECOUPLED into two devices (transport + camera) after a
  combined patch proved fragile to paste; both ran simultaneously in Live.
- **Redesign (2026-06-16, user choice): ONE device, Python owns the camera, NO
  raw video.** Instead of jit.grab showing video (which forced a Max-vs-OpenCV
  camera-enumeration bridge), the device shows a **face-mesh/dots visualization**
  drawn from OSC landmarks. Python is the single camera owner, so the in-device
  **camera dropdown** is clean: Python sends the camera list, the device's umenu
  shows it, the user's pick comes back over OSC and Python switches cameras live.
  - Ports: Python→device 7400 (transport + status + camera list); device→Python
    7500 (camera select/refresh).
  - **DONE (Python, tested headless):** camera enumeration + `/camera/list`
    broadcast, control server for `/camera/select`+`/camera/refresh`, live camera
    switching in `detect.py`, shared `cameras.find_cameras()`.
  - **Remaining (device, Max):** a `jsui` face-mesh+meters overlay, a `umenu`
    camera dropdown wired back to Python, all in ONE combined device with
    transport.js. The standalone `camera_picker.py` GUI stays as a fallback.

### Phase 4 — Polish & resilience
- Reconnect/heartbeat so the device shows when the detector is down.
- Sensitivity presets (sensitive / balanced / strict).
- Packaging: freeze the device, document setup, camera-permission steps.
- **Verify:** cold-start works from the README on a clean machine; full
  record-a-take-and-redo loop done 100% hands-free.

## Verification (acceptance)

- Full workflow — arm record, play, stop, jump to start, undo, re-record —
  performed without hands leaving the guitar.
- Zero false transport triggers across a sustained playing session.
- New action can be added by editing only the OSC map + config (proven by adding
  one, e.g. metronome toggle).

## Head-pose gestures (partially implemented 2026-06-16)

- **Head ROLL (tilt) is live.** `derived.head_tilt()` computes roll from the
  eye-line angle (landmarks 33↔263), exposed as `tiltLeft`/`tiltRight` 0..1
  channels the classifier consumes like any blendshape. Default map uses
  tilt-left = undo, tilt-right = record-arm. Sign is an assumption — swap the two
  gestures in `gestures.json` if it reads backwards.
- **Why tilt, not nod:** a guitarist constantly looks DOWN at the fretboard, so
  head-pitch-down would false-fire. Head *tilt* (ear-to-shoulder) is deliberate
  and rare while playing. Avoid pitch-based gestures.
- **Beard constraint** drove this: lip-corner blendshapes (smile/pucker) are
  unreliable for this user, so we lean on brows + jaw + head pose. See the
  [[beard-gesture-constraint]] memory.
- **Still parked:** yaw (turn) gestures, and nod-*motion* detection (down-then-
  return) if we ever want a nod without the fretboard false-fire.

## Open tasks (checkpoint 2026-06-17 — resume here after /clear)

Done: detector + classifier + transport device working in Live; final gesture set
(both-brows=play/stop, tilt-right=record, tilt-left=undo) tuned; camera picker GUI;
new single-device architecture's Python side (camera list/select/live-switch).

Remaining:
1. **Device `jsui` face-mesh + meters overlay** — draw landmark dots from
   `/status/landmarks` + meters from `/status/meters` + face LED. Build as a
   standalone test patch first; syntax-check the JS; user verifies in Max.
2. **Device `umenu` camera dropdown** — populate from `/camera/list`; on select,
   `udpsend /camera/select <position>` to Python:7500; refresh sends
   `/camera/refresh`. Python already handles mapping + live switch.
3. **Combine into ONE device** — udpreceive 7400 → route transport(js)+status+
   camera list; udpsend 7500. Assembly rules: copy in PATCHING view (cords!),
   clear device fully first, save the `.amxd` next to `transport.js`.
4. **Verify/fix `undo`** — Max Console once showed a `SendMessage … 'undo'` error;
   confirm undo works after the clean rebuild, fix the LiveAPI call if not.
5. **Bundle detector as a one-click macOS app** (PyInstaller/py2app) — no Python
   install for testers; later code-sign + notarize. Picker = the app's front screen.

Key facts for a fresh session: camera = OpenCV index from `settings.json` (Max's
jit.grab numbering differs); user has a beard so avoid lip-corner gestures
([[beard-gesture-constraint]]); `transport.js` must sit next to the `.amxd`;
Python detector must run (it's the brain — the device is just OSC in/out).
Run helpers: `./pick-camera`, `./detect`, `./detect --no-osc`.

## Open questions

1. One bidirectional gesture for Play/Stop (toggle) vs. two separate gestures?
2. Record arm = arrangement record toggle, or punch-in/out at the playhead?
3. Want a visual confirmation the player can see (device LED / on-screen flash)
   so they know a gesture registered without looking at the transport?
4. Multi-monitor / camera placement: where does the webcam sit relative to the
   player while seated with a guitar?
