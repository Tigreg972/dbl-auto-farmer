# DBL Auto Farmer

Automatisation côté client pour Dragon Ball Legends sous Windows avec BlueStacks 5. Le bot utilise la reconnaissance d’images OpenCV, une machine à états et des clics limités à la fenêtre BlueStacks détectée. Il ne modifie pas la mémoire du jeu, ne falsifie pas la progression serveur, ne modifie pas le trafic réseau du jeu et ne contourne pas l’anti-cheat.

## Ce que fait la V1

- Fait d’abord l’Histoire, puis les Événements.
- Détecte l’écran actuel au lieu d’exécuter une macro fixe.
- Fonctionne avec BlueStacks placé sur l’un ou l’autre écran.
- Peut utiliser les Tickets skip lorsque le bouton correspondant est disponible.
- Peut utiliser des objets de restauration d’énergie lorsque les éléments nécessaires ont été calibrés.
- Ne possède aucune action permettant de confirmer une dépense de Chrono Crystals.
- Utilise les options Auto / Recommended du jeu pour l’équipe lorsqu’elles sont disponibles, puis appuie sur Ready.
- Active le combat automatique lorsqu’un bouton indiquant que l’Auto est désactivé est détecté.
- Retente un combat et abandonne le niveau après trois défaites détectées.
- Journalise les écrans détectés, les actions prévues, les cibles et les clics.
- Passe en « Calibration requise » lorsqu’un bouton obligatoire n’a jamais été capturé au lieu de cliquer au hasard.

## Démarrage rapide sous Windows

1. Installe Python 3.11 ou une version plus récente.
2. Ouvre le dossier du dépôt.
3. Double-clique sur `start.bat`.
4. Choisis **1 - Installer / mettre à jour les dépendances** une première fois.
5. Choisis **2 - Calibrer les boutons de l’interface** pour capturer les éléments de ta version actuelle de DB Legends.
6. Choisis **3 - Test sans clic** pour vérifier la détection. La souris ne doit pas bouger.
7. Quand la détection est correcte, choisis **4 - Lancer le bot**.

La fenêtre de contrôle contient les boutons **Démarrer**, **Pause** et **Arrêter**. Le bot ne commence réellement à cliquer qu’après avoir appuyé sur **Démarrer**.

## Langue du jeu

L’interface du bot est en français. Pour la calibration, Dragon Ball Legends peut rester en anglais : c’est même recommandé pour garder les libellés des boutons stables et cohérents entre les captures.

## Tests

Depuis une invite de commandes ouverte dans le dépôt :

```bat
set PYTHONPATH=src
python -m pytest -q
```

## Règles de sécurité

- L’énergie et les objets de restauration d’énergie peuvent être utilisés.
- Les Tickets skip peuvent être utilisés.
- La dépense de Chrono Crystals est interdite en dur et ne peut pas être activée dans `config.yaml`.
- Tous les clics du bot doivent rester à l’intérieur de la fenêtre BlueStacks actuellement détectée.

Consulte `docs/template-capture.md` pour les instructions de calibration.
