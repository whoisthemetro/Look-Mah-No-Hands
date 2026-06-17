"""Deterministic tests for GestureClassifier (run directly: no pytest needed).

    detector/.venv/bin/python detector/test_classifier.py
"""

from __future__ import annotations

from classifier import GestureClassifier
from gestures_config import Gesture, GestureConfig, Settings

FPS_STEP = 33  # ms per frame (~30fps)


def make_cfg(gestures, single_active=True, global_lockout_ms=350):
    return GestureConfig(
        settings=Settings(global_lockout_ms=global_lockout_ms, single_active=single_active),
        gestures=gestures,
    )


def brow(**kw):
    d = dict(name="play_stop", blendshape="browInnerUp", threshold=0.45,
             release=0.25, hold_ms=450, cooldown_ms=1000, osc="/transport/playstop")
    d.update(kw)
    return Gesture(**d)


def jaw(**kw):
    d = dict(name="return", blendshape="jawOpen", threshold=0.45,
             release=0.20, hold_ms=450, cooldown_ms=1000, osc="/transport/return")
    d.update(kw)
    return Gesture(**d)


def run(clf, segments):
    """segments: list of (duration_ms, {blendshape: value}). Returns all fires."""
    fires = []
    t = 0
    for duration, scores in segments:
        end = t + duration
        while t < end:
            fires.extend(clf.update(scores, t))
            t += FPS_STEP
    return fires


def names(fires):
    return [f.name for f in fires]


def check(label, cond):
    print(f"  {'PASS' if cond else 'FAIL'}  {label}")
    assert cond, label


def test_brief_spike_no_fire():
    clf = GestureClassifier(make_cfg([brow()]))
    fires = run(clf, [(300, {"browInnerUp": 0.8}), (300, {"browInnerUp": 0.0})])
    check("brief 300ms spike (<450 hold) does not fire", names(fires) == [])


def test_sustained_fires_once():
    clf = GestureClassifier(make_cfg([brow()]))
    fires = run(clf, [(700, {"browInnerUp": 0.8})])
    check("sustained hold fires exactly once", names(fires) == ["play_stop"])


def test_held_does_not_repeat():
    clf = GestureClassifier(make_cfg([brow()]))
    fires = run(clf, [(3000, {"browInnerUp": 0.8})])
    check("continuous 3s hold fires only once (armed gate)", names(fires) == ["play_stop"])


def test_refire_after_release_and_cooldown():
    clf = GestureClassifier(make_cfg([brow()]))
    fires = run(clf, [
        (700, {"browInnerUp": 0.8}),   # fire 1
        (1300, {"browInnerUp": 0.0}),  # relax (re-arm) + let cooldown pass
        (700, {"browInnerUp": 0.8}),   # fire 2
    ])
    check("re-fires after relaxing and cooldown", names(fires) == ["play_stop", "play_stop"])


def test_hysteresis_blocks_chatter():
    # Value sits between release(0.25) and threshold(0.45) after one fire:
    # should NOT re-arm (never drops below release) -> no second fire.
    clf = GestureClassifier(make_cfg([brow()]))
    fires = run(clf, [
        (700, {"browInnerUp": 0.8}),   # fire 1
        (2000, {"browInnerUp": 0.35}), # hovers above release, below threshold
        (700, {"browInnerUp": 0.8}),   # back up, but never re-armed
    ])
    check("no re-arm without dropping below release", names(fires) == ["play_stop"])


def test_cooldown_enforced():
    clf = GestureClassifier(make_cfg([brow(cooldown_ms=2000)]))
    # fire1 ~462ms; cooldown 2000 -> next allowed ~2462ms. Keep the whole
    # timeline under that so the second hold is blocked purely by cooldown.
    fires = run(clf, [
        (700, {"browInnerUp": 0.8}),   # fire 1 (~462ms)
        (300, {"browInnerUp": 0.0}),   # quick relax to re-arm (ends 1000ms)
        (1000, {"browInnerUp": 0.8}),  # held >hold_ms but ends 2000ms < cooldown end
    ])
    check("cooldown blocks early second fire", names(fires) == ["play_stop"])


def test_single_active_blocks_overlap():
    clf = GestureClassifier(make_cfg([brow(), jaw()], single_active=True))
    # Both faces high at once for 600ms: only the first to own the floor fires
    # in that window (the other is blocked from counting).
    fires = run(clf, [(600, {"browInnerUp": 0.8, "jawOpen": 0.8})])
    check("single_active: only one fire while overlapping", names(fires) == ["play_stop"])


def test_no_face_resets():
    clf = GestureClassifier(make_cfg([brow()]))
    fires = run(clf, [
        (300, {"browInnerUp": 0.8}),   # partial hold
        (200, {}),                     # face lost -> counting resets, re-arms
        (300, {"browInnerUp": 0.8}),   # only 300ms again -> still no fire
    ])
    check("losing the face resets the hold timer", names(fires) == [])


def main():
    tests = [
        test_brief_spike_no_fire,
        test_sustained_fires_once,
        test_held_does_not_repeat,
        test_refire_after_release_and_cooldown,
        test_hysteresis_blocks_chatter,
        test_cooldown_enforced,
        test_single_active_blocks_overlap,
        test_no_face_resets,
    ]
    print(f"Running {len(tests)} classifier tests...")
    for t in tests:
        t()
    print("All classifier tests passed.")


if __name__ == "__main__":
    main()
