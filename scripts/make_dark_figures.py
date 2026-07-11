#!/usr/bin/env python3
"""Create dark-theme variants of the paper figures without redrawing content."""

from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "static" / "images"
DARK = np.array([10, 13, 18], dtype=np.float32)   # website --bg
LIGHT = np.array([232, 234, 237], dtype=np.float32)  # website --ink


def rectangles(columns, rows):
    return [(x0, y0, x1, y1) for x0, x1 in columns for y0, y1 in rows]


# Normalized rectangles protect photographic/simulation panels from recoloring.
PROTECTED = {
    "figure1_eel_c_start_optimal_timepoints.png": rectangles(
        [
            (0.052, 0.172), (0.180, 0.300), (0.309, 0.429),
            (0.437, 0.557), (0.565, 0.685), (0.693, 0.813),
            (0.821, 0.941),
        ],
        [(0.044, 0.316), (0.619, 0.891)],
    ),
    "figure9_eel_forward_swimming_timepoints.png": rectangles(
        [
            (0.061, 0.223), (0.234, 0.396), (0.407, 0.568),
            (0.580, 0.741), (0.752, 0.914),
        ],
        [(0.031, 0.313), (0.626, 0.902)],
    ),
}

TARGETS = [
    "figure1_eel_c_start_optimal_timepoints.png",
    "figure3_physics_comparison.png",
    "figure8_rmse_comparison.png",
    "figure9_eel_forward_swimming_timepoints.png",
]


def darken_figure(name):
    source = IMAGE_DIR / name
    image = np.asarray(Image.open(source).convert("RGB"), dtype=np.float32)
    height, width, _ = image.shape

    # Only remap near-neutral pixels. The paper's semantic colors are preserved.
    chroma = image.max(axis=2) - image.min(axis=2)
    neutral = chroma <= 24

    if name in PROTECTED:
        editable = np.ones((height, width), dtype=bool)
        for x0, y0, x1, y1 in PROTECTED[name]:
            editable[
                round(y0 * height):round(y1 * height),
                round(x0 * width):round(x1 * width),
            ] = False
        neutral &= editable

    luminance = image.mean(axis=2) / 255.0
    mapped = DARK + (1.0 - luminance[..., None]) * (LIGHT - DARK)
    result = image.copy()
    result[neutral] = mapped[neutral]

    output = source.with_name(f"{source.stem}_dark.png")
    Image.fromarray(np.clip(result, 0, 255).astype(np.uint8)).save(
        output, optimize=True
    )
    print(output.relative_to(ROOT))


if __name__ == "__main__":
    for target in TARGETS:
        darken_figure(target)
