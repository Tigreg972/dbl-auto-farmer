import pytest

from dbl_farmer.input.clicker import SafeClicker
from dbl_farmer.vision.window import WindowBounds


def test_relative_click_is_offset_by_window_origin():
    clicks = []
    clicker = SafeClicker(click_fn=lambda x, y: clicks.append((x, y)))
    bounds = WindowBounds(left=1920, top=0, width=1440, height=900)

    point = clicker.click_relative(bounds, 0.5, 0.5)

    assert point == (2640, 450)
    assert clicks == [(2640, 450)]


def test_click_outside_window_is_rejected():
    clicker = SafeClicker(click_fn=lambda *_: None)
    bounds = WindowBounds(left=0, top=0, width=100, height=100)

    with pytest.raises(ValueError):
        clicker.click_point(bounds, 120, 50)
