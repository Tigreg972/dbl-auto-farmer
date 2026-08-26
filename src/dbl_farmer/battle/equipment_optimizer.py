from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1

from dbl_farmer.battle.team_optimizer import TeamPlan


@dataclass(frozen=True)
class EquipmentCandidate:
    id: str
    compatible_character_ids: set[str]
    rank_score: float
    stat_score: float


@dataclass(frozen=True)
class EquipmentPlan:
    assignments: dict[str, tuple[str, ...]]
    signature: str


class EquipmentOptimizer:
    def __init__(self, max_per_character: int = 3):
        if max_per_character < 1:
            raise ValueError("max_per_character must be at least 1")
        self.max_per_character = max_per_character

    def choose(self, team: TeamPlan, equipment: list[EquipmentCandidate]) -> EquipmentPlan:
        assignments: dict[str, tuple[str, ...]] = {}
        used: set[str] = set()

        for character_id in team.core:
            compatible = [
                item
                for item in equipment
                if character_id in item.compatible_character_ids and item.id not in used
            ]
            compatible.sort(
                key=lambda item: (item.rank_score, item.stat_score, item.id),
                reverse=True,
            )
            selected = compatible[: self.max_per_character]
            assignments[character_id] = tuple(item.id for item in selected)
            used.update(item.id for item in selected)

        payload = ";".join(
            f"{char}:{','.join(items)}" for char, items in sorted(assignments.items())
        )
        signature = sha1(payload.encode("utf-8")).hexdigest()[:12]
        return EquipmentPlan(assignments=assignments, signature=signature)
