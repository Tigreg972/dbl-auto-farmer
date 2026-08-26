from __future__ import annotations

import numpy as np
from PIL import ImageGrab

from .window import WindowBounds


class ScreenCapture:
    def grab(self, bounds: WindowBounds) -> np.ndarray:
        image = ImageGrab.grab(
            bbox=(bounds.left, bounds.top, bounds.right, bounds.bottom),
            all_screens=True,
        )
        return np.asarray(image.convert("RGB"))
