from dbl_farmer.farm.resources import ResourceContext, ResourceManager
from dbl_farmer.models import ResourceDecision


def test_skip_ticket_is_preferred_when_eligible():
    ctx = ResourceContext(
        skip_eligible=True,
        skip_tickets=3,
        energy=10,
        energy_cost=2,
        energy_items=0,
        premium_refill_visible=False,
    )
    assert ResourceManager().decide(ctx) is ResourceDecision.USE_SKIP


def test_premium_refill_is_never_confirmed():
    manager = ResourceManager()
    assert manager.is_safe_confirmation({"Chrono Crystals", "10", "Confirm"}) is False


def test_insufficient_energy_without_items_stops_instead_of_buying_cc():
    ctx = ResourceContext(
        skip_eligible=False,
        skip_tickets=0,
        energy=0,
        energy_cost=2,
        energy_items=0,
        premium_refill_visible=True,
    )
    assert ResourceManager().decide(ctx) is ResourceDecision.STOP_NO_SAFE_ENERGY


def test_available_energy_uses_normal_battle():
    ctx = ResourceContext(False, 0, 5, 2, 0, False)
    assert ResourceManager().decide(ctx) is ResourceDecision.RUN_BATTLE
