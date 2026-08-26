from pathlib import Path

from dbl_farmer.farm.visual_resources import VisualResourceContextProvider
from dbl_farmer.vision.locator import TemplateMatch


class FakeLocator:
    def __init__(self, visible):
        self.visible = set(visible)

    def find(self, frame, path, threshold):
        key = Path(path).as_posix()
        if any(key.endswith(name) for name in self.visible):
            return TemplateMatch(0.99, (1, 1), (0, 0, 2, 2))
        return None


def test_energy_item_visibility_allows_safe_item_refill(tmp_path: Path):
    provider = VisualResourceContextProvider(
        template_root=tmp_path,
        locator=FakeLocator({"popup/energy_item_confirm.png"}),
    )
    provider.update(object())

    context = provider.current()

    assert context.energy == 0
    assert context.energy_cost == 1
    assert context.energy_items == 1
    assert context.premium_refill_visible is False


def test_chrono_crystal_prompt_is_reported_as_premium(tmp_path: Path):
    provider = VisualResourceContextProvider(
        template_root=tmp_path,
        locator=FakeLocator({"popup/chrono_crystal.png"}),
    )
    provider.update(object())

    context = provider.current()

    assert context.energy_items == 0
    assert context.premium_refill_visible is True
