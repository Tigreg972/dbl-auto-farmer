from dbl_farmer.models import Objective, ObjectiveKind, ScreenState
from dbl_farmer.navigation.router import NavigationRouter


def test_story_and_event_menus_use_distinct_actions():
    router = NavigationRouter()
    story = Objective("story", ObjectiveKind.STORY, "Story")
    event = Objective("event", ObjectiveKind.EVENT, "Event")

    assert router.action_for(ScreenState.STORY_MENU, story).name == "CONTINUE_STORY"
    assert router.action_for(ScreenState.EVENT_MENU, event).name == "OPEN_UNFINISHED_EVENT"


def test_stage_list_uses_unfinished_stage_action():
    router = NavigationRouter()
    story = Objective("story", ObjectiveKind.STORY, "Story")

    assert router.action_for(ScreenState.STAGE_LIST, story).name == "SELECT_UNFINISHED_STAGE"
