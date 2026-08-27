# Calibration de l’interface Dragon Ball Legends

Le bot fonctionne à partir de captures de la fenêtre BlueStacks. Il ne dépend pas de coordonnées fixes sur tout l’écran, donc BlueStacks peut être placé sur l’un ou l’autre moniteur. En revanche, garde la même taille de fenêtre BlueStacks après la calibration.

La méthode la plus simple est maintenant :

```bat
start.bat
```

Choisis **2 - Calibrer les boutons de l’interface**. Une fenêtre affiche toutes les captures attendues, indique celles qui existent déjà et explique ce qu’il faut sélectionner. Place DB Legends sur l’écran correspondant, sélectionne la ligne, clique sur **Capturer la sélection**, puis dessine un rectangle serré autour du bouton ou du repère demandé.

Utilise la même langue du jeu pour toutes les captures. L’anglais est recommandé afin de garder les textes des boutons stables et cohérents avec les noms utilisés par le projet.

## Commencer par l’Histoire

Il n’est pas nécessaire de capturer tous les éléments optionnels avant le premier essai. Commence par ces éléments au fur et à mesure que tu rencontres les écrans :

```text
home/home_logo.png
home/story_button.png
home/event_button.png
story/story_title.png
story/continue_button.png
stage_list/stage_list_marker.png
stage_list/stage_card.png
stage_list/unfinished_stage.png
pre_battle/start_battle.png
team/ready_button.png
battle/battle_hud.png
battle/auto_battle.png
results/result_title.png
results/result_ok.png
results/next_button.png
popup/cancel.png
navigation/back_button.png
navigation/home_button.png
```

Si le bot affiche **Calibration requise**, arrête-le, rouvre la fenêtre de calibration et capture l’élément manquant indiqué dans le journal de session. Ce comportement est volontaire : lorsqu’un bouton obligatoire n’a jamais été calibré, le bot s’arrête au lieu de deviner une position à l’écran.

## Énergie et sécurité liée aux Chrono Crystals

Les objets de restauration d’énergie peuvent être automatisés une fois ces captures optionnelles réalisées :

```text
popup/energy_popup.png
popup/energy_item.png
popup/energy_item_confirm.png
```

La confirmation d’une dépense premium ou de Chrono Crystals n’est jamais une action autorisée. Capturer `popup/chrono_crystal.png` améliore la détection de ce type de fenêtre, mais le bot ne possède aucune action permettant de confirmer un achat en Chrono Crystals. Il est important de capturer `popup/cancel.png` afin que le bot puisse fermer ces fenêtres en toute sécurité.

## Événements

Pour les Événements, capture aussi :

```text
event/event_title.png
event/event_tabs.png
event/unfinished_event.png
stage_list/unfinished_stage.png
```

`event/unfinished_event.png` doit correspondre au repère visuel ou à l’état de carte qui permet d’identifier un événement encore non terminé. Lorsqu’aucun événement non terminé correspondant n’est visible, l’objectif de farm d’Événements peut se terminer au lieu de rejouer un événement déjà fini.
