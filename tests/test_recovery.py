from dbl_farmer.recovery.manager import RecoveryLevel, RecoveryManager


def test_recovery_escalates_by_elapsed_time():
    mgr = RecoveryManager(soft_after=15, navigation_after=45, max_failures=3)
    mgr.start_objective("x", now=0)

    assert mgr.observe(now=16, state_changed=False, recognized=True, objective_id="x") is RecoveryLevel.SOFT
    assert mgr.observe(now=46, state_changed=False, recognized=False, objective_id="x") is RecoveryLevel.NAVIGATION


def test_state_change_resets_elapsed_timer():
    mgr = RecoveryManager(soft_after=15, navigation_after=45, max_failures=3)
    mgr.start_objective("x", now=0)

    assert mgr.observe(now=10, state_changed=True, recognized=True, objective_id="x") is RecoveryLevel.NONE
    assert mgr.observe(now=20, state_changed=False, recognized=True, objective_id="x") is RecoveryLevel.NONE


def test_third_failed_recovery_blocks_objective():
    mgr = RecoveryManager(soft_after=15, navigation_after=45, max_failures=3)
    mgr.start_objective("x", now=0)

    assert mgr.record_failure("x") is RecoveryLevel.HARD
    assert mgr.record_failure("x") is RecoveryLevel.HARD
    assert mgr.record_failure("x") is RecoveryLevel.BLOCK_OBJECTIVE
