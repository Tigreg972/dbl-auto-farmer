from __future__ import annotations

from dataclasses import dataclass

from dbl_farmer.models import Objective, ObjectiveKind, ScreenState


@dataclass(frozen=True)
class NavigationAction:
    name: str
    expected_states: tuple[ScreenState, ...] = ()


class NavigationRouter:
    def action_for(self, state: ScreenState, objective: Objective | None) -> NavigationAction:
        if state is ScreenState.HOME:
            if objective is None:
                return NavigationAction("IDLE")
            if objective.kind is ObjectiveKind.STORY:
                return NavigationAction("OPEN_STORY", (ScreenState.STORY_MENU, ScreenState.STAGE_LIST))
            return NavigationAction("OPEN_EVENTS", (ScreenState.EVENT_MENU, ScreenState.STAGE_LIST))

        mapping: dict[ScreenState, NavigationAction] = {
            ScreenState.STORY_MENU: NavigationAction("OPEN_STAGE_LIST", (ScreenState.STAGE_LIST,)),
            ScreenState.EVENT_MENU: NavigationAction("OPEN_STAGE_LIST", (ScreenState.STAGE_LIST,)),
            ScreenState.STAGE_LIST: NavigationAction("SELECT_STAGE", (ScreenState.STAGE_DETAILS, ScreenState.PRE_BATTLE)),
            ScreenState.STAGE_DETAILS: NavigationAction("OPEN_PRE_BATTLE", (ScreenState.PRE_BATTLE,)),
            ScreenState.PRE_BATTLE: NavigationAction("PREPARE_STAGE", (ScreenState.SKIP_TICKET_POPUP, ScreenState.TEAM_SELECTION)),
            ScreenState.SKIP_TICKET_POPUP: NavigationAction("CONFIRM_SKIP", (ScreenState.RESULTS, ScreenState.REWARD_POPUP)),
            ScreenState.TEAM_SELECTION: NavigationAction("START_BATTLE", (ScreenState.BATTLE,)),
            ScreenState.EQUIPMENT_SELECTION: NavigationAction("CONFIRM_EQUIPMENT", (ScreenState.TEAM_SELECTION,)),
            ScreenState.BATTLE: NavigationAction("WAIT_FOR_RESULT", (ScreenState.RESULTS,)),
            ScreenState.RESULTS: NavigationAction("CONTINUE_RESULTS", (ScreenState.REWARD_POPUP, ScreenState.STAGE_LIST)),
            ScreenState.REWARD_POPUP: NavigationAction("CLOSE_REWARD", (ScreenState.STAGE_LIST, ScreenState.RESULTS)),
            ScreenState.ERROR_POPUP: NavigationAction("CLOSE_ERROR"),
            ScreenState.UNKNOWN: NavigationAction("RECOVER"),
        }
        return mapping.get(state, NavigationAction("RECOVER"))
