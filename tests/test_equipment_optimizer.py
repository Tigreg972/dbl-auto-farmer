from dbl_farmer.battle.equipment_optimizer import EquipmentCandidate, EquipmentOptimizer
from dbl_farmer.battle.team_optimizer import TeamPlan


def test_equipment_optimizer_never_assigns_incompatible_item():
    team = TeamPlan(core=("a", "b", "c"), bench=(), signature="abc")
    items = [
        EquipmentCandidate("great-but-wrong", {"x"}, 100, 100),
        EquipmentCandidate("valid", {"a"}, 50, 50),
    ]

    plan = EquipmentOptimizer().choose(team, items)

    assert plan.assignments["a"] == ("valid",)


def test_best_compatible_items_are_assigned_first():
    team = TeamPlan(core=("a",), bench=(), signature="a")
    items = [
        EquipmentCandidate("low", {"a"}, 10, 10),
        EquipmentCandidate("high", {"a"}, 20, 40),
        EquipmentCandidate("mid", {"a"}, 15, 30),
    ]

    plan = EquipmentOptimizer(max_per_character=2).choose(team, items)

    assert plan.assignments["a"] == ("high", "mid")
