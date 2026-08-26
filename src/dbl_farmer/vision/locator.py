from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass(frozen=True)
class TemplateMatch:
    confidence: float
    center: tuple[int, int]
    rect: tuple[int, int, int, int]


class TemplateLocator:
    def find(
        self,
        frame: object,
        template_path: str | Path,
        threshold: float = 0.78,
    ) -> TemplateMatch | None:
        path = Path(template_path)
        if not path.exists() or not isinstance(frame, np.ndarray):
            return None

        template = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if template is None:
            return None

        source = frame
        if source.ndim == 2:
            source_bgr = cv2.cvtColor(source, cv2.COLOR_GRAY2BGR)
        elif source.shape[-1] == 4:
            source_bgr = cv2.cvtColor(source, cv2.COLOR_RGBA2BGR)
        else:
            source_bgr = cv2.cvtColor(source, cv2.COLOR_RGB2BGR)

        sh, sw = source_bgr.shape[:2]
        th, tw = template.shape[:2]
        if th > sh or tw > sw:
            return None

        result = cv2.matchTemplate(source_bgr, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        confidence = float(max_val)
        if confidence < threshold:
            return None

        x, y = int(max_loc[0]), int(max_loc[1])
        return TemplateMatch(
            confidence=confidence,
            center=(x + tw // 2, y + th // 2),
            rect=(x, y, tw, th),
        )
