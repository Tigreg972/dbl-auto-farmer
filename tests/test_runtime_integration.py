from pathlib import Path

from app import RuntimeApp
from dbl_farmer.config import AppConfig
from dbl_farmer.logging.session_log import SessionLogger
from dbl_farmer.models import ActionResult, ScreenState
from dbl_farmer.vision.window import WindowBounds


class FakeMachine:
    def __init__(self, result):
        self.result = result
        self.frames = []

    def step(self, frame, now):
        self.frames.append(frame)
        return self.result


class FakeResolver:
    def __init__(self, bounds):
        self.bounds = bounds
        self.calls = 0

    def find(self, pattern):
        self.calls += 1
        return self.bounds


class FakeCapture:
    def __init__(self, frame):
        self.frame = frame
        self.bounds = []

    def grab(self, bounds):
        self.bounds.append(bounds)
        return self.frame


class FakeExecutor:
    def __init__(self):
        self.calls = []

    def execute(self, action, frame, bounds):
        self.calls.append((action, frame, bounds))
        from dbl_farmer.input.executor import ActionExecution
        return ActionExecution(True, target="home/story_button.png", point=(10, 10))


def test_runtime_captures_bluestacks_and_executes_decided_action(tmp_path: Path):
    frame = object()
    bounds = WindowBounds(100, 50, 500, 800)
    machine = FakeMachine(ActionResult(True, "OPEN_STORY", data={"state": ScreenState.HOME, "objective_id": "story-progress"}))
    capture = FakeCapture(frame)
    executor = FakeExecutor()
    runtime = RuntimeApp(
        config=AppConfig(),
        machine=machine,
        logger=SessionLogger(tmp_path / "logs"),
        resolver=FakeResolver(bounds),
        capture=capture,
        executor=executor,
        dry_run=False,
    )

    runtime.process_once(now=1.0)

    assert capture.bounds == [bounds]
    assert machine.frames == [frame]
    assert executor.calls == [("OPEN_STORY", frame, bounds)]


def test_runtime_dry_run_captures_but_never_executes(tmp_path: Path):
    frame = object()
    bounds = WindowBounds(0, 0, 500, 800)
    executor = FakeExecutor()
    runtime = RuntimeApp(
        config=AppConfig(),
        machine=FakeMachine(ActionResult(True, "OPEN_STORY", data={"state": ScreenState.HOME, "objective_id": "story-progress"})),
        logger=SessionLogger(tmp_path / "logs"),
        resolver=FakeResolver(bounds),
        capture=FakeCapture(frame),
        executor=executor,
        dry_run=True,
    )

    runtime.process_once(now=1.0)

    assert executor.calls == []


class FakeContextObserver:
    def __init__(self):
        self.frames = []

    def update(self, frame):
        self.frames.append(frame)


def test_runtime_updates_visual_context_before_state_machine(tmp_path: Path):
    frame = object()
    bounds = WindowBounds(0, 0, 500, 800)
    observer = FakeContextObserver()
    machine = FakeMachine(ActionResult(True, "IDLE", data={"state": ScreenState.HOME, "objective_id": None}))
    runtime = RuntimeApp(
        config=AppConfig(),
        machine=machine,
        logger=SessionLogger(tmp_path / "logs"),
        resolver=FakeResolver(bounds),
        capture=FakeCapture(frame),
        executor=FakeExecutor(),
        dry_run=True,
        context_observer=observer,
    )

    runtime.process_once(now=1.0)

    assert observer.frames == [frame]
    assert machine.frames == [frame]


def test_runtime_reports_execution_back_to_machine(tmp_path: Path):
    class FeedbackMachine(FakeMachine):
        def __init__(self, result):
            super().__init__(result)
            self.feedback = []

        def notify_execution(self, action, executed):
            self.feedback.append((action, executed))

    frame = object()
    machine = FeedbackMachine(ActionResult(True, "OPEN_STORY", data={"state": ScreenState.HOME, "objective_id": "story-progress"}))
    runtime = RuntimeApp(
        config=AppConfig(),
        machine=machine,
        logger=SessionLogger(tmp_path / "logs"),
        resolver=FakeResolver(WindowBounds(0, 0, 500, 800)),
        capture=FakeCapture(frame),
        executor=FakeExecutor(),
        dry_run=False,
    )

    runtime.process_once(now=1.0)

    assert machine.feedback == [("OPEN_STORY", True)]


def test_build_runtime_wires_battle_runner():
    from app import build_runtime

    runtime = build_runtime(dry_run=True, window_provider=lambda: [])

    assert runtime.machine.battle_runner is not None
