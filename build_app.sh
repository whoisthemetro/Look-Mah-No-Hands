#!/usr/bin/env bash
# Build the one-click macOS app for the detector (Task 5).
#
#   ./build_app.sh
#
# Output: dist/LookMahNoHands-Detector.app  (double-clickable, no Python needed).
# See docs/plans/2026-06-17-01-one-click-detector-app.md.
set -euo pipefail
cd "$(dirname "$0")"

PY=detector/.venv/bin/python
MODEL=models/face_landmarker.task

if [ ! -f "$MODEL" ]; then
  echo "ERROR: $MODEL not found. Download it first (see README) so it can be bundled." >&2
  exit 1
fi

exec "$PY" -m PyInstaller \
  --noconfirm --clean --windowed \
  --name "LookMahNoHands-Detector" \
  --paths detector \
  --collect-all mediapipe \
  --collect-all cv2 \
  --add-data "$MODEL:models" \
  --add-data "detector/gestures.json:." \
  detector/app_main.py
