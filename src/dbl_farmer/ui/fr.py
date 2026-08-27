from __future__ import annotations

_ACTIONS = {
    "OPEN_STORY": "Ouvrir l’Histoire",
    "OPEN_EVENTS": "Ouvrir les Événements",
    "CONTINUE_STORY": "Continuer l’Histoire",
    "OPEN_UNFINISHED_EVENT": "Ouvrir un événement non terminé",
    "SELECT_UNFINISHED_STAGE": "Sélectionner un niveau non terminé",
    "OPEN_STAGE_LIST": "Ouvrir la liste des niveaux",
    "SELECT_STAGE": "Sélectionner un niveau",
    "OPEN_PRE_BATTLE": "Ouvrir la préparation du combat",
    "PREPARE_STAGE": "Préparer le niveau",
    "CONFIRM_SKIP": "Confirmer l’utilisation du ticket skip",
    "CONFIRM_ENERGY_ITEM": "Confirmer l’objet d’énergie",
    "AUTO_CONFIGURE_TEAM": "Configurer automatiquement l’équipe",
    "AUTO_CONFIGURE_EQUIPMENT": "Configurer automatiquement les équipements",
    "CONFIRM_EQUIPMENT": "Confirmer les équipements",
    "START_BATTLE": "Lancer le combat",
    "ENSURE_AUTO_BATTLE": "Activer le combat automatique",
    "RETRY_BATTLE": "Retenter le combat",
    "ABANDON_STAGE": "Abandonner le niveau",
    "CONTINUE_RESULTS": "Continuer après les résultats",
    "CLOSE_REWARD": "Fermer la récompense",
    "CLOSE_ERROR": "Fermer le message d’erreur",
    "CANCEL_ENERGY_POPUP": "Fermer la fenêtre d’énergie",
    "CANCEL_PREMIUM_REFILL": "Annuler la dépense de Chrono Crystals",
    "RECOVER": "Récupération automatique",
    "IDLE": "En attente",
    "WAIT_FOR_RESULT": "Attendre le résultat",
    "CONTINUE_WITH_CURRENT_ENERGY": "Continuer avec l’énergie actuelle",
    "CALIBRATION_REQUIRED": "Calibration requise",
}

_STATES = {
    "UNKNOWN": "Inconnu",
    "HOME": "Accueil",
    "STORY_MENU": "Menu Histoire",
    "EVENT_MENU": "Menu Événements",
    "STAGE_LIST": "Liste des niveaux",
    "PRE_BATTLE": "Avant-combat",
    "TEAM_SELECTION": "Sélection de l’équipe",
    "EQUIPMENT_SELECTION": "Sélection des équipements",
    "BATTLE": "Combat",
    "RESULTS": "Résultats",
    "DEFEAT": "Défaite",
    "ENERGY_POPUP": "Fenêtre d’énergie",
    "SKIP_TICKET_POPUP": "Fenêtre des tickets skip",
    "REWARD_POPUP": "Récompense",
    "ERROR_POPUP": "Erreur",
    "PREMIUM_REFILL_POPUP": "Dépense en Chrono Crystals détectée",
}

_OBJECTIVES = {
    "story-progress": "Progression de l’Histoire",
    "event-progress": "Progression des Événements",
}

_STATUSES = {
    "Stopped": "Arrêté",
    "Running": "En cours",
    "Paused": "En pause",
}


def action_label(value: str) -> str:
    return _ACTIONS.get(value, value)


def state_label(value: str) -> str:
    return _STATES.get(value, value)


def objective_label(value: str) -> str:
    return _OBJECTIVES.get(value, value)


def status_label(value: str) -> str:
    return _STATUSES.get(value, value)
