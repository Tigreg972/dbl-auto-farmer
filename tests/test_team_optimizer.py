from dbl_farmer.battle.team_optimizer import (
    CharacterCandidate,
    StageRequirements,
    TeamOptimizer,
)


def test_required_tag_beats_raw_power():
    candidates = [
        CharacterCandidate("strong", {"Saiyan"}, "RED", 100, False, False),
        CharacterCandidate("required", {"Android"}, "BLU", 60, False, False),
        CharacterCandidate("boosted", {"Android"}, "GRN", 55, True, False),
        CharacterCandidate("third", {"Android"}, "PUR", 50, False, False),
    ]
    req = StageRequirements(required_tags={"Android"}, enemy_elements={"YEL"})

    plan = TeamOptimizer().choose(candidates, req)

    assert "strong" not in plan.core
    assert "boosted" in plan.core


def test_restricted_out_character_is_never_selected():
    candidates = [
        CharacterCandidate("bad", {"Android"}, "BLU", 999, True, True),
        CharacterCandidate("a", {"Android"}, "BLU", 60, False, False),
        CharacterCandidate("b", {"Android"}, "GRN", 55, False, False),
        CharacterCandidate("c", {"Android"}, "PUR", 50, False, False),
    ]
    req = StageRequirements(required_tags={"Android"}, enemy_elements={"YEL"})

    plan = TeamOptimizer().choose(candidates, req)

    assert "bad" not in plan.core


def test_team_signature_changes_when_core_changes():
    opt = TeamOptimizer()
    req = StageRequirements(required_tags=set(), enemy_elements=set())
    a = [
        CharacterCandidate("1", set(), "RED", 100, False, False),
        CharacterCandidate("2", set(), "BLU", 90, False, False),
        CharacterCandidate("3", set(), "GRN", 80, False, False),
        CharacterCandidate("4", set(), "PUR", 70, False, False),
    ]
    b = a + [CharacterCandidate("5", set(), "YEL", 200, False, False)]

    assert opt.choose(a, req).signature != opt.choose(b, req).signature
