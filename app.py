from __future__ import annotations

import argparse
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Callable

from dbl_farmer.battle.runner import BattleRunner
from dbl_farmer.config import AppConfig, load_config
from dbl_farmer.core.state_machine import StateMachine
from dbl_farmer.farm.objectives import build_default_objectives
from dbl_farmer.farm.resources import ResourceManager
from dbl_farmer.farm.visual_resources import VisualResourceContextProvider
from dbl_farmer.input.executor import ActionExecutor
from dbl_farmer.logging.session_log import SessionLogger
from dbl_farmer.navigation.router import NavigationRouter
from dbl_farmer.recovery.manager import RecoveryManager
from dbl_farmer.ui.fr import action_label, objective_label, state_label, status_label
from dbl_farmer.vision.capture import ScreenCapture
from dbl_farmer.vision.detector import ScreenDetector
from dbl_farmer.vision.states import default_state_definitions
from dbl_farmer.vision.window import BlueStacksWindowResolver, WindowBounds, WindowNotFoundError


class RuntimeApp:
    def __init__(
        self,
        *,
        config: AppConfig,
        machine: StateMachine,
        logger: SessionLogger,
        resolver: BlueStacksWindowResolver,
        capture: ScreenCapture,
        executor: ActionExecutor,
        dry_run: bool,
        context_observer=None,
    ) -> None:
        self.config = config
        self.machine = machine
        self.logger = logger
        self.resolver = resolver
        self.capture = capture
        self.executor = executor
        self.dry_run = dry_run
        self.context_observer = context_observer
        self._bounds: WindowBounds | None = None

    def process_once(self, frame=None, now: float | None = None):
        now = time.monotonic() if now is None else now
        try:
            bounds = self.resolver.find(self.config.window_title_pattern)
            self._bounds = bounds
        except WindowNotFoundError:
            if not self.dry_run or frame is not None:
                raise
            bounds = WindowBounds(0, 0, 1, 1)

        if frame is None and self._bounds is not None:
            frame = self.capture.grab(bounds)

        if self.context_observer is not None:
            self.context_observer.update(frame)

        result = self.machine.step(frame=frame, now=now)
        data = result.data if isinstance(result.data, dict) else {}
        state = data.get("state")
        objective_id = data.get("objective_id")
        if state is not None:
            self.logger.stats.current_state = getattr(state, "name", str(state))
        self.logger.stats.current_objective = objective_id or ""
        self.logger.stats.last_action = result.action
        self.logger.event(
            "Action décidée",
            etat=state_label(self.logger.stats.current_state),
            objectif=objective_label(objective_id or "-"),
            action=action_label(result.action),
            test_sans_clic=self.dry_run,
        )

        if self.dry_run:
            return result

        execution = self.executor.execute(result.action, frame=frame, bounds=bounds)
        notify = getattr(self.machine, "notify_execution", None)
        if callable(notify):
            try:
                notify(result.action, execution.executed, execution.configured)
            except TypeError:
                notify(result.action, execution.executed)
        self.logger.event(
            "Exécution de l’action",
            action=action_label(result.action),
            executee=execution.executed,
            cible=execution.target,
            point=execution.point,
            detail=execution.message,
        )
        return result

    def run_until(
        self,
        stop_event: threading.Event,
        pause_event: threading.Event,
        *,
        interval: float = 0.6,
    ) -> None:
        while not stop_event.is_set():
            if pause_event.is_set():
                time.sleep(0.1)
                continue
            try:
                self.process_once()
            except Exception as exc:
                self.logger.event("Erreur d’exécution", erreur=repr(exc))
            time.sleep(interval)


