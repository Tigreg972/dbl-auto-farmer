from __future__ import annotations

from dataclasses import dataclass

from dbl_farmer.models import ScreenState


@dataclass(frozen=True)
class Cue:
    name: str
    template_path: str
    weight: float
    required: bool = False


@dataclass(frozen=True)
class StateDefinition:
    state: ScreenState
    cues: tuple[Cue, ...]
    threshold: float


def default_state_definitions(base: str = "assets/templates") -> tuple[StateDefinition, ...]:
    groups = {
        "home_logo": "home",
        "story_button": "home",
        "event_button": "home",
        "story_title": "story",
        "continue_button": "story",
        "event_title": "event",
        "event_tabs": "event",
        "stage_list_marker": "stage_list",
        "stage_card": "stage_list",
        "start_battle": "pre_battle",
        "energy_cost": "pre_battle",
        "team_selection": "team",
        "ready_button": "team",
        "auto_battle": "battle",
        "battle_hud": "battle",
        "result_title": "results",
        "result_ok": "results",
        "energy_popup": "popup",
        "energy_confirm": "popup",
        "skip_ticket_popup": "popup",
        "skip_confirm": "popup",
        "reward_popup": "popup",
        "reward_ok": "popup",
        "error_popup": "popup",
        "error_ok": "popup",
    }

    def cue(name: str, weight: float = 1.0, required: bool = False) -> Cue:
        group = groups[name]
        return Cue(name=name, template_path=f"{base}/{group}/{name}.png", weight=weight, required=required)

    return (
        StateDefinition(ScreenState.HOME, (cue("home_logo", .5), cue("story_button", .25), cue("event_button", .25)), .78),
        StateDefinition(ScreenState.STORY_MENU, (cue("story_title", .6), cue("continue_button", .4)), .78),
        StateDefinition(ScreenState.EVENT_MENU, (cue("event_title", .6), cue("event_tabs", .4)), .78),
        StateDefinition(ScreenState.STAGE_LIST, (cue("stage_list_marker", .6), cue("stage_card", .4)), .78),
        StateDefinition(ScreenState.PRE_BATTLE, (cue("start_battle", .6, True), cue("energy_cost", .4)), .78),
        StateDefinition(ScreenState.TEAM_SELECTION, (cue("team_selection", .6), cue("ready_button", .4, True)), .78),
        StateDefinition(ScreenState.BATTLE, (cue("auto_battle", .7), cue("battle_hud", .3)), .78),
        StateDefinition(ScreenState.RESULTS, (cue("result_title", .6), cue("result_ok", .4)), .78),
        StateDefinition(ScreenState.ENERGY_POPUP, (cue("energy_popup", .7), cue("energy_confirm", .3)), .78),
        StateDefinition(ScreenState.SKIP_TICKET_POPUP, (cue("skip_ticket_popup", .7), cue("skip_confirm", .3)), .78),
        StateDefinition(ScreenState.REWARD_POPUP, (cue("reward_popup", .7), cue("reward_ok", .3)), .78),
        StateDefinition(ScreenState.ERROR_POPUP, (cue("error_popup", .7), cue("error_ok", .3)), .78),
    )
