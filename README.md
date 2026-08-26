# DBL Auto Farmer

Windows / BlueStacks 5 client-side UI automation for Dragon Ball Legends. The bot uses OpenCV template recognition, a state machine, and clicks constrained to the detected BlueStacks window. It does **not** modify game memory, forge server progression, tamper with game network traffic, or bypass anti-cheat.

## What the current V1 does

- Farms Story first, then Events.
- Uses screen-state detection instead of a fixed macro sequence.
- Works with BlueStacks on either monitor.
- Can use Skip Tickets when the Skip button is available.
- Can use Energy-restoration items after the relevant popup templates are calibrated.
- Never has an action that confirms Chrono Crystal spending.
- Uses the game's Auto/Recommended team option when available, then presses Ready.
- Ensures Auto Battle is enabled when an `AUTO OFF` button is detected.
- Retries a battle and abandons the current stage after three detected defeats.
- Logs every state, intended action, target and click.
- Stops with `CALIBRATION_REQUIRED` when a required UI target has never been captured instead of guessing coordinates.

## Quick start on Windows

1. Install Python 3.11+.
2. Open the repository folder.
3. Double-click `start.bat`.
4. Choose **1** once to install dependencies.
5. Choose **2** to calibrate the DB Legends UI in your current game language/resolution.
6. Choose **3** for a dry run. The mouse must not move.
7. When detection is correct, choose **4** for live mode.

The control window has Start / Pause / Stop buttons. Live automation begins only after pressing **Start**.

## Tests

From a command prompt in the repository:

```bat
set PYTHONPATH=src
python -m pytest -q
```

## Safety rules

- Energy and Energy-restoration items may be used.
- Skip Tickets may be used.
- Chrono Crystal spending is hard-coded forbidden and cannot be enabled through `config.yaml`.
- All bot clicks must be inside the currently resolved BlueStacks window.

See `docs/template-capture.md` for calibration instructions.
