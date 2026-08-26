from dbl_farmer.battle.runner import BattleRunner
from dbl_farmer.models import BattleOutcome, ObjectiveStatus


def test_stage_blocks_on_exactly_third_defeat():
    runner = BattleRunner(max_defeats=3)

    assert runner.record_outcome("4-2", BattleOutcome.DEFEAT) is ObjectiveStatus.ACTIVE
    assert runner.record_outcome("4-2", BattleOutcome.DEFEAT) is ObjectiveStatus.ACTIVE
    assert runner.record_outcome("4-2", BattleOutcome.DEFEAT) is ObjectiveStatus.BLOCKED
    assert runner.defeats_for("4-2") == 3


def test_victory_resets_defeat_counter():
    runner = BattleRunner(max_defeats=3)
    runner.record_outcome("4-2", BattleOutcome.DEFEAT)
    runner.record_outcome("4-2", BattleOutcome.DEFEAT)

    assert runner.record_outcome("4-2", BattleOutcome.VICTORY) is ObjectiveStatus.COMPLETED
    assert runner.defeats_for("4-2") == 0


def test_aborted_battle_does_not_count_as_defeat():
    runner = BattleRunner(max_defeats=3)
    assert runner.record_outcome("4-2", BattleOutcome.ABORTED) is ObjectiveStatus.ACTIVE
    assert runner.defeats_for("4-2") == 0
