from pathlib import Path

from dbl_farmer.input.executor import ActionExecutor, ActionTarget, default_action_targets
from dbl_farmer.vision.locator import TemplateMatch
from dbl_farmer.vision.window import WindowBounds


class FakeLocator:
    def __init__(self, matches):
        self.matches = matches
        self.calls = []

    def find(self, frame, path, threshold):
        key = str(path).replace('\\', '/')
        self.calls.append((key, threshold))
        return self.matches.get(key)


def test_open_story_clicks_center_of_story_template_relative_to_window(tmp_path: Path):
    clicks = []
    target = ActionTarget("OPEN_STORY", ("home/story_button.png",))
    locator = FakeLocator({
        str(tmp_path / "home/story_button.png").replace('\\', '/'): TemplateMatch(0.99, (100, 200), (80, 180, 40, 40))
    })
    executor = ActionExecutor(
        template_root=tmp_path,
        targets={"OPEN_STORY": target},
        locator=locator,
        click_fn=lambda x, y: clicks.append((x, y)),
    )
    bounds = WindowBounds(left=1920, top=50, width=1440, height=900)

    result = executor.execute("OPEN_STORY", frame=object(), bounds=bounds)

    assert result.executed is True
    assert result.target == "home/story_button.png"
    assert clicks == [(2020, 250)]


def test_wait_action_never_clicks(tmp_path: Path):
    clicks = []
    executor = ActionExecutor(
        template_root=tmp_path,
        targets={},
        locator=FakeLocator({}),
        click_fn=lambda x, y: clicks.append((x, y)),
    )

    result = executor.execute(
        "WAIT_FOR_RESULT",
        frame=object(),
        bounds=WindowBounds(0, 0, 100, 100),
    )

    assert result.executed is True
    assert result.passive is True
    assert clicks == []


def test_cancel_premium_refill_only_uses_safe_cancel_targets(tmp_path: Path):
    clicks = []
    locator = FakeLocator({
        str(tmp_path / "popup/chrono_confirm.png").replace('\\', '/'): TemplateMatch(1.0, (50, 50), (40, 40, 20, 20)),
        str(tmp_path / "popup/cancel.png").replace('\\', '/'): TemplateMatch(0.95, (20, 80), (10, 70, 20, 20)),
    })
    targets = {
        "CANCEL_PREMIUM_REFILL": ActionTarget(
            "CANCEL_PREMIUM_REFILL",
            ("popup/cancel.png", "navigation/back_button.png"),
        )
    }
    executor = ActionExecutor(
        template_root=tmp_path,
        targets=targets,
        locator=locator,
        click_fn=lambda x, y: clicks.append((x, y)),
    )

    result = executor.execute(
        "CANCEL_PREMIUM_REFILL",
        frame=object(),
        bounds=WindowBounds(0, 0, 100, 100),
    )

    assert result.executed is True
    assert result.target == "popup/cancel.png"
    assert clicks == [(20, 80)]


def test_default_targets_cover_main_story_and_event_navigation():
    targets = default_action_targets()

    for action in {
        "OPEN_STORY",
        "OPEN_EVENTS",
        "OPEN_STAGE_LIST",
        "SELECT_STAGE",
        "PREPARE_STAGE",
        "START_BATTLE",
        "CONTINUE_RESULTS",
        "CLOSE_REWARD",
        "CLOSE_ERROR",
        "RECOVER",
    }:
        assert action in targets


def test_optional_auto_configure_succeeds_when_button_is_not_visible(tmp_path: Path):
    clicks = []
    executor = ActionExecutor(
        template_root=tmp_path,
        targets={
            "AUTO_CONFIGURE_TEAM": ActionTarget(
                "AUTO_CONFIGURE_TEAM",
                ("team/auto_select_button.png",),
                optional=True,
            )
        },
        locator=FakeLocator({}),
        click_fn=lambda x, y: clicks.append((x, y)),
    )

    result = executor.execute(
        "AUTO_CONFIGURE_TEAM",
        frame=object(),
        bounds=WindowBounds(0, 0, 100, 100),
    )

    assert result.executed is True
    assert result.passive is True
    assert clicks == []


def test_default_targets_include_auto_team_and_auto_battle():
    targets = default_action_targets()

    assert targets["AUTO_CONFIGURE_TEAM"].optional is True
    assert targets["ENSURE_AUTO_BATTLE"].optional is True


def test_default_targets_include_defeat_recovery_actions():
    targets = default_action_targets()

    assert targets["RETRY_BATTLE"].templates[0] == "results/rematch_button.png"
    assert "ABANDON_STAGE" in targets


def test_missing_required_template_reports_calibration_not_configured(tmp_path: Path):
    executor = ActionExecutor(
        template_root=tmp_path,
        targets={"OPEN_STORY": ActionTarget("OPEN_STORY", ("home/story_button.png",))},
        locator=FakeLocator({}),
        click_fn=lambda *_: None,
    )

    result = executor.execute(
        "OPEN_STORY",
        frame=object(),
        bounds=WindowBounds(0, 0, 100, 100),
    )

    assert result.executed is False
    assert result.configured is False


def test_present_but_not_visible_template_reports_configured(tmp_path: Path):
    path = tmp_path / "home/story_button.png"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"captured")
    executor = ActionExecutor(
        template_root=tmp_path,
        targets={"OPEN_STORY": ActionTarget("OPEN_STORY", ("home/story_button.png",))},
        locator=FakeLocator({}),
        click_fn=lambda *_: None,
    )

    result = executor.execute(
        "OPEN_STORY",
        frame=object(),
        bounds=WindowBounds(0, 0, 100, 100),
    )

    assert result.executed is False
    assert result.configured is True


def test_default_targets_include_optional_auto_equipment():
    targets = default_action_targets()

    assert targets["AUTO_CONFIGURE_EQUIPMENT"].optional is True
    assert targets["AUTO_CONFIGURE_EQUIPMENT"].templates[0] == "team/equipment_auto_button.png"


def test_calibration_required_is_passive_and_never_clicks(tmp_path: Path):
    clicks = []
    executor = ActionExecutor(
        template_root=tmp_path,
        targets={},
        locator=FakeLocator({}),
        click_fn=lambda x, y: clicks.append((x, y)),
    )

    result = executor.execute(
        "CALIBRATION_REQUIRED",
        frame=object(),
        bounds=WindowBounds(0, 0, 100, 100),
    )

    assert result.executed is True
    assert result.passive is True
    assert clicks == []
