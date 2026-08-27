from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from dbl_farmer.input.clicker import SafeClicker
from dbl_farmer.vision.locator import TemplateLocator
from dbl_farmer.vision.window import WindowBounds


@dataclass(frozen=True)
class ActionTarget:
    action: str
    templates: tuple[str, ...]
    threshold: float = 0.78
    optional: bool = False


@dataclass(frozen=True)
class ActionExecution:
    executed: bool
    target: str | None = None
    point: tuple[int, int] | None = None
    passive: bool = False
    message: str = ""
    configured: bool = True


PASSIVE_ACTIONS = {"IDLE", "WAIT_FOR_RESULT", "CONTINUE_WITH_CURRENT_ENERGY", "CALIBRATION_REQUIRED"}


def default_action_targets() -> dict[str, ActionTarget]:
    def target(
        action: str,
        *templates: str,
        threshold: float = 0.78,
        optional: bool = False,
    ) -> ActionTarget:
        return ActionTarget(action, tuple(templates), threshold, optional)

    return {
        "OPEN_STORY": target("OPEN_STORY", "home/story_button.png"),
        "OPEN_EVENTS": target("OPEN_EVENTS", "home/event_button.png"),
        "CONTINUE_STORY": target(
            "CONTINUE_STORY",
            "story/continue_button.png",
        ),
        "OPEN_UNFINISHED_EVENT": target(
            "OPEN_UNFINISHED_EVENT",
            "event/unfinished_event.png",
        ),
        "SELECT_UNFINISHED_STAGE": target(
            "SELECT_UNFINISHED_STAGE",
            "stage_list/unfinished_stage.png",
            "stage_list/next_stage.png",
        ),
        "OPEN_STAGE_LIST": target(
            "OPEN_STAGE_LIST",
            "story/continue_button.png",
            "event/unfinished_event.png",
        ),
        "SELECT_STAGE": target(
            "SELECT_STAGE",
            "stage_list/unfinished_stage.png",
            "stage_list/next_stage.png",
        ),
        "OPEN_PRE_BATTLE": target(
            "OPEN_PRE_BATTLE",
            "stage_list/start_stage.png",
            "stage_list/stage_card.png",
        ),
        "PREPARE_STAGE": target(
            "PREPARE_STAGE",
            "pre_battle/skip_ticket_button.png",
            "pre_battle/start_battle.png",
        ),
        "CONFIRM_SKIP": target(
            "CONFIRM_SKIP",
            "popup/skip_confirm.png",
            "pre_battle/skip_confirm.png",
        ),
        "CONFIRM_ENERGY_ITEM": target(
            "CONFIRM_ENERGY_ITEM",
            "popup/energy_item_confirm.png",
        ),
        "AUTO_CONFIGURE_TEAM": target(
            "AUTO_CONFIGURE_TEAM",
            "team/auto_select_button.png",
            "team/recommended_button.png",
            optional=True,
        ),
        "START_BATTLE": target(
            "START_BATTLE",
            "team/ready_button.png",
        ),
        "ENSURE_AUTO_BATTLE": target(
            "ENSURE_AUTO_BATTLE",
            "battle/auto_off.png",
            optional=True,
        ),
        "AUTO_CONFIGURE_EQUIPMENT": target(
            "AUTO_CONFIGURE_EQUIPMENT",
            "team/equipment_auto_button.png",
            optional=True,
        ),
        "CONFIRM_EQUIPMENT": target(
            "CONFIRM_EQUIPMENT",
            "team/equipment_confirm.png",
            "team/ready_button.png",
        ),
        "RETRY_BATTLE": target(
            "RETRY_BATTLE",
            "results/rematch_button.png",
        ),
        "ABANDON_STAGE": target(
            "ABANDON_STAGE",
            "results/quit_button.png",
            "navigation/back_button.png",
        ),
        "CONTINUE_RESULTS": target(
            "CONTINUE_RESULTS",
            "results/next_button.png",
            "results/result_ok.png",
            "results/tap_continue.png",
        ),
        "CLOSE_REWARD": target(
            "CLOSE_REWARD",
            "popup/reward_ok.png",
            "results/result_ok.png",
        ),
        "CLOSE_ERROR": target(
            "CLOSE_ERROR",
            "popup/error_ok.png",
            "popup/cancel.png",
        ),
        "CANCEL_ENERGY_POPUP": target(
            "CANCEL_ENERGY_POPUP",
            "popup/cancel.png",
            "navigation/back_button.png",
        ),
        "CANCEL_PREMIUM_REFILL": target(
            "CANCEL_PREMIUM_REFILL",
            "popup/cancel.png",
            "navigation/back_button.png",
        ),
        "RECOVER": target(
            "RECOVER",
            "popup/cancel.png",
            "navigation/home_button.png",
            "navigation/back_button.png",
        ),
    }


class ActionExecutor:
    def __init__(
        self,
        *,
        template_root: str | Path,
        click_fn,
        targets: Mapping[str, ActionTarget] | None = None,
        locator: TemplateLocator | None = None,
    ) -> None:
        self.template_root = Path(template_root)
        self.targets = dict(targets or default_action_targets())
        self.locator = locator or TemplateLocator()
        self.clicker = SafeClicker(click_fn)

    def execute(self, action: str, frame: object, bounds: WindowBounds) -> ActionExecution:
        if action in PASSIVE_ACTIONS:
            return ActionExecution(True, passive=True, message="Action passive")

        target = self.targets.get(action)
        if target is None:
            return ActionExecution(False, message=f"Aucune cible configurée pour {action}")

        for relative_path in target.templates:
            match = self.locator.find(
                frame,
                self.template_root / relative_path,
                target.threshold,
            )
            if match is None:
                continue

            absolute_x = bounds.left + match.center[0]
            absolute_y = bounds.top + match.center[1]
            point = self.clicker.click_point(bounds, absolute_x, absolute_y)
            return ActionExecution(
                True,
                target=relative_path,
                point=point,
                message=f"Clic effectué sur {relative_path}",
            )

        configured = any((self.template_root / relative_path).exists() for relative_path in target.templates)
        if target.optional:
            return ActionExecution(
                True,
                passive=True,
                message=f"Cible optionnelle non visible pour {action}",
                configured=configured,
            )
        return ActionExecution(
            False,
            message=f"Aucune cible visible pour {action}",
            configured=configured,
        )
