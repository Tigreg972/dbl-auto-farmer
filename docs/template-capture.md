# Capturing Dragon Ball Legends UI templates

Run BlueStacks 5 on the Windows primary display or any other display and keep its size stable while capturing a template set. The bot resolves the BlueStacks window bounds, so a second monitor is supported.

Use:

```bat
set PYTHONPATH=src
python tools\capture_template.py --group home --name story_button
```

A screenshot of the BlueStacks window opens. Draw a tight rectangle around the requested UI element and press Enter. Avoid animated backgrounds around the button whenever possible.

## Minimum Story smoke-test set

Capture these first:

```text
home/home_logo.png
home/story_button.png
story/continue_button.png
stage_list/unfinished_marker.png
pre_battle/start_battle.png
pre_battle/skip_ticket.png
team/ready_button.png
battle/auto_on.png
results/victory_marker.png
results/next_button.png
popup/energy.png
popup/chrono_crystal.png
popup/cancel.png
```

Chrono Crystal templates are detection-only. The runtime must cancel/refuse any premium-spend confirmation.

Use the same BlueStacks display scaling and game language for one complete template set. English is recommended because it reduces variation with existing references.
