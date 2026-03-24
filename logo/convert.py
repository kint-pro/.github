#!/usr/bin/env python3
"""Convert a logo source image into all required web asset formats.

Usage:
    python convert.py <source-image> [--output-dir <dir>]

Accepts: PNG, WebP, JPEG, BMP
Outputs: All formats in the correct directory structure.

Requires: Pillow, potrace (system binary for SVG tracing)
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image


def trace_svg_path(img_l: Image.Image) -> str:
    bmp = img_l.point(lambda p: 0 if p < 128 else 255, mode="1")
    tmp = Path("/tmp/_potrace_input.bmp")
    bmp.save(tmp)
    result = subprocess.run(
        ["potrace", str(tmp), "-s", "-o", "-", "--flat",
         "--turdsize", "5", "--alphamax", "1.0", "--opttolerance", "0.2"],
        capture_output=True, text=True, check=True,
    )
    tmp.unlink()
    match = re.search(r'<path d="([^"]+)"', result.stdout)
    if not match:
        sys.exit("ERROR: potrace produced no path data")
    return match.group(1)


def to_black_on_white(src: Image.Image) -> Image.Image:
    if src.mode in ("LA", "PA"):
        lum, alpha = src.split()
        bg = Image.new("L", src.size, 255)
        bg.paste(lum, mask=alpha)
        return bg
    if src.mode in ("RGBA",):
        bg = Image.new("RGBA", src.size, (255, 255, 255, 255))
        bg.paste(src, mask=src.split()[-1])
        return bg.convert("L")
    return src.convert("L")


def to_white_on_black(src: Image.Image) -> Image.Image:
    bw = to_black_on_white(src)
    return bw.point(lambda p: 255 - p)


def to_transparent(src: Image.Image, fg_white: bool) -> Image.Image:
    bw = to_black_on_white(src)
    if fg_white:
        bw = bw.point(lambda p: 255 - p)
    rgba = Image.new("RGBA", src.size, (0, 0, 0, 0))
    fg_val = 255 if fg_white else 0
    r = Image.new("L", src.size, fg_val)
    g = Image.new("L", src.size, fg_val)
    b = Image.new("L", src.size, fg_val)
    alpha = bw.point(lambda p: 255 - p) if not fg_white else bw
    return Image.merge("RGBA", (r, g, b, alpha))


def fit_in_square(img: Image.Image, size: int, padding: float = 0.98) -> Image.Image:
    w, h = img.size
    scale = min(size * padding / w, size * padding / h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - new_w) // 2
    y = (size - new_h) // 2
    canvas.paste(resized, (x, y), resized if resized.mode == "RGBA" else None)
    return canvas


def generate_all(src_path: Path, out: Path):
    src = Image.open(src_path)
    w, h = src.size
    print(f"Source: {src_path.name} ({w}x{h}, {src.mode})")

    os.makedirs(out / "favicons", exist_ok=True)
    os.makedirs(out / "logos", exist_ok=True)
    os.makedirs(out / "pwa", exist_ok=True)

    bw = to_black_on_white(src)

    # --- SVGs via potrace ---
    path_d = trace_svg_path(bw)
    vb = f"0 0 {w} {h}"
    tf = f"translate(0,{h}) scale(0.1,-0.1)"

    (out / "favicon.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">\n'
        f"<style>\npath {{ fill: #000000; }}\n"
        f"@media (prefers-color-scheme: dark) {{ path {{ fill: #ffffff; }} }}\n"
        f'</style>\n<g transform="{tf}"><path d="{path_d}"/></g>\n</svg>'
    )
    (out / "logos/kint-logo-black.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">\n'
        f'<g transform="{tf}" fill="#000000"><path d="{path_d}"/></g>\n</svg>'
    )
    (out / "logos/kint-logo-white.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">\n'
        f'<g transform="{tf}" fill="#ffffff"><path d="{path_d}"/></g>\n</svg>'
    )
    print("  SVGs: favicon.svg, logos/*.svg")

    # --- Raster logos (800x438) ---
    black_white = bw
    white_black = to_white_on_black(src)
    black_trans = to_transparent(src, fg_white=False)
    white_trans = to_transparent(src, fg_white=True)

    for name, img in [
        ("kint-logo-black-white-bg", black_white),
        ("kint-logo-white-black-bg", white_black),
        ("kint-logo-black-transparent", black_trans),
        ("kint-logo-white-transparent", white_trans),
    ]:
        if img.mode in ("L",):
            img.save(out / "logos" / f"{name}.png", optimize=True)
            img.convert("RGB").save(out / "logos" / f"{name}.webp", method=6)
        else:
            img.save(out / "logos" / f"{name}.png", optimize=True)
            img.save(out / "logos" / f"{name}.webp", method=6)
    print("  Logos: PNG + WebP variants")

    # --- Favicons ---
    black_sq = to_transparent(src, fg_white=False)
    for size in [16, 32, 48, 96, 128, 256]:
        icon = fit_in_square(black_sq, size)
        icon.save(out / "favicons" / f"favicon-{size}x{size}.png", optimize=True)

    ico = fit_in_square(black_sq, 32)
    ico.save(out / "favicons" / "favicon.ico", format="ICO", sizes=[(32, 32)])
    print("  Favicons: ICO + PNGs")

    # --- PWA icons ---
    for size in [192, 512]:
        icon = fit_in_square(black_sq, size)
        icon.save(out / "pwa" / f"android-chrome-{size}x{size}.png", optimize=True)

    # apple-touch-icon: no transparency, white bg
    apple = fit_in_square(black_sq, 180)
    apple_bg = Image.new("RGBA", (180, 180), (255, 255, 255, 255))
    apple_bg.paste(apple, mask=apple)
    apple_bg.convert("RGB").save(out / "pwa" / "apple-touch-icon.png", optimize=True)

    # maskable icons: 60% content area (40% radius safe zone)
    for size in [192, 512]:
        maskable = fit_in_square(black_sq, size, padding=0.8)
        mask_bg = Image.new("RGBA", (size, size), (255, 255, 255, 255))
        mask_bg.paste(maskable, mask=maskable)
        mask_bg.convert("RGB").save(out / "pwa" / f"maskable-icon-{size}x{size}.png", optimize=True)

    # mstiles
    for size in [150, 310]:
        tile = fit_in_square(black_sq, size)
        tile.save(out / "pwa" / f"mstile-{size}x{size}.png", optimize=True)
    print("  PWA: chrome, apple, maskable, mstile icons")

    # --- OG images ---
    for name, fg_img, bg_color in [
        ("og-image.png", black_trans, (255, 255, 255)),
        ("og-image-dark.png", white_trans, (17, 17, 17)),
    ]:
        og_w, og_h = 1200, 630
        target_w = int(og_w * 0.8)
        scale = target_w / w
        target_h = int(h * scale)
        resized = fg_img.resize((target_w, target_h), Image.LANCZOS)
        canvas = Image.new("RGBA", (og_w, og_h), (*bg_color, 255))
        x = (og_w - target_w) // 2
        y = (og_h - target_h) // 2
        canvas.paste(resized, (x, y), resized)
        canvas.convert("RGB").save(out / name, optimize=True)
    print("  OG images: light + dark")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate all logo assets from a source image")
    parser.add_argument("source", help="Source image (PNG, WebP, JPEG, BMP)")
    parser.add_argument("--output-dir", "-o", default=".", help="Output directory")
    args = parser.parse_args()

    src = Path(args.source)
    if not src.exists():
        sys.exit(f"ERROR: {src} not found")
    if not shutil.which("potrace"):
        sys.exit("ERROR: potrace not found. Install via: brew install potrace")

    generate_all(src, Path(args.output_dir))
