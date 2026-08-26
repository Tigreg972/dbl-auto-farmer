from __future__ import annotations

import argparse
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Callable

from dbl_farmer.config import AppConfig, load_config
from dbl_farmer.core.state_machine import StateMachine
from dbl_farmer.farm.objectives import ObjectiveQueue
from dbl_farmer.farm.resources import ResourceManager
from dbl_farmer.input.clicker import SafeClicker
from dbl_farmer.logging.session_log import SessionLogger
from dbl_farmer.navigation.router import NavigationRouter
from dbl_farmer.recovery.manager import RecoveryManager
from dbl_farmer.vision.detector import ScreenDetector
from dbl_farmer.vision.states import default_state_definitions
from dbl_farmer.vision.window import BlueStacksWindowResolver, WindowBounds


class RuntimeApp:
    def __init__(
        self,
        *,
        config: AppConfig,
        machine: StateMachine,
        logger: SessionLogger,
        clicker: SafeClicker,
        resolver: BlueStacksWindowResolver,
        dry_run: bool,
        action_points: dict[str, tuple[float, float]] | None = None,
    ) -> None:
        self.config = config
        self.machine = machine
        self.logger = logger
        self.clicker = clicker
        self.resolver = resolver
        self.dry_run = dry_run
        self.action_points = action_points or {}
        self._bounds: WindowBounds | None = None

    def process_once(self, frame=None, now: float | None = None):
        now = time.monotonic() if now is None else now
        result = self.machine.step(frame=frame, now=now)
        self.logger.stats.last_action = result.action
        self.logger.event("Action decided", action=result.action, dry_run=self.dry_run)

        if self.dry_run:
            return result

        point = self.action_points.get(result.action)
        if point is None:
            self.logger.event("No click mapping for action", action=result.action)
            return result

        bounds = self._bounds or self.resolver.find(self.config.window_title_pattern)
        self._bounds = bounds
        self.clicker.click_relative(bounds, *point)
        return result


class ControlWindow:
    def __init__(self, logger: SessionLogger):
        self.logger = logger
        self.root = tk.Tk()
        self.root.title("DBL Auto Farmer")
        self.root.resizable(False, False)
        self.running = False
        self.paused = False

        self.status_var = tk.StringVar(value="Stopped")
        self.state_var = tk.StringVar(value="UNKNOWN")
        self.objective_var = tk.StringVar(value="-")
        self.action_var = tk.StringVar(value="-")
        self.energy_var = tk.StringVar(value="0")
        self.skip_var = tk.StringVar(value="0")
        self.success_var = tk.StringVar(value="0")
        self.blocked_var = tk.StringVar(value="0")
        self.defeats_var = tk.StringVar(value="0")

        frame = ttk.Frame(self.root, padding=12)
        frame.grid(sticky="nsew")
        rows = [
            ("Status", self.status_var),
            ("State", self.state_var),
            ("Objective", self.objective_var),
            ("Last action", self.action_var),
            ("Energy used", self.energy_var),
            ("Skip Tickets used", self.skip_var),
            ("Successful stages", self.success_var),
            ("Blocked stages", self.blocked_var),
            ("Current defeats", self.defeats_var),
            ("Chrono Crystals spent", tk.StringVar(value="0")),
        ]
        for row, (label, variable) in enumerate(rows):
            ttk.Label(frame, text=f"{label}:").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=2)
            ttk.Label(frame, textvariable=variable).grid(row=row, column=1, sticky="w", pady=2)

        buttons = ttk.Frame(frame)
        buttons.grid(row=len(rows), column=0, columnspan=2, pady=(10, 0))
        ttk.Button(buttons, text="Start", command=self.start).grid(row=0, column=0, padx=3)
        ttk.Button(buttons, text="Pause", command=self.pause).grid(row=0, column=1, padx=3)
        ttk.Button(buttons, text="Stop", command=self.stop).grid(row=0, column=2, padx=3)
        self.root.after(250, self.refresh)

    def start(self) -> None:
        self.running = True
        self.paused = False
        self.status_var.set("Running")

    def pause(self) -> None:
        if self.running:
            self.paused = not self.paused
            self.status_var.set("Paused" if self.paused else "Running")

    def stop(self) -> None:
        self.running = False
        self.paused = False
        self.status_var.set("Stopped")

    def refresh(self) -> None:
        s = self.logger.stats
        self.state_var.set(s.current_state)
        self.objective_var.set(s.current_objective or "-")
        self.action_var.set(s.last_action or "-")
        self.energy_var.set(str(s.energy_used))
        self.skip_var.set(str(s.skip_tickets_used))
        self.success_var.set(str(s.successful_stages))
        self.blocked_var.set(str(s.blocked_stages))
        self.defeats_var.set(str(s.current_defeats))
        self.root.after(250, self.refresh)

    def run(self) -> None:
        self.root.mainloop()


def _default_click(x: int, y: int) -> None:
    import pyautogui

    pyautogui.click(x, y)


def build_runtime(
    *,
    dry_run: bool,
    config_path: Path | str = Path("config.yaml"),
    click_fn: Callable[[int, int], None] | None = None,
    window_provider=None,
    action_points: dict[str, tuple[float, float]] | None = None,
) -> RuntimeApp:
    config = load_config(Path(config_path))
    logger = SessionLogger(Path("logs"))
    detector = ScreenDetector(default_state_definitions())
    objectives = ObjectiveQueue([])
    resources = ResourceManager()
    recovery = RecoveryManager(
        soft_after=config.soft_recovery_seconds,
        navigation_after=config.navigation_recovery_seconds,
        max_failures=config.max_recovery_failures,
    )
    router = NavigationRouter()
    machine = StateMachine(
        detector=detector,
        router=router,
        objectives=objectives,
        resources=resources,
        recovery=recovery,
        resource_context_provider=lambda: None,
    )
    clicker = SafeClicker(click_fn or _default_click)
    resolver = BlueStacksWindowResolver(window_provider=window_provider)
    return RuntimeApp(
        config=config,
        machine=machine,
        logger=logger,
        clicker=clicker,
        resolver=resolver,
        dry_run=dry_run,
        action_points=action_points,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DBL Auto Farmer")
    parser.add_argument("--dry-run", action="store_true", help="Detect and log actions without clicking")
    parser.add_argument("--config", type=Path, default=Path("config.yaml"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    runtime = build_runtime(dry_run=args.dry_run, config_path=args.config)
    runtime.logger.event("Runtime initialized", dry_run=args.dry_run)
    print("DBL Auto Farmer initialized.")
    print("Dry-run:" if args.dry_run else "Live mode:", args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
