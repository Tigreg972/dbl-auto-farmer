from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class SessionStats:
    current_state: str = "UNKNOWN"
    current_objective: str = ""
    last_action: str = ""
    energy_used: int = 0
    skip_tickets_used: int = 0
    successful_stages: int = 0
    blocked_stages: int = 0
    current_defeats: int = 0

    @property
    def chrono_crystals_spent(self) -> int:
        return 0


class SessionLogger:
    def __init__(self, log_dir: Path):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
        self.log_path = self.log_dir / f"session_{stamp}.log"
        self.stats = SessionStats()

    def event(self, message: str, **fields) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        suffix = " ".join(f"{key}={value}" for key, value in fields.items())
        line = f"[{timestamp}] {message}"
        if suffix:
            line += f" | {suffix}"
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def summary(self) -> str:
        s = self.stats
        return "\n".join(
            [
                f"Énergie utilisée : {s.energy_used}",
                f"Tickets skip utilisés : {s.skip_tickets_used}",
                f"Niveaux réussis : {s.successful_stages}",
                f"Niveaux bloqués : {s.blocked_stages}",
                f"Chrono Crystals dépensés : {s.chrono_crystals_spent}",
            ]
        )
