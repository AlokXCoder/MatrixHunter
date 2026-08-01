"""
settings.py
===========
Settings dataclass — loaded from / saved to data/settings.json.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict, field
from typing import Tuple

from config import (
    SETTINGS_FILE, DATA_DIR,
    Difficulty, SCREEN_WIDTH, SCREEN_HEIGHT,
)


@dataclass
class Settings:
    """All user-configurable game settings with JSON persistence."""

    master_volume : float = 0.70
    music_volume  : float = 0.50
    sfx_volume    : float = 0.80
    fullscreen    : bool  = False
    resolution    : Tuple[int, int] = field(default_factory=lambda: (SCREEN_WIDTH, SCREEN_HEIGHT))
    difficulty    : str   = Difficulty.NORMAL.value
    show_fps      : bool  = True
    screen_shake  : bool  = True
    particles     : bool  = True

    # ── persistence ──────────────────────────────────────────────

    @classmethod
    def load(cls) -> "Settings":
        """Return a Settings instance from disk, or defaults if file missing/corrupt."""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as fh:
                    raw = json.load(fh)
                instance = cls()
                for key, val in raw.items():
                    if hasattr(instance, key):
                        if key == "resolution":
                            val = tuple(val)
                        setattr(instance, key, val)
                return instance
            except (json.JSONDecodeError, KeyError, TypeError):
                pass          # fall through to defaults
        return cls()

    def save(self) -> None:
        """Persist current settings to disk."""
        os.makedirs(DATA_DIR, exist_ok=True)
        data = asdict(self)
        data["resolution"] = list(data["resolution"])   # JSON-serialisable
        with open(SETTINGS_FILE, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    # ── helpers ──────────────────────────────────────────────────

    @property
    def effective_music(self) -> float:
        """Clamped combined volume for background music."""
        return max(0.0, min(1.0, self.music_volume * self.master_volume))

    @property
    def effective_sfx(self) -> float:
        """Clamped combined volume for sound effects."""
        return max(0.0, min(1.0, self.sfx_volume * self.master_volume))

    def cycle_difficulty(self) -> None:
        """Rotate through Easy → Normal → Hard → Easy."""
        levels = [d.value for d in Difficulty]
        idx = levels.index(self.difficulty) if self.difficulty in levels else 1
        self.difficulty = levels[(idx + 1) % len(levels)]

    def cycle_resolution(self, resolutions: list[Tuple[int, int]]) -> None:
        """Advance to the next available resolution option."""
        try:
            idx = resolutions.index(tuple(self.resolution))
        except ValueError:
            idx = 0
        self.resolution = resolutions[(idx + 1) % len(resolutions)]
