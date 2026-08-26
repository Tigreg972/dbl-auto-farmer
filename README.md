# DBL Auto Farmer

Client-side Windows automation for Dragon Ball Legends running in BlueStacks 5. The project uses screen recognition and safe window-relative clicks. It does **not** modify game memory, forge server progress, tamper with network traffic, bypass anti-cheat, or automatically spend Chrono Crystals.

## Current milestone

The repository contains the tested automation core: immutable premium-spend guard, multi-monitor BlueStacks window resolution, multi-cue screen-state detection, safe relative clicks, objective prioritization, Energy/Skip Ticket policy, three-defeat blocking, recovery escalation, state-machine routing, session logging, and team/equipment scoring.

Live automation still requires a UI template set captured from the current Dragon Ball Legends build and language before enabling clicks.

## Install on Windows

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Run tests:

```bat
set PYTHONPATH=src
pytest -q
```

Start in dry-run mode first:

```bat
start.bat --dry-run
```

Dry-run detects/logs intended actions but does not click. Do not use live mode until the relevant templates have been captured and detection is correct.

## Capture templates

See [docs/template-capture.md](docs/template-capture.md).

Example:

```bat
set PYTHONPATH=src
python tools\capture_template.py --group home --name story_button
```

## Safety rules

- Energy and Energy-restoration items may be used.
- Skip Tickets may be used.
- Chrono Crystal spending is hard-coded forbidden and cannot be enabled through `config.yaml`.
- A stage is blocked for the session after three defeats unless a materially different team configuration is later selected.
