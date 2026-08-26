from __future__ import annotations

from dataclasses import replace

from dbl_farmer.models import Objective, ObjectiveKind, ObjectiveStatus


class ObjectiveQueue:
    def __init__(self, objectives: list[Objective]):
        self._objectives = list(objectives)
        self._blocked_team_signatures: dict[str, str] = {}

    def next(self) -> Objective | None:
        eligible = [obj for obj in self._objectives if self._is_eligible(obj)]
        if not eligible:
            return None
        return min(eligible, key=self._priority_key)

    def mark_completed(self, objective_id: str) -> None:
        self._replace_status(objective_id, ObjectiveStatus.COMPLETED)
        self._blocked_team_signatures.pop(objective_id, None)

    def mark_blocked(self, objective_id: str, team_signature: str = "") -> None:
        self._replace_status(objective_id, ObjectiveStatus.BLOCKED)
        self._blocked_team_signatures[objective_id] = team_signature

    def requeue_if_team_changed(self, objective_id: str, team_signature: str) -> None:
        previous = self._blocked_team_signatures.get(objective_id)
        if previous is None or previous == team_signature:
            return
        self._replace_status(objective_id, ObjectiveStatus.PENDING)
        self._blocked_team_signatures.pop(objective_id, None)

    def _replace_status(self, objective_id: str, status: ObjectiveStatus) -> None:
        for index, objective in enumerate(self._objectives):
            if objective.id == objective_id:
                self._objectives[index] = replace(objective, status=status)
                return
        raise KeyError(f"Unknown objective: {objective_id}")

    @staticmethod
    def _is_eligible(objective: Objective) -> bool:
        if objective.status in {ObjectiveStatus.COMPLETED, ObjectiveStatus.BLOCKED}:
            return False
        if objective.kind is ObjectiveKind.PERMANENT and not objective.required_for_progress:
            return False
        return True

    @staticmethod
    def _priority_key(objective: Objective) -> tuple[int, int]:
        if objective.kind is ObjectiveKind.EVENT and objective.limited and objective.first_clear_reward:
            priority = 0
        elif objective.kind is ObjectiveKind.STORY:
            priority = 1
        elif objective.kind is ObjectiveKind.EVENT:
            priority = 2
        else:
            priority = 3
        return priority, 0


def build_default_objectives(*, enable_story: bool = True, enable_events: bool = True) -> ObjectiveQueue:
    objectives: list[Objective] = []
    if enable_story:
        objectives.append(
            Objective(
                id="story-progress",
                kind=ObjectiveKind.STORY,
                label="Story progression",
                first_clear_reward=True,
                required_for_progress=True,
            )
        )
    if enable_events:
        objectives.append(
            Objective(
                id="event-progress",
                kind=ObjectiveKind.EVENT,
                label="Event progression",
                first_clear_reward=True,
                limited=False,
                required_for_progress=True,
            )
        )
    return ObjectiveQueue(objectives)
