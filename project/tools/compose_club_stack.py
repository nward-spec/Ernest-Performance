#!/usr/bin/env python3
"""
compose_club_stack.py — pre-render a golf club into one aligned PNG.

Why this exists
---------------
Manufacturer product photos of club HEADS are shot at an angle and have a short
diagonal shaft stub baked into the image at the hosel. A separate straight SHAFT
image cannot be lined up with that baked-in stub using CSS transforms in the
carousel HTML — you always get a visible kink or a doubled shaft at the hosel.

So we composite in Pillow instead: rotate the shaft to continue the head's TRUE
hosel axis, drop the grip on the top end of the shaft, flatten to a single RGBA
PNG, and let the HTML place that finished image. No CSS alignment of components.

Manifest (assets/products/manifest.json)
----------------------------------------
{
  "canvas":  {"w": 900, "h": 2400, "bg": [0, 0, 0, 0]},
  "clubs": {
    "driver": {
      "head":  "raw/driver-head.png",
      "shaft": "raw/driver-shaft.png",
      "grip":  "raw/driver-grip.png",

      // Where the shaft physically enters the head, in HEAD-image pixels.
      "hosel":       [512, 88],
      // Direction the real shaft leaves the hosel, degrees clockwise from
      // straight-up (0 = vertical, positive tilts the top to the right).
      "hosel_angle": 8.0,

      // Optional per-part scaling relative to the head (1.0 = as supplied).
      "head_scale":  1.0,
      "shaft_scale": 1.0,
      "grip_scale":  1.0,

      // How far up the shaft the grip sits, as a fraction of shaft length
      // (0 = butt end, measured from the top). Usually leave at 0.0.
      "grip_overlap": 0.0
    }
  }
}

Coordinates are dialled in per club because every manufacturer photo is framed
differently. When a stack looks wrong, adjust `hosel` / `hosel_angle` here and
re-run — never compensate in the HTML.

Usage
-----
    python tools/compose_club_stack.py --all
    python tools/compose_club_stack.py --club driver
    python tools/compose_club_stack.py --club driver --debug   # draw the axis
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit(
        "Pillow is required: pip install Pillow\n"
        "(the compositor cannot run without it)"
    )

# project/tools/compose_club_stack.py -> project/
ROOT = Path(__file__).resolve().parent.parent
PRODUCTS = ROOT / "assets" / "products"
MANIFEST = PRODUCTS / "manifest.json"
STACK_DIR = PRODUCTS / "stack"


def _load(path_str: str) -> Image.Image:
    """Load an image from a manifest-relative (or absolute) path as RGBA."""
    p = Path(path_str)
    if not p.is_absolute():
        p = PRODUCTS / p
    if not p.exists():
        raise FileNotFoundError(f"source image not found: {p}")
    return Image.open(p).convert("RGBA")


def _scale(img: Image.Image, factor: float) -> Image.Image:
    if factor == 1.0:
        return img
    w, h = img.size
    return img.resize((max(1, round(w * factor)), max(1, round(h * factor))), Image.LANCZOS)


def _paste(base: Image.Image, top: Image.Image, cx: int, cy: int) -> None:
    """Alpha-composite `top` onto `base` centered at (cx, cy)."""
    x = round(cx - top.width / 2)
    y = round(cy - top.height / 2)
    base.alpha_composite(top, (x, y))


def compose_club(name: str, spec: dict, canvas: dict, debug: bool = False) -> Image.Image:
    """Composite one club (head + shaft + grip) into a single aligned RGBA image."""
    cw, ch = canvas["w"], canvas["h"]
    bg = tuple(canvas.get("bg", [0, 0, 0, 0]))
    out = Image.new("RGBA", (cw, ch), bg)

    head = _scale(_load(spec["head"]), spec.get("head_scale", 1.0))
    shaft = _scale(_load(spec["shaft"]), spec.get("shaft_scale", 1.0))
    grip = _scale(_load(spec["grip"]), spec.get("grip_scale", 1.0))

    angle = float(spec.get("hosel_angle", 0.0))
    # Head hosel point in ORIGINAL head-image pixels, adjusted for head_scale.
    hx, hy = spec["hosel"]
    hs = spec.get("head_scale", 1.0)
    hx, hy = hx * hs, hy * hs

    # Anchor the head so its hosel lands on the canvas center-x, near the bottom.
    # Place the head so that its hosel point (hx, hy) sits at (hosel_cx, hosel_cy).
    hosel_cx = cw // 2
    hosel_cy = ch - head.height // 2  # tune via canvas height / head_scale
    out.alpha_composite(head, (round(hosel_cx - hx), round(hosel_cy - hy)))

    # Rotate the shaft to the hosel axis (expand=True keeps it uncropped).
    # PIL rotates counter-clockwise for positive angles, so negate to make a
    # positive hosel_angle tilt the top of the shaft to the right.
    shaft_rot = shaft.rotate(-angle, expand=True, resample=Image.BICUBIC)

    # The shaft's BOTTOM end meets the hosel; it extends upward along the axis.
    # Approximate placement: center the rotated shaft so its bottom edge sits at
    # the hosel, offset along the axis by half its (rotated) height.
    import math

    theta = math.radians(angle)
    half_h = shaft_rot.height / 2
    shaft_cx = hosel_cx + math.sin(theta) * half_h
    shaft_cy = hosel_cy - math.cos(theta) * half_h
    _paste(out, shaft_rot, round(shaft_cx), round(shaft_cy))

    # Grip sits on the top (butt) end of the shaft, along the same axis.
    # Walk from the hosel up the axis by the visible shaft length, then up by
    # half the grip height so the grip's lower end overlaps the shaft top.
    overlap = float(spec.get("grip_overlap", 0.0))
    grip_rot = grip.rotate(-angle, expand=True, resample=Image.BICUBIC)
    top_cx = hosel_cx + math.sin(theta) * (shaft_rot.height * (1.0 - overlap))
    top_cy = hosel_cy - math.cos(theta) * (shaft_rot.height * (1.0 - overlap))
    grip_cx = top_cx + math.sin(theta) * (grip_rot.height / 2)
    grip_cy = top_cy - math.cos(theta) * (grip_rot.height / 2)
    _paste(out, grip_rot, round(grip_cx), round(grip_cy))

    if debug:
        d = ImageDraw.Draw(out)
        # Draw the hosel axis so anchor tuning is visible.
        x0, y0 = hosel_cx, hosel_cy
        x1 = hosel_cx + math.sin(theta) * ch
        y1 = hosel_cy - math.cos(theta) * ch
        d.line([(x0, y0), (x1, y1)], fill=(255, 0, 0, 200), width=3)
        d.ellipse([x0 - 6, y0 - 6, x0 + 6, y0 + 6], outline=(255, 0, 0, 255), width=3)

    return out.crop(out.getbbox() or (0, 0, cw, ch))


def main() -> int:
    ap = argparse.ArgumentParser(description="Composite golf club stacks from a manifest.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true", help="compose every club in the manifest")
    g.add_argument("--club", help="compose a single named club")
    ap.add_argument("--debug", action="store_true", help="draw the hosel axis for tuning")
    ap.add_argument("--manifest", default=str(MANIFEST), help="path to manifest.json")
    args = ap.parse_args()

    mpath = Path(args.manifest)
    if not mpath.exists():
        sys.exit(f"manifest not found: {mpath}\n(see the docstring for its shape)")
    data = json.loads(mpath.read_text())
    canvas = data.get("canvas", {"w": 900, "h": 2400, "bg": [0, 0, 0, 0]})
    clubs = data["clubs"]

    STACK_DIR.mkdir(parents=True, exist_ok=True)
    names = list(clubs) if args.all else [args.club]

    ok = True
    for name in names:
        if name not in clubs:
            print(f"  ! no such club in manifest: {name}", file=sys.stderr)
            ok = False
            continue
        try:
            img = compose_club(name, clubs[name], canvas, debug=args.debug)
            dest = STACK_DIR / f"{name}-stack.png"
            img.save(dest)
            print(f"  ✓ {name} -> {dest.relative_to(ROOT)}  ({img.width}x{img.height})")
        except (FileNotFoundError, KeyError) as e:
            print(f"  ! {name}: {e}", file=sys.stderr)
            ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