class ControlWindow:
    def __init__(self, runtime: RuntimeApp):
        self.runtime = runtime
        self.logger = runtime.logger
        self.root = tk.Tk()
        self.root.title("DBL Auto Farmer - Contrôle")
        self.root.resizable(False, False)
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._worker: threading.Thread | None = None

        self.status_var = tk.StringVar(value=status_label("Stopped"))
        self.state_var = tk.StringVar(value=state_label("UNKNOWN"))
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
            ("Statut", self.status_var),
            ("Écran détecté", self.state_var),
            ("Objectif", self.objective_var),
            ("Dernière action", self.action_var),
            ("Énergie utilisée", self.energy_var),
            ("Tickets skip utilisés", self.skip_var),
            ("Niveaux réussis", self.success_var),
            ("Niveaux bloqués", self.blocked_var),
            ("Défaites sur le niveau actuel", self.defeats_var),
            ("Chrono Crystals dépensés", tk.StringVar(value="0")),
        ]
        for row, (label, variable) in enumerate(rows):
            ttk.Label(frame, text=f"{label} :").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=2)
            ttk.Label(frame, textvariable=variable).grid(row=row, column=1, sticky="w", pady=2)

        buttons = ttk.Frame(frame)
        buttons.grid(row=len(rows), column=0, columnspan=2, pady=(10, 0))
        ttk.Button(buttons, text="Démarrer", command=self.start).grid(row=0, column=0, padx=3)
        ttk.Button(buttons, text="Pause", command=self.pause).grid(row=0, column=1, padx=3)
        ttk.Button(buttons, text="Arrêter", command=self.stop).grid(row=0, column=2, padx=3)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(250, self.refresh)

    def start(self) -> None:
        if self._worker is not None and self._worker.is_alive():
            self._pause_event.clear()
            self.status_var.set(status_label("Running"))
            return
        self._stop_event.clear()
        self._pause_event.clear()
        self._worker = threading.Thread(
            target=self.runtime.run_until,
            args=(self._stop_event, self._pause_event),
            daemon=True,
        )
        self._worker.start()
        self.status_var.set(status_label("Running"))

    def pause(self) -> None:
        if self._worker is None or not self._worker.is_alive():
            return
        if self._pause_event.is_set():
            self._pause_event.clear()
            self.status_var.set(status_label("Running"))
        else:
            self._pause_event.set()
            self.status_var.set(status_label("Paused"))

    def stop(self) -> None:
        self._stop_event.set()
        self._pause_event.clear()
        self.status_var.set(status_label("Stopped"))

    def close(self) -> None:
        self.stop()
        self.root.destroy()

    def refresh(self) -> None:
        s = self.logger.stats
        self.state_var.set(state_label(s.current_state))
        self.objective_var.set(objective_label(s.current_objective or "-"))
        self.action_var.set(action_label(s.last_action or "-"))
        self.energy_var.set(str(s.energy_used))
        self.skip_var.set(str(s.skip_tickets_used))
        self.success_var.set(str(s.successful_stages))
        self.blocked_var.set(str(s.blocked_stages))
        self.defeats_var.set(str(s.current_defeats))
        if self.root.winfo_exists():
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
) -> RuntimeApp:
    config = load_config(Path(config_path))
    logger = SessionLogger(Path("logs"))
    detector = ScreenDetector(default_state_definitions())
    objectives = build_default_objectives(
        enable_story=config.enable_story,
        enable_events=config.enable_events,
    )
    resources = ResourceManager()
    visual_resources = VisualResourceContextProvider(
        template_root=Path("assets/templates"),
        threshold=config.detection_threshold,
    )
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
        resource_context_provider=visual_resources.current,
        battle_runner=BattleRunner(max_defeats=config.max_defeats_per_stage),
    )
    resolver = BlueStacksWindowResolver(window_provider=window_provider)
    capture = ScreenCapture()
    executor = ActionExecutor(
        template_root=Path("assets/templates"),
        click_fn=click_fn or _default_click,
    )
    return RuntimeApp(
        config=config,
        machine=machine,
        logger=logger,
        resolver=resolver,
        capture=capture,
        executor=executor,
        dry_run=dry_run,
        context_observer=visual_resources,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DBL Auto Farmer")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Détecter et journaliser les actions sans effectuer de clic",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Chemin du fichier de configuration",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    runtime = build_runtime(dry_run=args.dry_run, config_path=args.config)
    runtime.logger.event("Moteur initialisé", test_sans_clic=args.dry_run)
    ControlWindow(runtime).run()
    print(runtime.logger.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
