# Calibrating the Dragon Ball Legends interface

The bot works from screenshots of the BlueStacks window. It does not rely on global screen coordinates, so BlueStacks can be on either monitor, but keep the BlueStacks window size stable after calibration.

The easiest method is now:

```bat
start.bat
```

Choose **2 - Calibrate UI templates**. A window lists every template, whether it has already been captured, and what you should select. Put DB Legends on the corresponding screen, select the row, click **Capture selected**, then draw a tight rectangle around the requested button or stable UI marker.

Use the same game language for all captures. English is recommended because button labels remain consistent with the names used by the project.

## Start with the Story path

You do not need to capture every optional item before the first test. Capture these screens as you encounter them:

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

If the bot displays `CALIBRATION_REQUIRED`, stop it, reopen the calibration window, and capture the missing element shown in the session log. This is deliberate: when a required button has never been calibrated, the bot stops instead of guessing a screen coordinate.

## Energy and premium safety

Energy-restoration items can be automated once these optional templates are captured:

```text
popup/energy_popup.png
popup/energy_item.png
popup/energy_item_confirm.png
```

Premium/Chrono Crystal confirmation is never an allowed action. Capturing `popup/chrono_crystal.png` improves detection, but the bot has no action that confirms a Chrono Crystal purchase. `popup/cancel.png` should be captured so premium refill prompts can be closed safely.

## Events

For Events, capture:

```text
event/event_title.png
event/event_tabs.png
event/unfinished_event.png
stage_list/unfinished_stage.png
```

`event/unfinished_event.png` should be the visible marker/card state that tells you an event is not yet finished. Once no matching unfinished event is visible, the event farming objective can finish rather than replaying a completed event.
