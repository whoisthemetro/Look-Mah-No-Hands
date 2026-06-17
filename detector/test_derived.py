"""Tests for derived channels (run directly: no pytest needed).

    detector/.venv/bin/python detector/test_derived.py
"""

from __future__ import annotations

import derived


def check(label, cond):
    print(f"  {'PASS' if cond else 'FAIL'}  {label}")
    assert cond, label


def main():
    print("Running derived-channel tests...")

    # Left wink: left eye shut, right open -> winkLeft high, winkRight ~0.
    s = derived.augment({"eyeBlinkLeft": 0.95, "eyeBlinkRight": 0.05})
    check("left wink -> winkLeft high", s["winkLeft"] > 0.8)
    check("left wink -> winkRight zero", s["winkRight"] == 0.0)

    # Blink: both eyes shut -> both winks ~0 (THE key false-trigger guard).
    s = derived.augment({"eyeBlinkLeft": 0.92, "eyeBlinkRight": 0.90})
    check("blink -> winkLeft near zero", s["winkLeft"] < 0.1)
    check("blink -> winkRight near zero", s["winkRight"] < 0.1)

    # Right wink.
    s = derived.augment({"eyeBlinkLeft": 0.04, "eyeBlinkRight": 0.88})
    check("right wink -> winkRight high", s["winkRight"] > 0.8)
    check("right wink -> winkLeft zero", s["winkLeft"] == 0.0)

    # Single left brow up -> browUpLeft high, browUpRight ~0.
    s = derived.augment({"browOuterUpLeft": 0.80, "browOuterUpRight": 0.10})
    check("left brow up -> browUpLeft high", s["browUpLeft"] > 0.6)
    check("left brow up -> browUpRight zero", s["browUpRight"] == 0.0)

    # BOTH brows up (the play/stop gesture) -> browUpLeft ~0 (no undo cross-fire).
    s = derived.augment({"browOuterUpLeft": 0.85, "browOuterUpRight": 0.82})
    check("both brows up -> browUpLeft near zero", s["browUpLeft"] < 0.1)

    # Smile -> combined smile high; mouth-open alone -> smile ~0 (no cross-fire).
    s = derived.augment({"mouthSmileLeft": 0.8, "mouthSmileRight": 0.7})
    check("grin -> smile high", s["smile"] > 0.7)
    s = derived.augment({"jawOpen": 0.9, "mouthSmileLeft": 0.05, "mouthSmileRight": 0.05})
    check("mouth-open only -> smile near zero", s["smile"] < 0.1)

    # Empty (no face) -> no crash, no channels invented.
    s = derived.augment({})
    check("empty scores stay empty", s == {})

    # Head tilt from eye-corner landmarks. Build a 264-point list; only the two
    # eye corners (33, 263) matter. Upright = same y.
    lm = [(0.5, 0.5)] * 264
    lm[33] = (0.4, 0.5)   # left corner
    lm[263] = (0.6, 0.5)  # right corner, level -> upright
    t = derived.head_tilt(lm)
    check("upright -> both tilts ~0", t["tiltLeft"] < 0.1 and t["tiltRight"] < 0.1)

    lm[263] = (0.6, 0.6)  # right-image corner dropped -> positive angle -> tiltLeft
    t = derived.head_tilt(lm)
    check("tilt one way -> tiltLeft fires, tiltRight 0",
          t["tiltLeft"] > 0.1 and t["tiltRight"] == 0.0)

    lm[263] = (0.6, 0.4)  # right-image corner raised -> negative angle -> tiltRight
    t = derived.head_tilt(lm)
    check("tilt other way -> tiltRight fires, tiltLeft 0",
          t["tiltRight"] > 0.1 and t["tiltLeft"] == 0.0)

    # No landmarks -> no tilt channels.
    check("no landmarks -> empty tilt", derived.head_tilt([]) == {})

    # Head pose from a 4x4 matrix. Identity = facing forward -> all ~0.
    ident = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    p = derived.head_pose(ident)
    check("facing forward -> lookUp/lookDown ~0", p["lookUp"] < 0.1 and p["lookDown"] < 0.1)

    # Pure pitch rotation Rx(+0.4) -> pitch positive -> lookUp fires.
    import math as _m
    th = 0.4
    rx = [[1, 0, 0, 0],
          [0, _m.cos(th), -_m.sin(th), 0],
          [0, _m.sin(th), _m.cos(th), 0],
          [0, 0, 0, 1]]
    p = derived.head_pose(rx)
    check("pitch up -> lookUp fires, lookDown 0", p["lookUp"] > 0.1 and p["lookDown"] == 0.0)
    rx_down = [[1, 0, 0, 0],
               [0, _m.cos(-th), -_m.sin(-th), 0],
               [0, _m.sin(-th), _m.cos(-th), 0],
               [0, 0, 0, 1]]
    p = derived.head_pose(rx_down)
    check("pitch down -> lookDown fires, lookUp 0", p["lookDown"] > 0.1 and p["lookUp"] == 0.0)

    check("no matrix -> empty pose", derived.head_pose(None) == {})

    print("All derived-channel tests passed.")


if __name__ == "__main__":
    main()
