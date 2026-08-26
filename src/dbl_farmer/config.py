from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class AppConfig:
    window_title_pattern: str = "BlueStacks App Player"
    detection_threshold: float = 0.78
    soft_recovery_seconds: float = 15.0
    navigation_recovery_seconds: float = 45.0
    max_recovery_failures: int = 3
    max_defeats_per_stage: int = 3
    enable_story: bool = True
    enable_events: bool = True
    allow_energy_items: bool = True
    allow_skip_tickets: bool = True
    allow_chrono_crystals: bool = False
    debug_screenshots: bool = True


def load_config(path: Path) -> AppConfig:
    raw: dict[str, Any] = {}
    if path.exists():
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            raw = loaded

    allowed = {field.name for field in fields(AppConfig)}
    merged = {key: value for key, value in raw.items() if key in allowed}

    # Premium spending is intentionally not configurable in v1.
    merged["allow_chrono_crystals"] = False
    return AppConfig(**merged)
