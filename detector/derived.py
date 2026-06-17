"""Derived signal channels computed from raw MediaPipe blendshapes.

These behave like extra blendshapes (a name -> 0..1 score) so gestures.json can
target them exactly like a real blendshape. Added to every score dict by the
landmarker, so all consumers (detect, calibrate, probe) see them.

Differentials separate a one-sided expression from a symmetric one:
  winkLeft/winkRight     -- one eye closed vs. a (both-eye) blink.
  browUpLeft/browUpRight -- one eyebrow raised vs. raising BOTH brows
                            (the play/stop gesture), which reads ~0 here.
A symmetric expression cancels in the difference, so it won't cross-trigger.
"""

from __future__ import annotations

import math

# Outer eye-corner landmark indices (MediaPipe canonical face mesh).
_EYE_CORNER_A = 33     # image-left eye corner (subject's right eye)
_EYE_CORNER_B = 263    # image-right eye corner (subject's left eye)
# Roll angle (radians) that maps to a full-scale (1.0) head tilt.
_MAX_TILT_RAD = 0.50   # ~28 degrees
# Pitch / yaw angles (radians) that map to full-scale look-up / turn.
_MAX_PITCH_RAD = 0.45  # ~26 degrees
_MAX_YAW_RAD = 0.55    # ~31 degrees


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def head_tilt(landmarks) -> dict[str, float]:
    """Head roll from the eye-line angle -> {tiltLeft, tiltRight} in 0..1.

    Upright eyes are horizontal (angle ~0). Tilting the head ear-to-shoulder
    rotates the eye line; positive angle (in image coords, y-down) is treated as
    a LEFT tilt. If it reads backwards in practice, swap the two gesture
    assignments in gestures.json (or flip the sign here).
    """
    if not landmarks or len(landmarks) <= _EYE_CORNER_B:
        return {}
    ax, ay = landmarks[_EYE_CORNER_A]
    bx, by = landmarks[_EYE_CORNER_B]
    angle = math.atan2(by - ay, bx - ax)  # ~0 when upright
    mag = _clamp01(abs(angle) / _MAX_TILT_RAD)
    if angle >= 0:
        return {"tiltLeft": mag, "tiltRight": 0.0}
    return {"tiltLeft": 0.0, "tiltRight": mag}


def head_pose(matrix) -> dict[str, float]:
    """Head pitch/yaw from the 4x4 facial transformation matrix.

    Returns lookUp/lookDown/turnLeft/turnRight in 0..1. Sign conventions are
    assumptions verified by live testing — flip here if a direction is reversed.
    """
    if matrix is None:
        return {}
    # Upper-left 3x3 rotation block (matrix is a 4x4 numpy array).
    r10, r00 = float(matrix[1][0]), float(matrix[0][0])
    r20, r21, r22 = float(matrix[2][0]), float(matrix[2][1]), float(matrix[2][2])
    pitch = math.atan2(r21, r22)
    yaw = math.atan2(-r20, math.hypot(r21, r22))
    up = _clamp01(pitch / _MAX_PITCH_RAD)
    down = _clamp01(-pitch / _MAX_PITCH_RAD)
    left = _clamp01(yaw / _MAX_YAW_RAD)
    right = _clamp01(-yaw / _MAX_YAW_RAD)
    return {"lookUp": up, "lookDown": down, "turnLeft": left, "turnRight": right}


def augment(scores: dict[str, float], landmarks=None, matrix=None) -> dict[str, float]:
    """Add derived channels to a blendshape score dict in place; returns it.

    If landmarks/matrix are provided, head-tilt and head-pose channels are added.
    """
    if not scores:
        return scores
    bl = scores.get("eyeBlinkLeft", 0.0)
    br = scores.get("eyeBlinkRight", 0.0)
    scores["winkLeft"] = _clamp01(bl - br)   # subject's left eye closed, right open
    scores["winkRight"] = _clamp01(br - bl)  # subject's right eye closed, left open

    # One eyebrow raised vs. raising both. browInnerUp is the both-brow signal
    # used for play/stop; these outer-brow differentials isolate a single brow.
    obl = scores.get("browOuterUpLeft", 0.0)
    obr = scores.get("browOuterUpRight", 0.0)
    scores["browUpLeft"] = _clamp01(obl - obr)   # only the left brow up
    scores["browUpRight"] = _clamp01(obr - obl)  # only the right brow up

    # Combined smile (both corners), robust to a one-sided smirk.
    sl = scores.get("mouthSmileLeft", 0.0)
    sr = scores.get("mouthSmileRight", 0.0)
    scores["smile"] = _clamp01((sl + sr) / 2.0)

    if landmarks is not None:
        scores.update(head_tilt(landmarks))
    if matrix is not None:
        scores.update(head_pose(matrix))
    return scores
