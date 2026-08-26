from dbl_farmer.models import ScreenState
from dbl_farmer.vision.detector import ScreenDetector
from dbl_farmer.vision.states import Cue, StateDefinition, default_state_definitions


def test_detector_combines_multiple_cues():
    scores = {"home_logo": 0.96, "story_button": 0.91, "event_button": 0.88}
    matcher = lambda _frame, cue: scores.get(cue.name, 0.0)
    definition = StateDefinition(
        state=ScreenState.HOME,
        cues=(
            Cue("home_logo", "x", 0.5),
            Cue("story_button", "y", 0.25),
            Cue("event_button", "z", 0.25),
        ),
        threshold=0.80,
    )
    detector = ScreenDetector([definition], matcher=matcher)

    result = detector.detect(object())

    assert result.state is ScreenState.HOME
    assert result.confidence > 0.90


def test_required_cue_can_veto_state():
    scores = {"required": 0.2, "optional": 1.0}
    matcher = lambda _frame, cue: scores.get(cue.name, 0.0)
    definition = StateDefinition(
        state=ScreenState.RESULTS,
        cues=(Cue("required", "x", 0.7, required=True), Cue("optional", "y", 0.3)),
        threshold=0.70,
    )
    detector = ScreenDetector([definition], matcher=matcher, required_cue_threshold=0.75)

    result = detector.detect(object())

    assert result.state is ScreenState.UNKNOWN


def test_default_templates_use_semantic_subfolders():
    from dbl_farmer.vision.states import default_state_definitions

    definitions = default_state_definitions("assets/templates")
    home = next(d for d in definitions if d.state is ScreenState.HOME)
    story_cue = next(c for c in home.cues if c.name == "story_button")

    assert story_cue.template_path.endswith("home/story_button.png")


def test_default_definitions_include_defeat_state():
    from dbl_farmer.vision.states import default_state_definitions

    definitions = default_state_definitions("assets/templates")

    assert any(d.state is ScreenState.DEFEAT for d in definitions)


def test_default_home_can_be_recognized_from_story_and_event_buttons_without_logo():
    scores = {"story_button": 0.98, "event_button": 0.97}
    detector = ScreenDetector(
        default_state_definitions("assets/templates"),
        matcher=lambda _frame, cue: scores.get(cue.name, 0.0),
    )

    result = detector.detect(object())

    assert result.state is ScreenState.HOME


def test_story_menu_remains_recognizable_when_continue_disappears_at_completion():
    scores = {"story_title": 0.98, "continue_button": 0.0}
    detector = ScreenDetector(
        default_state_definitions("assets/templates"),
        matcher=lambda _frame, cue: scores.get(cue.name, 0.0),
    )

    result = detector.detect(object())

    assert result.state is ScreenState.STORY_MENU


def test_battle_can_be_recognized_when_auto_is_off():
    scores = {"battle_hud": 0.98, "auto_off": 0.95}
    detector = ScreenDetector(
        default_state_definitions("assets/templates"),
        matcher=lambda _frame, cue: scores.get(cue.name, 0.0),
    )

    result = detector.detect(object())

    assert result.state is ScreenState.BATTLE
