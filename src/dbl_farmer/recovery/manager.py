from __future__ import annotations

from collections import defaultdict
from enum import Enum, auto


class RecoveryLevel(Enum):
    NONE = auto()
    SOFT = auto()
    NAVIGATION = auto()
    HARD = auto()
    BLOCK_OBJECTIVE = auto()


class RecoveryManager:
    def __init__(self, soft_after: float, navigation_after: float, max_failures: int):
        if soft_after <= 0 or navigation_after <= soft_after:
            raise ValueError("Recovery timings must satisfy 0 < soft_after < navigation_after")
        if max_failures < 1:
            raise ValueError("max_failures must be at least 1")
        self.soft_after = soft_after
        self.navigation_after = navigation_after
        self.max_failures = max_failures
        self._last_change: dict[str, float] = {}
        self._failures: dict[str, int] = defaultdict(int)

    def start_objective(self, objective_id: str, now: float) -> None:
        self._last_change[objective_id] = now
        self._failures[objective_id] = 0

    def observe(
        self,
        now: float,
        state_changed: bool,
        recognized: bool,
        objective_id: str,
    ) -> RecoveryLevel:
        if objective_id not in self._last_change:
            self.start_objective(objective_id, now)
            return RecoveryLevel.NONE

        if state_changed:
            self._last_change[objective_id] = now
            return RecoveryLevel.NONE

        elapsed = now - self._last_change[objective_id]
        if elapsed >= self.navigation_after and not recognized:
            return RecoveryLevel.NAVIGATION
        if elapsed >= self.soft_after:
            return RecoveryLevel.SOFT
        return RecoveryLevel.NONE

    def record_failure(self, objective_id: str) -> RecoveryLevel:
        self._failures[objective_id] += 1
        if self._failures[objective_id] >= self.max_failures:
            return RecoveryLevel.BLOCK_OBJECTIVE
        return RecoveryLevel.HARD
