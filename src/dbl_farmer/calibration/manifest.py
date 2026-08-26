from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TemplateSpec:
    path: str
    description: str
    required: bool = True


_DESCRIPTIONS: dict[str, tuple[str, bool]] = {
    "home/home_logo.png": ("Stable home-screen marker (logo/header element)", True),
    "home/story_button.png": ("Story button on the home screen", True),
    "home/event_button.png": ("Events button on the home screen", True),
    "story/story_title.png": ("Stable Story screen title/header", True),
    "story/continue_button.png": ("Continue button in Story", True),
    "event/event_title.png": ("Stable Events screen title/header", True),
    "event/event_tabs.png": ("Stable event category tabs", True),
    "event/unfinished_event.png": ("Marker/card for an unfinished event", True),
    "event/event_card.png": ("Generic event card fallback", False),
    "stage_list/stage_list_marker.png": ("Stable marker proving the stage list is open", True),
    "stage_list/stage_card.png": ("Generic selectable stage card", True),
    "stage_list/unfinished_stage.png": ("Marker/card for an unfinished stage", True),
    "stage_list/next_stage.png": ("Next/new stage marker fallback", False),
    "stage_list/start_stage.png": ("Button that opens a selected stage", False),
    "pre_battle/start_battle.png": ("Start Battle button", True),
    "pre_battle/energy_cost.png": ("Energy cost area on pre-battle screen", True),
    "pre_battle/skip_ticket_button.png": ("Skip Ticket button when usable", False),
    "pre_battle/skip_confirm.png": ("Skip confirmation inside pre-battle flow", False),
    "team/team_selection.png": ("Stable marker on team selection screen", True),
    "team/ready_button.png": ("Ready button", True),
    "team/auto_select_button.png": ("Auto Select team button", False),
    "team/recommended_button.png": ("Recommended/Best team button", False),
    "team/equipment_selection.png": ("Stable marker on the equipment selection screen", False),
    "team/equipment_auto_button.png": ("Auto/Recommended equipment button", False),
    "team/equipment_confirm.png": ("Equipment confirmation button", False),
    "battle/battle_hud.png": ("Stable battle HUD marker", True),
    "battle/auto_battle.png": ("AUTO indicator while battle is active", True),
    "battle/auto_off.png": ("AUTO button while auto battle is OFF", False),
    "results/result_title.png": ("Victory/results title marker", True),
    "results/result_ok.png": ("OK button on results screen", True),
    "results/next_button.png": ("Next/Continue button after results", True),
    "results/tap_continue.png": ("Tap-to-continue prompt after results", False),
    "results/defeat_marker.png": ("Defeat marker", True),
    "results/rematch_button.png": ("Rematch button after defeat", True),
    "results/quit_button.png": ("Quit/Back button used after three defeats", False),
    "popup/energy_popup.png": ("Energy shortage/refill popup marker", True),
    "popup/energy_confirm.png": ("Safe energy refill confirmation", False),
    "popup/energy_item.png": ("Energy-restoration item marker", False),
    "popup/energy_item_confirm.png": ("Confirm use of an energy item", False),
    "popup/chrono_crystal.png": ("Chrono Crystal/premium refill marker — detection only", True),
    "popup/premium_refill.png": ("Alternative premium refill marker — detection only", False),
    "popup/skip_ticket_popup.png": ("Skip Ticket popup marker", False),
    "popup/skip_confirm.png": ("Confirm Skip Ticket use", False),
    "popup/reward_popup.png": ("Reward popup marker", True),
    "popup/reward_ok.png": ("Reward popup OK/Close button", True),
    "popup/error_popup.png": ("Generic error popup marker", True),
    "popup/error_ok.png": ("Generic error popup OK button", True),
    "popup/cancel.png": ("Cancel button, especially for premium refill prompts", True),
    "navigation/back_button.png": ("In-game Back button", True),
    "navigation/home_button.png": ("In-game Home button", True),
}


def template_specs() -> tuple[TemplateSpec, ...]:
    return tuple(
        TemplateSpec(path=path, description=description, required=required)
        for path, (description, required) in sorted(_DESCRIPTIONS.items())
    )


def missing_templates(root: str | Path, *, required_only: bool = False) -> list[TemplateSpec]:
    base = Path(root)
    return [
        spec
        for spec in template_specs()
        if (not required_only or spec.required) and not (base / spec.path).exists()
    ]
