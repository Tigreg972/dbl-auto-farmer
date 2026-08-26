from __future__ import annotations

from collections.abc import Callable

from dbl_farmer.vision.window import WindowBounds


class SafeClicker:
    def __init__(self, click_fn: Callable[[int, int], None]):
        self._click_fn = click_fn

    def click_relative(
        self,
        bounds: WindowBounds,
        x_ratio: float,
        y_ratio: float,
    ) -> tuple[int, int]:
        if not (0.0 <= x_ratio <= 1.0 and 0.0 <= y_ratio <= 1.0):
            raise ValueError("Relative click ratios must be between 0 and 1")

        x = bounds.left + int(bounds.width * x_ratio)
        y = bounds.top + int(bounds.height * y_ratio)
        return self.click_point(bounds, x, y)

    def click_point(
        self,
        bounds: WindowBounds,
        x: int,
        y: int,
    ) -> tuple[int, int]:
        if not (bounds.left <= x < bounds.right and bounds.top <= y < bounds.bottom):
            raise ValueError(
                f"Refusing click outside BlueStacks window: ({x}, {y}) not in {bounds}"
            )

        self._click_fn(x, y)
        return x, y
