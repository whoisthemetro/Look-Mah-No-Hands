"""Load and validate the gesture map (gestures.json).

Turns the JSON into typed Gesture objects so the classifier and detector deal
with attributes, not dict lookups, and bad configs fail loudly at startup.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import config


@dataclass(frozen=True)
class Gesture:
    name: str
    blendshape: str
    threshold: float
    release: float
    hold_ms: int
    cooldown_ms: int
    osc: str

    def __post_init__(self):
        if not (0.0 < self.threshold <= 1.0):
            raise ValueError(f"{self.name}: threshold must be in (0, 1]")
        if not (0.0 <= self.release < self.threshold):
            raise ValueError(f"{self.name}: release must be in [0, threshold)")
        if self.hold_ms < 0 or self.cooldown_ms < 0:
            raise ValueError(f"{self.name}: hold_ms/cooldown_ms must be >= 0")


@dataclass(frozen=True)
class Settings:
    global_lockout_ms: int = 350
    single_active: bool = True


@dataclass(frozen=True)
class GestureConfig:
    settings: Settings
    gestures: list[Gesture]


def load(path: Path = config.GESTURE_CONFIG) -> GestureConfig:
    if not path.exists():
        raise FileNotFoundError(f"Gesture config not found at {path}")
    raw = json.loads(path.read_text())

    s = raw.get("settings", {})
    settings = Settings(
        global_lockout_ms=int(s.get("global_lockout_ms", 350)),
        single_active=bool(s.get("single_active", True)),
    )

    gestures: list[Gesture] = []
    names = set()
    for g in raw.get("gestures", []):
        gesture = Gesture(
            name=g["name"],
            blendshape=g["blendshape"],
            threshold=float(g["threshold"]),
            release=float(g["release"]),
            hold_ms=int(g["hold_ms"]),
            cooldown_ms=int(g["cooldown_ms"]),
            osc=g["osc"],
        )
        if gesture.name in names:
            raise ValueError(f"duplicate gesture name: {gesture.name}")
        names.add(gesture.name)
        gestures.append(gesture)

    if not gestures:
        raise ValueError("gestures.json defines no gestures")
    return GestureConfig(settings=settings, gestures=gestures)
