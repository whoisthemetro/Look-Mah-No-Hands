# One-click macOS app for the detector (Task 5)

**Date:** 2026-06-17
**Status:** Working build (2026-06-17) — `./build_app.sh` produces
`dist/LookMahNoHands-Detector.app` (~270 MB). Smoke-tested: the bundled binary
loads the model from inside the app, opens the camera, and streams the full
`/camera/list` + `/status/*` OSC (286 msgs in 28 s) with no Python install.
Remaining: code-sign + notarize, and ship via a GitHub Release.

## Goal

Bundle the Python detector into a **double-clickable macOS `.app`** so testers run
it with no Python install, no venv, no `pip`, no model download. They double-click,
grant camera permission once, and use the Max device as normal.

## Why it matters

Right now sharing needs: clone repo → make venv → `pip install` (mediapipe is
fussy) → `curl` the model → run from terminal. That's the wall non-technical
"peeps" hit. A single `.app` removes the entire setup.

## Decisions / constraints

- **PyInstaller, `--onedir` `.app` bundle** (not `--onefile`): mediapipe ships
  native libs + data files; onedir is far more reliable and starts faster.
- **No in-app picker GUI.** The Max device already has a live camera dropdown that
  switches Python's camera over OSC, so the app runs headless-of-config and the
  user picks the camera inside Ableton. Avoids bundling tkinter/PIL.
- **Bundle the model + gestures.json** inside the app (`face_landmarker.task`,
  `gestures.json`) so there's no download and no external file deps.
- **Keep the OpenCV preview window** as the app's visible surface: it's the
  "it's running" proof + the quit affordance (press `q` / close window). The
  in-Ableton overlay is the other view; the preview is for the standalone app.
- **Unsigned for now.** First run needs right-click → Open (Gatekeeper) and a
  camera-permission grant attributed to the app. Code-sign + notarize is a later
  step so testers don't see the warning.

## Work

1. `config.py`: when `sys.frozen`, resolve `MODEL_PATH` + `GESTURE_CONFIG` from
   the bundle (`sys._MEIPASS`) and skip the `settings.json` read (app bundle is
   read-only; camera comes from the device dropdown).
2. `detector/app_main.py`: thin entry point that neutralizes macOS launch args
   (`-psn_…`) and runs `detect.main()` with the preview window + OSC on.
3. `detector/requirements-build.txt` (pyinstaller) + `build_app.sh` / a `.spec`
   that `--collect-all mediapipe`, `--collect-all cv2`, adds the model +
   gestures.json as data, and emits `dist/LookMahNoHands-Detector.app`.
4. Build, smoke-test the bundled binary (imports + model load + OSC), iterate on
   missing data files / hidden imports until it runs.
5. Document in the root README (download/run the `.app`); note the Gatekeeper +
   camera-permission first-run steps.

## Verification

- `dist/LookMahNoHands-Detector.app` launches by double-click on a Mac with **no
  Python installed**, opens the preview, and drives Live through the device.
- Bundled binary loads the model from inside the app (no external `models/` dir).

## Open / later

- Code-sign + notarize (Developer ID) so testers skip the Gatekeeper warning.
- Optional: a tiny menubar/status UI instead of the OpenCV window.
- Optional: make the device's **start** button launch the `.app` instead of the
  venv python, so even that path needs no Python.
- GitHub Releases attachment (the `.app` zipped) so testers download a binary,
  not the repo.
