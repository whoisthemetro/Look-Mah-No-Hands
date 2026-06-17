"""Entry point for the bundled one-click macOS app (PyInstaller).

Double-clicking a .app passes no useful argv (and sometimes a -psn_… process
serial on older macOS), so we neutralize argv and run the detector with its
preview window + OSC on. The camera is chosen live from the Max device's
dropdown, so no CLI flags are needed here.

Build: see build_app.sh in the repo root.
"""

import os
import sys

# Strip any launch args macOS hands a .app so detect.py's argparse sees none.
sys.argv = [sys.argv[0]]

# Bundled run: make the detector's own module imports resolve the same whether
# frozen or not (config.py already branches on sys.frozen).
import detect  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(detect.main())
