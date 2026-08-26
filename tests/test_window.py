import pytest

from dbl_farmer.vision.window import BlueStacksWindowResolver, WindowNotFoundError


class FakeWindow:
    def __init__(self, title, left, top, width, height):
        self.title = title
        self.left = left
        self.top = top
        self.width = width
        self.height = height


def test_resolver_matches_title_substring_on_second_monitor():
    windows = [FakeWindow("BlueStacks App Player 1", 1920, 0, 1440, 900)]
    resolver = BlueStacksWindowResolver(window_provider=lambda: windows)

    bounds = resolver.find("BlueStacks App Player")

    assert (bounds.left, bounds.top, bounds.width, bounds.height) == (1920, 0, 1440, 900)


def test_resolver_rejects_minimized_window_and_lists_titles():
    windows = [
        FakeWindow("BlueStacks App Player 1", 0, 0, 0, 0),
        FakeWindow("Discord", 100, 100, 800, 600),
    ]
    resolver = BlueStacksWindowResolver(window_provider=lambda: windows)

    with pytest.raises(WindowNotFoundError) as exc:
        resolver.find("BlueStacks App Player")

    assert "BlueStacks App Player 1" in str(exc.value)
    assert "Discord" in str(exc.value)
