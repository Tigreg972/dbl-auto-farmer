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
