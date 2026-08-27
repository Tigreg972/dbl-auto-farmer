from __future__ import annotations

import argparse
import sys
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import cv2

from dbl_farmer.calibration.manifest import TemplateSpec, missing_templates, template_specs
from dbl_farmer.vision.capture import ScreenCapture
from dbl_farmer.vision.window import BlueStacksWindowResolver, WindowNotFoundError


class CalibrationWindow:
    def __init__(self, window_pattern: str = "BlueStacks App Player") -> None:
        self.window_pattern = window_pattern
        self.template_root = ROOT / "assets" / "templates"
        self.specs = list(template_specs())
        self.root = tk.Tk()
        self.root.title("DBL Auto Farmer - Calibration")
        self.root.geometry("900x620")
        self.root.minsize(760, 480)

        header = ttk.Frame(self.root, padding=10)
        header.pack(fill="x")
        ttk.Label(
            header,
            text="DBL Auto Farmer - Calibration de l’interface",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            header,
            text=(
                "Sélectionne un élément, affiche l’écran correspondant dans Dragon Ball Legends sur BlueStacks, "
                "puis clique sur « Capturer la sélection ». Garde la même taille de fenêtre BlueStacks pendant toute la calibration."
            ),
            wraplength=840,
        ).pack(anchor="w", pady=(4, 0))

        body = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        body.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            body,
            columns=("status", "required", "path", "description"),
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("status", text="Statut")
        self.tree.heading("required", text="Type")
        self.tree.heading("path", text="Modèle")
        self.tree.heading("description", text="Élément à capturer")
        self.tree.column("status", width=80, anchor="center", stretch=False)
        self.tree.column("required", width=95, anchor="center", stretch=False)
        self.tree.column("path", width=250, stretch=False)
        self.tree.column("description", width=430)
        scrollbar = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        footer = ttk.Frame(self.root, padding=10)
        footer.pack(fill="x")
        self.summary_var = tk.StringVar(value="")
        ttk.Label(footer, textvariable=self.summary_var).pack(side="left")
        ttk.Button(footer, text="Capturer la sélection", command=self.capture_selected).pack(side="right", padx=4)
        ttk.Button(footer, text="Supprimer la sélection", command=self.delete_selected).pack(side="right", padx=4)
        ttk.Button(footer, text="Actualiser", command=self.refresh).pack(side="right", padx=4)
        ttk.Button(footer, text="Fermer", command=self.root.destroy).pack(side="right", padx=4)

        self.refresh()

    def _selected_spec(self) -> TemplateSpec | None:
        selected = self.tree.selection()
        if not selected:
            return None
        return self.specs[int(selected[0])]

    def refresh(self) -> None:
        selected_path = None
        current = self._selected_spec()
        if current is not None:
            selected_path = current.path

        for item in self.tree.get_children():
            self.tree.delete(item)

        captured = 0
        required_captured = 0
        required_total = sum(spec.required for spec in self.specs)
        for index, spec in enumerate(self.specs):
            exists = (self.template_root / spec.path).exists()
            captured += int(exists)
            required_captured += int(exists and spec.required)
            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    "OK" if exists else "Manquant",
                    "Obligatoire" if spec.required else "Optionnel",
                    spec.path,
                    spec.description,
                ),
            )
            if selected_path == spec.path:
                self.tree.selection_set(str(index))
                self.tree.see(str(index))

        self.summary_var.set(
            f"Capturés : {captured}/{len(self.specs)} | Obligatoires : {required_captured}/{required_total}"
        )

    def capture_selected(self) -> None:
        spec = self._selected_spec()
        if spec is None:
            messagebox.showinfo("Calibration", "Sélectionne d’abord un élément à capturer.")
            return

        try:
            bounds = BlueStacksWindowResolver().find(self.window_pattern)
        except WindowNotFoundError as exc:
            messagebox.showerror("BlueStacks introuvable", str(exc))
            return

        self.root.withdraw()
        self.root.update_idletasks()
        time.sleep(0.25)
        try:
            frame = ScreenCapture().grab(bounds)
            bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            title = f"Capture : {spec.path} | ENTRÉE = enregistrer | ÉCHAP = annuler"
            x, y, width, height = map(
                int,
                cv2.selectROI(title, bgr, showCrosshair=True, fromCenter=False),
            )
            cv2.destroyAllWindows()
            if width <= 0 or height <= 0:
                return
            if x < 0 or y < 0 or x + width > bounds.width or y + height > bounds.height:
                messagebox.showerror("Sélection invalide", "La zone sélectionnée dépasse de la fenêtre BlueStacks.")
                return

            crop = bgr[y : y + height, x : x + width]
            destination = self.template_root / spec.path
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not cv2.imwrite(str(destination), crop):
                raise RuntimeError(f"Impossible d’enregistrer {destination}")
        finally:
            self.root.deiconify()
            self.root.lift()
            self.refresh()

    def delete_selected(self) -> None:
        spec = self._selected_spec()
        if spec is None:
            return
        path = self.template_root / spec.path
        if path.exists():
            path.unlink()
        self.refresh()

    def run(self) -> None:
        self.root.mainloop()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Outil de calibration de DBL Auto Farmer")
    parser.add_argument("--window", default="BlueStacks App Player", help="Titre ou partie du titre de la fenêtre BlueStacks")
    parser.add_argument("--list", action="store_true", help="Afficher l’état de la calibration puis quitter")
    parser.add_argument(
        "--required-only",
        action="store_true",
        help="Avec --list, afficher uniquement les captures obligatoires manquantes",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.list:
        root = ROOT / "assets" / "templates"
        missing = missing_templates(root, required_only=args.required_only)
        if not missing:
            print("Toutes les captures demandées sont présentes.")
            return 0
        for spec in missing:
            kind = "obligatoire" if spec.required else "optionnel"
            print(f"[{kind}] {spec.path} - {spec.description}")
        return 1

    CalibrationWindow(window_pattern=args.window).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
