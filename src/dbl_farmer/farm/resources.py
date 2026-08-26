from __future__ import annotations

from dataclasses import dataclass

from dbl_farmer.models import ResourceDecision


@dataclass(frozen=True)
class ResourceContext:
    skip_eligible: bool
    skip_tickets: int
    energy: int
    energy_cost: int
    energy_items: int
    premium_refill_visible: bool


class ResourceManager:
    _PREMIUM_LABELS = {
        "chrono crystal",
        "chrono crystals",
        "cc",
        "purchase",
        "shop",
    }

    def decide(self, context: ResourceContext) -> ResourceDecision:
        if context.skip_eligible and context.skip_tickets > 0 and context.energy >= context.energy_cost:
            return ResourceDecision.USE_SKIP
        if context.energy >= context.energy_cost:
            return ResourceDecision.RUN_BATTLE
        if context.energy_items > 0:
            return ResourceDecision.USE_ENERGY_ITEM
        return ResourceDecision.STOP_NO_SAFE_ENERGY

    def is_safe_confirmation(self, labels: set[str]) -> bool:
        normalized = {label.strip().casefold() for label in labels}
        return not any(
            premium in label
            for label in normalized
            for premium in self._PREMIUM_LABELS
        )
