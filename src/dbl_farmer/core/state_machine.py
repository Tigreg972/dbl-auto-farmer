from __future__ import annotations

from collections.abc import Callable

from dbl_farmer.farm.resources import ResourceContext, ResourceManager
from dbl_farmer.models import ActionResult, BattleOutcome, ObjectiveStatus, ResourceDecision, ScreenState
from dbl_farmer.navigation.router import NavigationRouter
from dbl_farmer.recovery.manager import RecoveryLevel


class StateMachine:
    def __init__(
        self,
        detector,
        router: NavigationRouter,
        objectives,
        resources: ResourceManager,
        recovery,
        resource_context_provider: Callable[[], ResourceContext | None],
        battle_runner=None,
    ) -> None:
        self.detector = detector
        self.router = router
        self.objectives = objectives
        self.resources = resources
        self.recovery = recovery
        self.resource_context_provider = resource_context_provider
        self.battle_runner = battle_runner
        self._last_state: ScreenState | None = None
        self._active_objective_id: str | None = None
        self._team_configured = False
        self._equipment_configured = False
        self._auto_battle_checked = False
        self._stage_key: str | None = None
        self._stage_sequence = 0
        self._defeat_entry_handled = False
        self._last_defeat_status: ObjectiveStatus | None = None
        self._forced_recovery = False
        self._calibration_required = False
        self._last_now = 0.0

    @property
    def current_stage_key(self) -> str | None:
        return self._stage_key

    def set_stage_key(self, stage_key: str | None) -> None:
        self._stage_key = stage_key
        self._defeat_entry_handled = False
        self._last_defeat_status = None

    def notify_execution(self, action: str, executed: bool, configured: bool = True) -> None:
        objective = self.objectives.next()
        objective_id = objective.id if objective is not None else "__idle__"

        if not executed:
            if not configured:
                self._calibration_required = True
                self._forced_recovery = False
                return

            mark_completed = getattr(self.objectives, "mark_completed", None)
            if (
                objective is not None
                and action in {"OPEN_STAGE_LIST", "CONTINUE_STORY"}
                and self._last_state is ScreenState.STORY_MENU
                and callable(mark_completed)
            ):
                mark_completed(objective.id)
                self._forced_recovery = True
                return

            if (
                objective is not None
                and action == "OPEN_UNFINISHED_EVENT"
                and self._last_state is ScreenState.EVENT_MENU
                and callable(mark_completed)
            ):
                mark_completed(objective.id)
                self._forced_recovery = True
                return

            record_failure = getattr(self.recovery, "record_failure", None)
            if callable(record_failure):
                record_failure(objective_id)
            self._forced_recovery = True
            return

        if action == "RECOVER":
            self._forced_recovery = False
            start_objective = getattr(self.recovery, "start_objective", None)
            if callable(start_objective):
                start_objective(objective_id, self._last_now)
            return

        if action in {"SELECT_STAGE", "SELECT_UNFINISHED_STAGE"} and objective is not None:
            if self._stage_key is None:
                self._stage_sequence += 1
                self.set_stage_key(f"{objective.id}:stage:{self._stage_sequence}")
            return
        if action in {"ABANDON_STAGE", "CONTINUE_RESULTS"}:
            if action == "CONTINUE_RESULTS" and self.battle_runner is not None and self._stage_key:
                self.battle_runner.record_outcome(self._stage_key, BattleOutcome.VICTORY)
            self.set_stage_key(None)

    def step(self, frame, now: float) -> ActionResult:
        self._last_now = now
        detection = self.detector.detect(frame)
        state = detection.state
        objective = self.objectives.next()

        if objective is not None and objective.id != self._active_objective_id:
            self._active_objective_id = objective.id
            self.recovery.start_objective(objective.id, now)

        objective_id = objective.id if objective is not None else "__idle__"
        previous_state = self._last_state
        state_changed = previous_state is not None and state is not previous_state
        recognized = state is not ScreenState.UNKNOWN
        if state is not ScreenState.TEAM_SELECTION:
            self._team_configured = False
        if state is not ScreenState.EQUIPMENT_SELECTION:
            self._equipment_configured = False
        if state is not ScreenState.BATTLE:
            self._auto_battle_checked = False
        if state is not ScreenState.DEFEAT:
            self._defeat_entry_handled = False
            self._last_defeat_status = None
        self._last_state = state

        if self._calibration_required:
            return ActionResult(
                False,
                "CALIBRATION_REQUIRED",
                "Required UI template is missing; run calibration and restart",
                data={
                    "state": state,
                    "objective_id": objective.id if objective is not None else None,
                    "objective_kind": objective.kind if objective is not None else None,
                },
            )

        if self._forced_recovery:
            return ActionResult(
                False,
                "RECOVER",
                "Previous action could not be executed",
                data={
                    "state": state,
                    "objective_id": objective.id if objective is not None else None,
                    "objective_kind": objective.kind if objective is not None else None,
                },
            )

        if state is ScreenState.ENERGY_POPUP:
            context = self.resource_context_provider()
            if context is None:
                return ActionResult(False, "CANCEL_ENERGY_POPUP", "No resource context available")
            decision = self.resources.decide(context)
            if decision is ResourceDecision.USE_ENERGY_ITEM:
                return ActionResult(True, "CONFIRM_ENERGY_ITEM")
            if decision is ResourceDecision.STOP_NO_SAFE_ENERGY:
                return ActionResult(True, "CANCEL_PREMIUM_REFILL")
            if decision is ResourceDecision.USE_SKIP:
                return ActionResult(True, "CONFIRM_SKIP")
            return ActionResult(True, "CONTINUE_WITH_CURRENT_ENERGY")

        if state is ScreenState.UNKNOWN:
            return ActionResult(False, "RECOVER", "Screen state is unknown")

        if state is ScreenState.DEFEAT:
            if objective is None or self.battle_runner is None:
                return ActionResult(
                    True,
                    "RETRY_BATTLE",
                    data={"state": state, "objective_id": objective.id if objective else None},
                )
            stage_key = self._stage_key or objective.id
            if not self._defeat_entry_handled:
                self._last_defeat_status = self.battle_runner.record_outcome(
                    stage_key,
                    BattleOutcome.DEFEAT,
                )
                self._defeat_entry_handled = True
            defeats = self.battle_runner.defeats_for(stage_key)
            blocked = self._last_defeat_status is ObjectiveStatus.BLOCKED
            return ActionResult(
                True,
                "ABANDON_STAGE" if blocked else "RETRY_BATTLE",
                data={
                    "state": state,
                    "objective_id": objective.id,
                    "objective_kind": objective.kind,
                    "stage_key": stage_key,
                    "stage_blocked": blocked,
                    "defeats": defeats,
                },
            )

        if state is ScreenState.EQUIPMENT_SELECTION and not self._equipment_configured:
            self._equipment_configured = True
            return ActionResult(
                True,
                "AUTO_CONFIGURE_EQUIPMENT",
                data={
                    "state": state,
                    "objective_id": objective.id if objective is not None else None,
                    "objective_kind": objective.kind if objective is not None else None,
                },
            )

        if state is ScreenState.TEAM_SELECTION and not self._team_configured:
            self._team_configured = True
            return ActionResult(
                True,
                "AUTO_CONFIGURE_TEAM",
                data={
                    "state": state,
                    "objective_id": objective.id if objective is not None else None,
                    "objective_kind": objective.kind if objective is not None else None,
                },
            )

        if state is ScreenState.BATTLE and not self._auto_battle_checked:
            self._auto_battle_checked = True
            return ActionResult(
                True,
                "ENSURE_AUTO_BATTLE",
                data={
                    "state": state,
                    "objective_id": objective.id if objective is not None else None,
                    "objective_kind": objective.kind if objective is not None else None,
                },
            )

        recovery_level = self.recovery.observe(
            now=now,
            state_changed=state_changed,
            recognized=recognized,
            objective_id=objective_id,
        )
        if recovery_level in {RecoveryLevel.NAVIGATION, RecoveryLevel.HARD, RecoveryLevel.BLOCK_OBJECTIVE}:
            return ActionResult(False, "RECOVER", recovery_level.name)

        action = self.router.action_for(state, objective)
        return ActionResult(
            True,
            action.name,
            data={
                "expected_states": action.expected_states,
                "state": state,
                "objective_id": objective.id if objective is not None else None,
                "objective_kind": objective.kind if objective is not None else None,
            },
        )
