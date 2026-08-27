from dbl_farmer.ui.fr import action_label, objective_label, state_label, status_label


def test_action_labels_are_french():
    assert action_label("OPEN_STORY") == "Ouvrir l’Histoire"
    assert action_label("START_BATTLE") == "Lancer le combat"
    assert action_label("CALIBRATION_REQUIRED") == "Calibration requise"


def test_state_and_objective_labels_are_french():
    assert state_label("HOME") == "Accueil"
    assert state_label("PRE_BATTLE") == "Avant-combat"
    assert objective_label("story-progress") == "Progression de l’Histoire"
    assert objective_label("event-progress") == "Progression des Événements"


def test_status_labels_are_french():
    assert status_label("Stopped") == "Arrêté"
    assert status_label("Running") == "En cours"
    assert status_label("Paused") == "En pause"


def test_unknown_values_remain_readable():
    assert action_label("SOMETHING_NEW") == "SOMETHING_NEW"
    assert state_label("NEW_STATE") == "NEW_STATE"
    assert objective_label("custom") == "custom"
