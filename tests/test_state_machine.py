from dbl_farmer.core.state_machine import StateMachine
from dbl_farmer.farm.resources import ResourceContext, ResourceManager
from dbl_farmer.models import DetectionResult, Objective, ObjectiveKind, ScreenState
from dbl_farmer.navigation.router import NavigationRouter


class FakeDetector:
    def __init__(self, state: ScreenState):
        self.state = state

    def detect(self, _frame):
        return DetectionResult(self.state, 0.99)


class FakeQueue:
    def __init__(self, objective):
        self.objective = objective

    def next(self):
        return self.objective


class FakeRecovery:
    def start_objective(self, objective_id, now):
        pass

    def observe(self, **kwargs):
        from dbl_farmer.recovery.manager import RecoveryLevel
        return RecoveryLevel.NONE


def make_machine(state, objective=None, resource_context=None):
    return StateMachine(
        detector=FakeDetector(state),
        router=NavigationRouter(),
        objectives=FakeQueue(objective),
        resources=ResourceManager(),
        recovery=FakeRecovery(),
        resource_context_provider=lambda: resource_context,
    )


def test_home_routes_to_story_for_story_objective():
    objective = Objective("story-1", ObjectiveKind.STORY, "Story")
    machine = make_machine(ScreenState.HOME, objective=objective)

    result = machine.step(frame=None, now=1.0)

    assert result.action == "OPEN_STORY"


def test_home_routes_to_events_for_event_objective():
    objective = Objective("event-1", ObjectiveKind.EVENT, "Event", limited=True, first_clear_reward=True)
    machine = make_machine(ScreenState.HOME, objective=objective)

    result = machine.step(frame=None, now=1.0)

    assert result.action == "OPEN_EVENTS"


def test_energy_popup_with_premium_only_never_confirms():
    objective = Objective("story-1", ObjectiveKind.STORY, "Story")
    ctx = ResourceContext(False, 0, 0, 2, 0, True)
    machine = make_machine(ScreenState.ENERGY_POPUP, objective=objective, resource_context=ctx)

    result = machine.step(frame=None, now=1.0)

    assert result.action == "CANCEL_PREMIUM_REFILL"


def test_unknown_screen_requests_recovery():
    objective = Objective("story-1", ObjectiveKind.STORY, "Story")
    machine = make_machine(ScreenState.UNKNOWN, objective=objective)

    result = machine.step(frame=None, now=1.0)

    assert result.action == "RECOVER"


def test_action_result_exposes_detected_state_and_objective():
    objective = Objective("story-1", ObjectiveKind.STORY, "Story")
    machine = make_machine(ScreenState.HOME, objective=objective)

    result = machine.step(frame=None, now=1.0)

    assert result.data["state"] is ScreenState.HOME
    assert result.data["objective_id"] == "story-1"


def test_team_selection_configures_once_then_starts_battle():
    objective = Objective("story-1", ObjectiveKind.STORY, "Story")
    machine = make_machine(ScreenState.TEAM_SELECTION, objective=objective)

    first = machine.step(frame=None, now=1.0)
    second = machine.step(frame=None, now=2.0)

    assert first.action == "AUTO_CONFIGURE_TEAM"
    assert second.action == "START_BATTLE"


def test_battle_enables_auto_once_then_waits():
    objective = Objective("story-1", ObjectiveKind.STORY, "Story")
    machine = make_machine(ScreenState.BATTLE, objective=objective)

    first = machine.step(frame=None, now=1.0)
    second = machine.step(frame=None, now=2.0)

    assert first.action == "ENSURE_AUTO_BATTLE"
    assert second.action == "WAIT_FOR_RESULT"


def test_defeat_retries_twice_then_abandons_stage():
    from dbl_farmer.battle.runner import BattleRunner

    objective = Objective("story-progress", ObjectiveKind.STORY, "Story")
    detector = FakeDetector(ScreenState.DEFEAT)
    runner = BattleRunner(max_defeats=3)
    machine = StateMachine(
        detector=detector,
        router=NavigationRouter(),
        objectives=FakeQueue(objective),
        resources=ResourceManager(),
        recovery=FakeRecovery(),
        resource_context_provider=lambda: None,
        battle_runner=runner,
    )
    machine.set_stage_key("story-stage-4-2")

    first = machine.step(frame=None, now=1.0)
    repeated = machine.step(frame=None, now=1.5)
    assert first.action == "RETRY_BATTLE"
    assert repeated.data["defeats"] == 1

    detector.state = ScreenState.BATTLE
    machine.step(frame=None, now=2.0)
    detector.state = ScreenState.DEFEAT
    second = machine.step(frame=None, now=3.0)
    assert second.action == "RETRY_BATTLE"
    assert second.data["defeats"] == 2

    detector.state = ScreenState.BATTLE
    machine.step(frame=None, now=4.0)
    detector.state = ScreenState.DEFEAT
    third = machine.step(frame=None, now=5.0)

    assert third.action == "ABANDON_STAGE"
    assert third.data["stage_blocked"] is True
    assert third.data["defeats"] == 3


