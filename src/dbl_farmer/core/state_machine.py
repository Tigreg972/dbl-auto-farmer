from __future__ import annotations

from collections.abc import Callable

from dbl_farmer.farm.resources import ResourceContext, ResourceManager
from dbl_farmer.models import ActionResult, ResourceDecision, ScreenState
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
    ) -> None:
        self.detector = detector
        self.router = router
        self.objectives = objectives
        self.resources = resources
        self.recovery = recovery
        self.resource_context_provider = resource_context_provider
        self._last_state: ScreenState | None = None
        self._active_objective_id: str | None = None

    def step(self, frame, now: float) -> ActionResult:
        detection = self.detector.detect(frame)
        state = detection.state
        objective = self.objectives.next()

        if objective is not None and objective.id != self._active_objective_id:
            self._active_objective_id = objective.id
            self.recovery.start_objective(objective.id, now)

        objective_id = objective.id if objective is not None else "__idle__"
        state_changed = self._last_state is not None and state is not self._last_state
        recognized = state is not ScreenState.UNKNOWN
        self._last_state = state

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

        recovery_level = self.recovery.observe(
            now=now,
            state_changed=state_changed,
            recognized=recognized,
            objective_id=objective_id,
        )
        if recovery_level in {RecoveryLevel.NAVIGATION, RecoveryLevel.HARD, RecoveryLevel.BLOCK_OBJECTIVE}:
            return ActionResult(False, "RECOVER", recovery_level.name)

        action = self.router.action_for(state, objective)
        return ActionResult(True, action.name, data={"expected_states": action.expected_states})
