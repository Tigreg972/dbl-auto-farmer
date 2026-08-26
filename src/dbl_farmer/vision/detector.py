from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

import cv2
import numpy as np

from dbl_farmer.models import DetectionResult, ScreenState
from dbl_farmer.vision.states import Cue, StateDefinition

Matcher = Callable[[object, Cue], float]


class ScreenDetector:
    def __init__(
        self,
        definitions: Sequence[StateDefinition],
        matcher: Matcher | None = None,
        required_cue_threshold: float = 0.75,
    ) -> None:
        self._definitions = tuple(definitions)
        self._matcher = matcher or self._opencv_matcher
        self._required_cue_threshold = required_cue_threshold

    def detect(self, frame: object) -> DetectionResult:
        best_state = ScreenState.UNKNOWN
        best_score = 0.0
        best_cues: tuple[str, ...] = ()

        for definition in self._definitions:
            total_weight = sum(cue.weight for cue in definition.cues)
            if total_weight <= 0:
                continue

            matched_names: list[str] = []
            weighted_score = 0.0
            vetoed = False

            for cue in definition.cues:
                score = max(0.0, min(1.0, float(self._matcher(frame, cue))))
                if cue.required and score < self._required_cue_threshold:
                    vetoed = True
                    break
                weighted_score += score * cue.weight
                if score >= self._required_cue_threshold:
                    matched_names.append(cue.name)

            if vetoed:
                continue

            confidence = weighted_score / total_weight
            if confidence >= definition.threshold and confidence > best_score:
                best_state = definition.state
                best_score = confidence
                best_cues = tuple(matched_names)

        return DetectionResult(state=best_state, confidence=best_score, cues=best_cues)

    @staticmethod
    def _opencv_matcher(frame: object, cue: Cue) -> float:
        path = Path(cue.template_path)
        if not path.exists() or not isinstance(frame, np.ndarray):
            return 0.0

        template = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if template is None:
            return 0.0

        source = frame
        if source.ndim == 2:
            source = cv2.cvtColor(source, cv2.COLOR_GRAY2BGR)
        elif source.shape[-1] == 4:
            source = cv2.cvtColor(source, cv2.COLOR_RGBA2BGR)
        elif source.shape[-1] == 3:
            source = cv2.cvtColor(source, cv2.COLOR_RGB2BGR)

        sh, sw = source.shape[:2]
        th, tw = template.shape[:2]
        if th > sh or tw > sw:
            return 0.0

        result = cv2.matchTemplate(source, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        return float(max_val)
