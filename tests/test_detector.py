from dbl_farmer.models import ScreenState
from dbl_farmer.vision.detector import ScreenDetector
from dbl_farmer.vision.states import Cue, StateDefinition


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
