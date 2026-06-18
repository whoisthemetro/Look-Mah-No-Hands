#!/usr/bin/env bash
# Build the one-click macOS app for the detector (Task 5).
#
#   ./build_app.sh
#
# Outputs:
#   dist/LookMahNoHands-Detector.app  — double-clickable detector (no Python needed)
#   dist/LookMahNoHands.zip           — hand-off bundle: the .app + device/ + INSTALL.txt
#
# See docs/plans/2026-06-17-01-one-click-detector-app.md.
set -euo pipefail
cd "$(dirname "$0")"

PY=detector/.venv/bin/python
MODEL=models/face_landmarker.task

if [ ! -f "$MODEL" ]; then
  echo "ERROR: $MODEL not found. Download it first (see README) so it can be bundled." >&2
  exit 1
fi

"$PY" -m PyInstaller \
  --noconfirm --clean --windowed \
  --name "LookMahNoHands-Detector" \
  --paths detector \
  --collect-all mediapipe \
  --collect-all cv2 \
  --add-data "$MODEL:models" \
  --add-data "detector/gestures.json:." \
  detector/app_main.py

# --- Assemble the hand-off bundle ---------------------------------------------
# One zip a tester downloads and unzips: the detector app, the Max device folder,
# and the install guide. No git, no Python, no model download on their end.
APP="dist/LookMahNoHands-Detector.app"
STAGE="dist/LookMahNoHands"
ZIP="dist/LookMahNoHands.zip"

echo "Packaging hand-off bundle -> $ZIP"
rm -rf "$STAGE" "$ZIP"
mkdir -p "$STAGE/device"
# ditto preserves the .app bundle (symlinks, code signature) — cp -R can mangle it.
ditto "$APP" "$STAGE/LookMahNoHands-Detector.app"
# Ship ONLY the device's runtime files. The unfrozen .amxd loads these three .js
# from beside it; everything else in device/ is editable source, tests, or scratch
# (e.g. the gitignored Gestures.amxd) that testers don't need. Allow-list, so new
# scratch files never leak into a release.
DEVICE_FILES=(
  device/LookMahNoHands.amxd
  device/transport.js
  device/face_overlay.js
  device/launch_detector.js
)
for f in "${DEVICE_FILES[@]}"; do
  if [ ! -f "$f" ]; then
    echo "ERROR: required device file missing: $f" >&2
    exit 1
  fi
  cp "$f" "$STAGE/device/"
done
cp INSTALL.txt "$STAGE/INSTALL.txt"
# Zip the staging folder (keepParent so it unzips to a single LookMahNoHands/ dir).
ditto -c -k --sequesterRsrc --keepParent "$STAGE" "$ZIP"
rm -rf "$STAGE"

echo "Done."
echo "  App:    $APP"
echo "  Bundle: $ZIP  ($(du -h "$ZIP" | cut -f1)) — send this to testers."
