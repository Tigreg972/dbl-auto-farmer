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
        "equipment_selection": "team",
        "equipment_confirm": "team",
        "auto_battle": "battle",
        "auto_off": "battle",
        "battle_hud": "battle",
        "result_title": "results",
        "result_ok": "results",
        "defeat_marker": "results",
        "rematch_button": "results",
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
        # HOME stays detectable if the animated header/logo changes, provided both main
        # navigation buttons are visible.
        StateDefinition(
            ScreenState.HOME,
            (cue("home_logo", .2), cue("story_button", .4), cue("event_button", .4)),
            .65,
        ),
        # The title is the stable screen identity. Continue can legitimately disappear
        # when Story is fully caught up, so it must not be required for recognition.
        StateDefinition(
            ScreenState.STORY_MENU,
            (cue("story_title", .65, True), cue("continue_button", .35)),
            .60,
        ),
        StateDefinition(
            ScreenState.EVENT_MENU,
            (cue("event_title", .65, True), cue("event_tabs", .35)),
            .60,
        ),
        StateDefinition(
            ScreenState.STAGE_LIST,
            (cue("stage_list_marker", .65, True), cue("stage_card", .35)),
            .60,
        ),
        StateDefinition(
            ScreenState.PRE_BATTLE,
            (cue("start_battle", .65, True), cue("energy_cost", .35)),
            .60,
        ),
        StateDefinition(
            ScreenState.TEAM_SELECTION,
            (cue("team_selection", .5), cue("ready_button", .5, True)),
            .50,
        ),
        # Auto may already be ON or still be OFF when the battle screen appears.
        StateDefinition(
            ScreenState.EQUIPMENT_SELECTION,
            (cue("equipment_selection", .45), cue("equipment_confirm", .55, True)),
            .55,
        ),
        StateDefinition(
            ScreenState.BATTLE,
            (cue("battle_hud", .65, True), cue("auto_battle", .35)),
            .60,
        ),
        StateDefinition(
            ScreenState.BATTLE,
            (cue("battle_hud", .65, True), cue("auto_off", .35)),
            .60,
        ),
        StateDefinition(
            ScreenState.RESULTS,
            (cue("result_title", .65, True), cue("result_ok", .35)),
            .60,
        ),
        StateDefinition(
            ScreenState.DEFEAT,
            (cue("defeat_marker", .7, True), cue("rematch_button", .3)),
            .68,
        ),
        StateDefinition(
            ScreenState.ENERGY_POPUP,
            (cue("energy_popup", .7, True), cue("energy_confirm", .3)),
            .68,
        ),
        StateDefinition(
            ScreenState.SKIP_TICKET_POPUP,
            (cue("skip_ticket_popup", .7, True), cue("skip_confirm", .3)),
            .68,
        ),
        StateDefinition(
            ScreenState.REWARD_POPUP,
            (cue("reward_popup", .7, True), cue("reward_ok", .3)),
            .68,
        ),
        StateDefinition(
            ScreenState.ERROR_POPUP,
            (cue("error_popup", .7, True), cue("error_ok", .3)),
            .68,
        ),
    )
