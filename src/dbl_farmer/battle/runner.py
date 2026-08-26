from __future__ import annotations

from collections import defaultdict

from dbl_farmer.models import BattleOutcome, ObjectiveStatus


class BattleRunner:
    def __init__(self, max_defeats: int = 3):
        if max_defeats < 1:
            raise ValueError("max_defeats must be at least 1")
        self._max_defeats = max_defeats
        self._defeats: dict[str, int] = defaultdict(int)

    def record_outcome(self, objective_id: str, outcome: BattleOutcome) -> ObjectiveStatus:
        if outcome is BattleOutcome.VICTORY:
            self._defeats[objective_id] = 0
            return ObjectiveStatus.COMPLETED

        if outcome is BattleOutcome.DEFEAT:
            self._defeats[objective_id] += 1
            if self._defeats[objective_id] >= self._max_defeats:
                return ObjectiveStatus.BLOCKED
            return ObjectiveStatus.ACTIVE

        return ObjectiveStatus.ACTIVE

    def defeats_for(self, objective_id: str) -> int:
        return self._defeats.get(objective_id, 0)
