"""Turn a stream of blendshape scores into debounced gesture fire events.

Anti-false-trigger design (each gesture, independently):
  * threshold / release hysteresis  -- must cross UP past threshold, and fall
    below the lower release line before it can fire again (no chatter).
  * hold_ms                         -- must stay above threshold this long
    before firing (rejects momentary expressions).
  * cooldown_ms                     -- minimum gap between fires of the gesture.
  * armed flag                      -- a single hold fires exactly once; you
    must relax below release to re-arm (no machine-gun repeats while held).

Across gestures:
  * global_lockout_ms  -- after ANY fire, suppress all gestures briefly.
  * single_active      -- only one gesture may be counting toward a fire at a
    time, so overlapping faces can't both trigger.

The clock is passed in (now_ms) so behaviour is deterministic and testable.
"""

from __future__ import annotations

from dataclasses import dataclass

from gestures_config import Gesture, GestureConfig


@dataclass(frozen=True)
class FireEvent:
    name: str
    osc: str
    value: float
    held_ms: int


@dataclass
class _State:
    counting_since: int | None = None  # when value first crossed threshold
    last_fire_ms: int = -10**9         # for cooldown
    armed: bool = True                 # must relax below release to re-arm


@dataclass
class GestureStatus:
    value: float = 0.0
    progress: float = 0.0       # 0..1 toward hold_ms while counting
    armed: bool = True
    cooling_ms: int = 0         # remaining cooldown, else 0


class GestureClassifier:
    def __init__(self, cfg: GestureConfig):
        self.cfg = cfg
        self._state: dict[str, _State] = {g.name: _State() for g in cfg.gestures}
        self._last_any_fire_ms = -10**9
        self._active: str | None = None  # name of the gesture currently counting
        self.status: dict[str, GestureStatus] = {
            g.name: GestureStatus(armed=True) for g in cfg.gestures
        }

    def update(self, scores: dict[str, float], now_ms: int) -> list[FireEvent]:
        events: list[FireEvent] = []
        global_locked = (now_ms - self._last_any_fire_ms) < self.cfg.settings.global_lockout_ms

        for g in self.cfg.gestures:
            st = self._state[g.name]
            v = scores.get(g.blendshape, 0.0)

            # Re-arm once the face relaxes below the release line.
            if v < g.release:
                st.armed = True

            fired = self._step(g, st, v, now_ms, global_locked)
            if fired is not None:
                events.append(fired)
                global_locked = True  # a fire this frame locks out the rest

            self._update_status(g, st, v, now_ms)

        return events

    def _step(self, g: Gesture, st: _State, v: float, now_ms: int,
              global_locked: bool) -> FireEvent | None:
        if v < g.threshold:
            # Below threshold: not counting; release the floor if we held it.
            st.counting_since = None
            if self._active == g.name:
                self._active = None
            return None

        # At/above threshold.
        if not st.armed:
            st.counting_since = None
            if self._active == g.name:
                self._active = None
            return None

        if self.cfg.settings.single_active and self._active not in (None, g.name):
            # Another gesture owns the floor.
            st.counting_since = None
            return None

        if st.counting_since is None:
            st.counting_since = now_ms
            if self.cfg.settings.single_active:
                self._active = g.name

        held = now_ms - st.counting_since
        cooled = (now_ms - st.last_fire_ms) >= g.cooldown_ms
        if held >= g.hold_ms and cooled and not global_locked:
            st.last_fire_ms = now_ms
            self._last_any_fire_ms = now_ms
            st.armed = False
            st.counting_since = None
            if self._active == g.name:
                self._active = None
            return FireEvent(name=g.name, osc=g.osc, value=v, held_ms=held)
        return None

    def _update_status(self, g: Gesture, st: _State, v: float, now_ms: int):
        progress = 0.0
        if st.counting_since is not None and g.hold_ms > 0:
            progress = min(1.0, (now_ms - st.counting_since) / g.hold_ms)
        cooling = max(0, g.cooldown_ms - (now_ms - st.last_fire_ms))
        self.status[g.name] = GestureStatus(
            value=v, progress=progress, armed=st.armed, cooling_ms=cooling
        )
