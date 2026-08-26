from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import cv2

from dbl_farmer.vision.capture import ScreenCapture
from dbl_farmer.vision.window import BlueStacksWindowResolver


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture a DBL UI template inside BlueStacks")
    parser.add_argument("--group", required=True, help="Semantic folder, e.g. home or popup")
    parser.add_argument("--name", required=True, help="Template name without .png")
    parser.add_argument("--window", default="BlueStacks App Player", help="BlueStacks window title substring")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    resolver = BlueStacksWindowResolver()
    bounds = resolver.find(args.window)
    print(
        f"BlueStacks bounds: left={bounds.left}, top={bounds.top}, "
        f"width={bounds.width}, height={bounds.height}"
    )

    frame = ScreenCapture().grab(bounds)
    bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    roi = cv2.selectROI("Select DBL template", bgr, showCrosshair=True, fromCenter=False)
    cv2.destroyAllWindows()

    x, y, width, height = map(int, roi)
    if width <= 0 or height <= 0:
        print("Selection cancelled.")
        return 1
    if x < 0 or y < 0 or x + width > bounds.width or y + height > bounds.height:
        raise ValueError("Selected rectangle is outside the BlueStacks window")

    crop = bgr[y : y + height, x : x + width]
    destination = ROOT / "assets" / "templates" / args.group / f"{args.name}.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(destination), crop):
        raise RuntimeError(f"Could not write {destination}")

    print(f"Saved: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
