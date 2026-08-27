from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TemplateSpec:
    path: str
    description: str
    required: bool = True


_DESCRIPTIONS: dict[str, tuple[str, bool]] = {
    "home/home_logo.png": ("Repère stable de l’écran d’accueil (logo ou en-tête)", True),
    "home/story_button.png": ("Bouton Story (Histoire) sur l’écran d’accueil", True),
    "home/event_button.png": ("Bouton Events (Événements) sur l’écran d’accueil", True),
    "story/story_title.png": ("Titre ou en-tête stable de l’écran Story", True),
    "story/continue_button.png": ("Bouton Continue dans Story", True),
    "event/event_title.png": ("Titre ou en-tête stable de l’écran Events", True),
    "event/event_tabs.png": ("Onglets stables des catégories d’événements", True),
    "event/unfinished_event.png": ("Repère ou carte d’un événement non terminé", True),
    "event/event_card.png": ("Carte générique d’événement de secours", False),
    "stage_list/stage_list_marker.png": ("Repère stable confirmant que la liste des niveaux est ouverte", True),
    "stage_list/stage_card.png": ("Carte générique d’un niveau sélectionnable", True),
    "stage_list/unfinished_stage.png": ("Repère ou carte d’un niveau non terminé", True),
    "stage_list/next_stage.png": ("Repère du prochain ou nouveau niveau, en secours", False),
    "stage_list/start_stage.png": ("Bouton ouvrant le niveau sélectionné", False),
    "pre_battle/start_battle.png": ("Bouton Start Battle", True),
    "pre_battle/energy_cost.png": ("Zone affichant le coût en énergie avant le combat", True),
    "pre_battle/skip_ticket_button.png": ("Bouton Skip Ticket lorsqu’il est disponible", False),
    "pre_battle/skip_confirm.png": ("Confirmation d’utilisation du ticket skip avant le combat", False),
    "team/team_selection.png": ("Repère stable de l’écran de sélection de l’équipe", True),
    "team/ready_button.png": ("Bouton Ready", True),
    "team/auto_select_button.png": ("Bouton Auto Select de l’équipe", False),
    "team/recommended_button.png": ("Bouton Recommended / Best pour l’équipe", False),
    "team/equipment_selection.png": ("Repère stable de l’écran de sélection des équipements", False),
    "team/equipment_auto_button.png": ("Bouton Auto / Recommended pour les équipements", False),
    "team/equipment_confirm.png": ("Bouton de confirmation des équipements", False),
    "battle/battle_hud.png": ("Repère stable de l’interface pendant le combat", True),
    "battle/auto_battle.png": ("Indicateur AUTO lorsque le combat automatique est actif", True),
    "battle/auto_off.png": ("Bouton AUTO lorsque le combat automatique est désactivé", False),
    "results/result_title.png": ("Repère du titre de victoire ou des résultats", True),
    "results/result_ok.png": ("Bouton OK sur l’écran des résultats", True),
    "results/next_button.png": ("Bouton Next / Continue après les résultats", True),
    "results/tap_continue.png": ("Invite à toucher l’écran pour continuer après les résultats", False),
    "results/defeat_marker.png": ("Repère indiquant une défaite", True),
    "results/rematch_button.png": ("Bouton Rematch après une défaite", True),
    "results/quit_button.png": ("Bouton Quit / Back utilisé après trois défaites", False),
    "popup/energy_popup.png": ("Repère de la fenêtre de manque ou recharge d’énergie", True),
    "popup/energy_confirm.png": ("Confirmation sûre d’une recharge d’énergie", False),
    "popup/energy_item.png": ("Repère d’un objet de restauration d’énergie", False),
    "popup/energy_item_confirm.png": ("Confirmation de l’utilisation d’un objet d’énergie", False),
    "popup/chrono_crystal.png": ("Repère Chrono Crystal / recharge premium — détection uniquement", True),
    "popup/premium_refill.png": ("Autre repère de recharge premium — détection uniquement", False),
    "popup/skip_ticket_popup.png": ("Repère de la fenêtre des tickets skip", False),
    "popup/skip_confirm.png": ("Confirmation de l’utilisation d’un ticket skip", False),
    "popup/reward_popup.png": ("Repère d’une fenêtre de récompense", True),
    "popup/reward_ok.png": ("Bouton OK / Fermer d’une récompense", True),
    "popup/error_popup.png": ("Repère d’une fenêtre d’erreur générique", True),
    "popup/error_ok.png": ("Bouton OK d’une fenêtre d’erreur", True),
    "popup/cancel.png": ("Bouton Cancel, notamment pour les demandes de dépense premium", True),
    "navigation/back_button.png": ("Bouton Retour du jeu", True),
    "navigation/home_button.png": ("Bouton Accueil du jeu", True),
}


def template_specs() -> tuple[TemplateSpec, ...]:
    return tuple(
        TemplateSpec(path=path, description=description, required=required)
        for path, (description, required) in sorted(_DESCRIPTIONS.items())
    )


def missing_templates(root: str | Path, *, required_only: bool = False) -> list[TemplateSpec]:
    base = Path(root)
    return [
        spec
        for spec in template_specs()
        if (not required_only or spec.required) and not (base / spec.path).exists()
    ]
