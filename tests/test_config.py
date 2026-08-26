from pathlib import Path

from dbl_farmer.config import load_config


def test_defaults_never_allow_cc_spending(tmp_path: Path):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("allow_chrono_crystals: true\n", encoding="utf-8")

    cfg = load_config(cfg_file)

    assert cfg.allow_chrono_crystals is False
    assert cfg.max_defeats_per_stage == 3


def test_window_pattern_and_timeouts_can_be_overridden(tmp_path: Path):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(
        "window_title_pattern: 'BlueStacks App Player 1'\n"
        "soft_recovery_seconds: 10\n"
        "navigation_recovery_seconds: 30\n",
        encoding="utf-8",
    )

    cfg = load_config(cfg_file)

    assert cfg.window_title_pattern == "BlueStacks App Player 1"
    assert cfg.soft_recovery_seconds == 10
    assert cfg.navigation_recovery_seconds == 30
