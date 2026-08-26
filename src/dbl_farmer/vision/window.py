from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Protocol


class WindowLike(Protocol):
    title: str
    left: int
    top: int
    width: int
    height: int


@dataclass(frozen=True)
class WindowBounds:
    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height


class WindowNotFoundError(RuntimeError):
    pass


def _default_window_provider() -> Iterable[WindowLike]:
    import pygetwindow as gw

    return gw.getAllWindows()


class BlueStacksWindowResolver:
    def __init__(self, window_provider: Callable[[], Iterable[WindowLike]] | None = None):
        self._window_provider = window_provider or _default_window_provider

    def find(self, pattern: str) -> WindowBounds:
        windows = list(self._window_provider())
        pattern_lower = pattern.casefold()

        for window in windows:
            title = str(getattr(window, "title", ""))
            width = int(getattr(window, "width", 0))
            height = int(getattr(window, "height", 0))
            if pattern_lower in title.casefold() and width > 0 and height > 0:
                return WindowBounds(
                    left=int(getattr(window, "left", 0)),
                    top=int(getattr(window, "top", 0)),
                    width=width,
                    height=height,
                )

        titles = [str(getattr(window, "title", "")) for window in windows if getattr(window, "title", "")]
        raise WindowNotFoundError(
            f"No visible window matching {pattern!r}. Visible windows: {titles}"
        )
