from __future__ import annotations

from pathlib import Path

from dbl_farmer.farm.resources import ResourceContext
from dbl_farmer.vision.locator import TemplateLocator


class VisualResourceContextProvider:
    def __init__(
        self,
        *,
        template_root: str | Path,
        locator: TemplateLocator | None = None,
        threshold: float = 0.78,
    ) -> None:
        self.template_root = Path(template_root)
        self.locator = locator or TemplateLocator()
        self.threshold = threshold
        self._frame = None

    def update(self, frame: object) -> None:
        self._frame = frame

    def _visible(self, relative_path: str) -> bool:
        if self._frame is None:
            return False
        return self.locator.find(
            self._frame,
            self.template_root / relative_path,
            self.threshold,
        ) is not None

    def current(self) -> ResourceContext:
        energy_item_visible = self._visible("popup/energy_item_confirm.png") or self._visible(
            "popup/energy_item.png"
        )
        premium_visible = self._visible("popup/chrono_crystal.png") or self._visible(
            "popup/premium_refill.png"
        )
        return ResourceContext(
            skip_eligible=False,
            skip_tickets=0,
            energy=0,
            energy_cost=1,
            energy_items=1 if energy_item_visible else 0,
            premium_refill_visible=premium_visible,
        )
