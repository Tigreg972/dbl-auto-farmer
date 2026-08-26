from dbl_farmer.farm.objectives import ObjectiveQueue
from dbl_farmer.models import Objective, ObjectiveKind


def test_limited_event_precedes_story_and_permanent_event():
    queue = ObjectiveQueue([
        Objective("story-1", ObjectiveKind.STORY, "Story 1", limited=False, first_clear_reward=True),
        Objective("event-perm", ObjectiveKind.EVENT, "Perm Event", limited=False, first_clear_reward=False),
        Objective("event-limited", ObjectiveKind.EVENT, "Limited Event", limited=True, first_clear_reward=True),
    ])

    assert queue.next().id == "event-limited"


def test_blocked_objective_is_not_retried_without_team_change():
    queue = ObjectiveQueue([
        Objective("story-1", ObjectiveKind.STORY, "Story 1", limited=False, first_clear_reward=True),
    ])

    queue.mark_blocked("story-1", team_signature="team-a")
    assert queue.next() is None

    queue.requeue_if_team_changed("story-1", "team-a")
    assert queue.next() is None

    queue.requeue_if_team_changed("story-1", "team-b")
    assert queue.next().id == "story-1"


def test_permanent_repeatable_requires_progress_flag():
    queue = ObjectiveQueue([
        Objective("perm", ObjectiveKind.PERMANENT, "Permanent", required_for_progress=False),
    ])
    assert queue.next() is None