def test_successful_stage_selection_allocates_stable_stage_key():
    from dbl_farmer.battle.runner import BattleRunner

    objective = Objective("story-progress", ObjectiveKind.STORY, "Story")
    machine = StateMachine(
        detector=FakeDetector(ScreenState.STAGE_LIST),
        router=NavigationRouter(),
        objectives=FakeQueue(objective),
        resources=ResourceManager(),
        recovery=FakeRecovery(),
        resource_context_provider=lambda: None,
        battle_runner=BattleRunner(max_defeats=3),
    )

    machine.notify_execution("SELECT_STAGE", executed=True)
    first_key = machine.current_stage_key
    machine.notify_execution("RETRY_BATTLE", executed=True)

    assert first_key == "story-progress:stage:1"
    assert machine.current_stage_key == first_key


def test_abandoned_stage_clears_key_so_next_selection_is_new():
    objective = Objective("story-progress", ObjectiveKind.STORY, "Story")
    machine = StateMachine(
        detector=FakeDetector(ScreenState.STAGE_LIST),
        router=NavigationRouter(),
        objectives=FakeQueue(objective),
        resources=ResourceManager(),
        recovery=FakeRecovery(),
        resource_context_provider=lambda: None,
    )

    machine.notify_execution("SELECT_STAGE", executed=True)
    machine.notify_execution("ABANDON_STAGE", executed=True)
    assert machine.current_stage_key is None

    machine.notify_execution("SELECT_STAGE", executed=True)
    assert machine.current_stage_key == "story-progress:stage:2"


def test_failed_visible_action_forces_recovery_on_next_step():
    from dbl_farmer.recovery.manager import RecoveryManager

    objective = Objective("story-1", ObjectiveKind.STORY, "Story")
    machine = StateMachine(
        detector=FakeDetector(ScreenState.HOME),
        router=NavigationRouter(),
        objectives=FakeQueue(objective),
        resources=ResourceManager(),
        recovery=RecoveryManager(soft_after=15, navigation_after=45, max_failures=3),
        resource_context_provider=lambda: None,
    )

    first = machine.step(frame=None, now=1.0)
    machine.notify_execution(first.action, executed=False)
    second = machine.step(frame=None, now=2.0)

    assert first.action == "OPEN_STORY"
    assert second.action == "RECOVER"


def test_successful_recovery_clears_forced_recovery():
    from dbl_farmer.recovery.manager import RecoveryManager

    objective = Objective("story-1", ObjectiveKind.STORY, "Story")
    machine = StateMachine(
        detector=FakeDetector(ScreenState.HOME),
        router=NavigationRouter(),
        objectives=FakeQueue(objective),
        resources=ResourceManager(),
        recovery=RecoveryManager(soft_after=15, navigation_after=45, max_failures=3),
        resource_context_provider=lambda: None,
    )

    first = machine.step(frame=None, now=1.0)
    machine.notify_execution(first.action, executed=False)
    assert machine.step(frame=None, now=2.0).action == "RECOVER"
    machine.notify_execution("RECOVER", executed=True)

    assert machine.step(frame=None, now=3.0).action == "OPEN_STORY"


def test_missing_calibration_pauses_machine_instead_of_random_recovery():
    objective = Objective("story-1", ObjectiveKind.STORY, "Story")
    machine = make_machine(ScreenState.HOME, objective=objective)

    machine.notify_execution("OPEN_STORY", executed=False, configured=False)
    result = machine.step(frame=None, now=2.0)

    assert result.action == "CALIBRATION_REQUIRED"


def test_story_continue_absent_after_calibration_marks_story_done():
    from dbl_farmer.farm.objectives import build_default_objectives
    from dbl_farmer.recovery.manager import RecoveryManager

    queue = build_default_objectives(enable_story=True, enable_events=True)
    detector = FakeDetector(ScreenState.STORY_MENU)
    machine = StateMachine(
        detector=detector,
        router=NavigationRouter(),
        objectives=queue,
        resources=ResourceManager(),
        recovery=RecoveryManager(soft_after=15, navigation_after=45, max_failures=3),
        resource_context_provider=lambda: None,
    )

    action = machine.step(frame=None, now=1.0)
    assert action.action == "CONTINUE_STORY"
    machine.notify_execution("CONTINUE_STORY", executed=False, configured=True)

    assert queue.next().id == "event-progress"
    assert machine.step(frame=None, now=2.0).action == "RECOVER"


def test_no_unfinished_event_after_calibration_marks_event_objective_done():
    from dbl_farmer.farm.objectives import build_default_objectives
    from dbl_farmer.recovery.manager import RecoveryManager

    queue = build_default_objectives(enable_story=False, enable_events=True)
    detector = FakeDetector(ScreenState.EVENT_MENU)
    machine = StateMachine(
        detector=detector,
        router=NavigationRouter(),
        objectives=queue,
        resources=ResourceManager(),
        recovery=RecoveryManager(soft_after=15, navigation_after=45, max_failures=3),
        resource_context_provider=lambda: None,
    )

    action = machine.step(frame=None, now=1.0)
    assert action.action == "OPEN_UNFINISHED_EVENT"
    machine.notify_execution("OPEN_UNFINISHED_EVENT", executed=False, configured=True)

    assert queue.next() is None
    assert machine.step(frame=None, now=2.0).action == "RECOVER"


def test_equipment_selection_auto_configures_once_then_confirms():
    objective = Objective("story-1", ObjectiveKind.STORY, "Story")
    machine = make_machine(ScreenState.EQUIPMENT_SELECTION, objective=objective)

    first = machine.step(frame=None, now=1.0)
    second = machine.step(frame=None, now=2.0)

    assert first.action == "AUTO_CONFIGURE_EQUIPMENT"
    assert second.action == "CONFIRM_EQUIPMENT"
