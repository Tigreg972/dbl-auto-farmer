from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class ScreenState(Enum):
    HOME = auto()
    STORY_MENU = auto()
    EVENT_MENU = auto()
    STAGE_LIST = auto()
    STAGE_DETAILS = auto()
    PRE_BATTLE = auto()
    TEAM_SELECTION = auto()
    EQUIPMENT_SELECTION = auto()
    BATTLE = auto()
    RESULTS = auto()
    REWARD_POPUP = auto()
    ENERGY_POPUP = auto()
    SKIP_TICKET_POPUP = auto()
    ERROR_POPUP = auto()
    UNKNOWN = auto()


class ObjectiveKind(Enum):
    LIMITED_EVENT = auto()
    STORY = auto()
    EVENT = auto()
    PERMANENT = auto()


class ObjectiveStatus(Enum):
    PENDING = auto()
    ACTIVE = auto()
    COMPLETED = auto()
    BLOCKED = auto()


@dataclass(frozen=True)
class Objective:
    id: str
    kind: ObjectiveKind
    label: str
    status: ObjectiveStatus = ObjectiveStatus.PENDING
    first_clear_reward: bool = False


@dataclass(frozen=True)
class DetectionResult:
    state: ScreenState
    confidence: float
    cues: tuple[str, ...] = ()


@dataclass(frozen=True)
class ActionResult:
    success: bool
    message: str = ""
    data: Any = None


@dataclass(frozen=True)
class ResourceDecision:
    use_skip_ticket: bool = False
    use_energy_item: bool = False
    stop_reason: str | None = None


class BattleOutcome(Enum):
    VICTORY = auto()
    DEFEAT = auto()
    ABORTED = auto()
    UNKNOWN = auto()
