from pathlib import Path

import cv2
import numpy as np

from dbl_farmer.vision.locator import TemplateLocator


def _pattern() -> np.ndarray:
    template = np.zeros((12, 14, 3), dtype=np.uint8)
    template[1:5, 1:4] = (255, 255, 255)
    template[6:10, 8:13] = (80, 180, 240)
    template[3:11, 6:8] = (10, 90, 200)
    return template


def test_locator_returns_center_of_best_template_match(tmp_path: Path):
    template = _pattern()
    template_path = tmp_path / "button.png"
    assert cv2.imwrite(str(template_path), template)

    frame_bgr = np.zeros((80, 100, 3), dtype=np.uint8)
    frame_bgr[30:42, 40:54] = template
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

    match = TemplateLocator().find(frame_rgb, template_path, threshold=0.8)

    assert match is not None
    assert match.center == (47, 36)
    assert match.confidence >= 0.99


def test_locator_returns_none_when_template_is_missing(tmp_path: Path):
    frame = np.zeros((40, 40, 3), dtype=np.uint8)

    match = TemplateLocator().find(frame, tmp_path / "missing.png", threshold=0.8)

    assert match is None
