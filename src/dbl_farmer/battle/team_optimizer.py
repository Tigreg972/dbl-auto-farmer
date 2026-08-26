from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1


@dataclass(frozen=True)
class CharacterCandidate:
    id: str
    tags: set[str]
    element: str
    power_score: float
    boosted: bool
    restricted_out: bool


@dataclass(frozen=True)
class StageRequirements:
    required_tags: set[str]
    enemy_elements: set[str]


@dataclass(frozen=True)
class TeamPlan:
    core: tuple[str, ...]
    bench: tuple[str, ...]
    signature: str


_ADVANTAGE = {
    "RED": "YEL",
    "YEL": "PUR",
    "PUR": "GRN",
    "GRN": "BLU",
    "BLU": "RED",
}


class TeamOptimizer:
    def choose(
        self,
        candidates: list[CharacterCandidate],
        requirements: StageRequirements,
    ) -> TeamPlan:
        eligible = [c for c in candidates if not c.restricted_out]
        if not eligible:
            return TeamPlan(core=(), bench=(), signature=self._signature((), ()))

        if requirements.required_tags:
            required = [
                c for c in eligible
                if requirements.required_tags.issubset(c.tags)
                or bool(requirements.required_tags.intersection(c.tags))
            ]
        else:
            required = eligible

        pool = required if len(required) >= 3 else required + [c for c in eligible if c not in required]
        ranked = sorted(pool, key=lambda c: self._score(c, requirements), reverse=True)
        core_candidates = ranked[:3]
        core_ids = tuple(c.id for c in core_candidates)

        remaining = [c for c in eligible if c.id not in core_ids]
        bench_ranked = sorted(
            remaining,
            key=lambda c: (self._bench_synergy(c, core_candidates), c.power_score, c.id),
            reverse=True,
        )
        bench_ids = tuple(c.id for c in bench_ranked[:3])
        return TeamPlan(core=core_ids, bench=bench_ids, signature=self._signature(core_ids, bench_ids))

    @staticmethod
    def _score(candidate: CharacterCandidate, requirements: StageRequirements) -> tuple[float, float, float, str]:
        boost_score = 1.0 if candidate.boosted else 0.0
        favorable = 1.0 if _ADVANTAGE.get(candidate.element.upper()) in {e.upper() for e in requirements.enemy_elements} else 0.0
        return boost_score, favorable, float(candidate.power_score), candidate.id

    @staticmethod
    def _bench_synergy(candidate: CharacterCandidate, core: list[CharacterCandidate]) -> int:
        return sum(len(candidate.tags.intersection(member.tags)) for member in core)

    @staticmethod
    def _signature(core: tuple[str, ...], bench: tuple[str, ...]) -> str:
        payload = "|".join((*core, "--", *bench)).encode("utf-8")
        return sha1(payload).hexdigest()[:12]
