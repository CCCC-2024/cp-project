"""Python equivalent of artlab.m for previewing the Lab 0 result."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_PATH = SCRIPT_DIR / "mountains.png"
QUANTIZED_PATH = SCRIPT_DIR / "best_quantized.png"
COMPARISON_PATH = SCRIPT_DIR / "matlab_comparison.png"
CANDIDATE_DIR = SCRIPT_DIR / "quantization_candidates"
LEVEL_COMPARISON_PATH = SCRIPT_DIR / "quantization_levels_comparison.png"


# Read the RGB image as a height-by-width-by-channel array.
original_image = Image.open(INPUT_PATH).convert("RGB")
im = np.asarray(original_image)

# Q1: MATLAB size(im) is equivalent to NumPy im.shape.
print(f"Image size (height, width, channels): {im.shape}")

# Q2: Extract the red, green, and blue channels.
red = im[:, :, 0]
green = im[:, :, 1]
blue = im[:, :, 2]

grayim = (
    red.astype(np.float64)
    + green.astype(np.float64)
    + blue.astype(np.float64)
) / 3

print(f"Gray minimum: {grayim.min():.2f}")
print(f"Gray maximum: {grayim.max():.2f}")
print(f"Gray range:   {np.ptp(grayim):.2f}")

# Q3: Reduce each RGB channel from 256 possible values to four values.
level1 = 50
level2 = 100
level3 = 150

quantim = np.empty_like(im)

for channel_index in range(3):
    source_channel = im[:, :, channel_index]

    quantim[:, :, channel_index] = np.select(
        [
            source_channel <= level1,
            (source_channel > level1) & (source_channel <= level2),
            (source_channel > level2) & (source_channel <= level3),
        ],
        [25, 75, 140],
        default=220,
    ).astype(np.uint8)

quantized_image = Image.fromarray(quantim)
quantized_image.save(QUANTIZED_PATH)

# Create a labeled side-by-side preview for easy inspection.
title_height = 45
gap = 12
comparison = Image.new(
    "RGB",
    (original_image.width * 2 + gap, original_image.height + title_height),
    "white",
)
comparison.paste(original_image, (0, title_height))
comparison.paste(quantized_image, (original_image.width + gap, title_height))

draw = ImageDraw.Draw(comparison)
draw.text((10, 14), "Original Image", fill="black")
draw.text((original_image.width + gap + 10, 14), "Quantized Image", fill="black")
comparison.save(COMPARISON_PATH)

print(f"Saved quantized image: {QUANTIZED_PATH}")
print(f"Saved comparison image: {COMPARISON_PATH}")


# Generate additional candidates with different numbers of uniform levels.
# With N levels per channel, the RGB image can contain at most N^3 colors.
def uniform_quantize(image_array: np.ndarray, levels: int) -> np.ndarray:
    """Quantize every RGB channel to evenly spaced output levels."""
    if levels < 2:
        raise ValueError("levels must be at least 2")

    scale = 255.0 / (levels - 1)
    quantized = np.rint(image_array.astype(np.float64) / scale) * scale
    return np.clip(np.rint(quantized), 0, 255).astype(np.uint8)


def comparison_font(size: int) -> ImageFont.ImageFont:
    """Use a readable macOS font, with a portable fallback."""
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


CANDIDATE_DIR.mkdir(exist_ok=True)
level_counts = [2, 3, 4, 5, 6, 8, 12, 16]
candidate_images = [("Original", original_image)]

for levels in level_counts:
    candidate_array = uniform_quantize(im, levels)
    candidate_image = Image.fromarray(candidate_array)
    candidate_path = CANDIDATE_DIR / f"quantized_{levels}_levels.png"
    candidate_image.save(candidate_path)
    candidate_images.append(
        (f"{levels} levels/channel (up to {levels ** 3} colors)", candidate_image)
    )
    print(f"Saved {levels}-level candidate: {candidate_path}")

# Arrange the original and eight candidates in one 3-by-3 contact sheet.
columns = 3
rows = 3
panel_width = 700
panel_height = 500
title_height = 55
thumbnail_area = (panel_width - 20, panel_height - title_height - 15)
sheet = Image.new(
    "RGB",
    (columns * panel_width, rows * panel_height),
    "white",
)
sheet_draw = ImageDraw.Draw(sheet)
font = comparison_font(24)

for index, (label, candidate_image) in enumerate(candidate_images):
    column = index % columns
    row = index // columns
    panel_x = column * panel_width
    panel_y = row * panel_height

    thumbnail = candidate_image.copy()
    thumbnail.thumbnail(thumbnail_area, Image.Resampling.LANCZOS)
    image_x = panel_x + (panel_width - thumbnail.width) // 2
    image_y = panel_y + title_height
    sheet.paste(thumbnail, (image_x, image_y))
    sheet_draw.text((panel_x + 15, panel_y + 15), label, fill="black", font=font)

sheet.save(LEVEL_COMPARISON_PATH)
print(f"Saved level comparison sheet: {LEVEL_COMPARISON_PATH}")
