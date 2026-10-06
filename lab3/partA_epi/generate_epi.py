"""
Part A - Epipolar Plane Images (EPI)

Reads a video of a horizontally-translating camera looking at a static scene
with objects at different depths, and produces:
  1. A horizontal EPI (fixed row y, stacked over time)
  2. A perpendicular EPI (fixed column x, stacked over time)
  3. The same two EPIs after painting a fixed-image-coordinate colored patch
     onto every frame (to show the difference between real scene motion and
     an artifact that is glued to the screen instead of the world).

Usage:
    python generate_epi.py

Edit the CONFIG block below to point at your video and to choose the row/
column/patch that make sense for your scene.
"""

import cv2
import numpy as np
from pathlib import Path

# ----------------------------- CONFIG --------------------------------------
VIDEO_PATH = "data/IMG_2207_no_person.mp4"  # input video (camera translates sideways)
OUT_DIR = Path("output")

# The assignment defines `mid` as the midpoint of the rows/columns
# (vid(mid,:,:,:) / vid(:,mid,:,:)) as the starting point, then explicitly
# asks you to "try different locations of mid". We tried the true geometric
# midpoint first (see MIDPOINT_EXPLORATION below) and found it worse than
# these values, so these are the final, deliberately-chosen locations:
ROW_Y = 720          # row used for the horizontal EPI  (vid(ROW_Y, :, :, :))
COL_X = 1080         # column used for the perpendicular EPI (vid(:, COL_X, :, :))

# Set to True to ALSO render the true-midpoint (H//2, W//2) EPIs into
# output/midpoint_exploration/, to document the "try different locations of
# mid" comparison required by step 6 of the assignment.
SAVE_MIDPOINT_EXPLORATION = True

# Patch is defined in (row, col) image coordinates: (y0, y1, x0, x1).
# NOTE: for the patch to show up in BOTH the horizontal EPI (row=ROW_Y) and
# the perpendicular EPI (col=COL_X), the patch's y-range must include ROW_Y
# and its x-range must include COL_X.
PATCH = (650, 800, 1000, 1160)
PATCH_COLOR_BGR = (0, 0, 255)   # red, since OpenCV uses BGR
# -----------------------------------------------------------------------------


def load_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")

    frames = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
    cap.release()

    if not frames:
        raise RuntimeError("No frames read from video.")

    return frames  # list of H x W x 3 (BGR) arrays


def make_horizontal_epi(frames, row_y):
    """EPI(x, t) = frame_t[row_y, x, :] -> shape (T, W, 3)"""
    rows = [f[row_y, :, :].copy() for f in frames]
    return np.stack(rows, axis=0)


def make_perpendicular_epi(frames, col_x):
    """EPI(y, t) = frame_t[:, col_x, :] -> shape (H, T, 3)"""
    cols = [f[:, col_x, :].copy() for f in frames]
    return np.stack(cols, axis=1)


def add_fixed_patch(frames, patch, color_bgr):
    """Paint the same rectangular region of image coordinates on every frame.

    Because the rectangle is defined in image (screen) coordinates and not
    tied to any 3D scene point, it will NOT show parallax as the camera
    moves -- unlike every real object in the scene.
    """
    y0, y1, x0, x1 = patch
    patched = []
    for f in frames:
        f2 = f.copy()
        f2[y0:y1, x0:x1] = color_bgr
        patched.append(f2)
    return patched


def main():
    OUT_DIR.mkdir(exist_ok=True)

    frames = load_frames(VIDEO_PATH)
    h, w = frames[0].shape[:2]
    print(f"Loaded {len(frames)} frames, each {w}x{h}")

    # --- true-midpoint EPIs, for documenting "try different locations of mid" ---
    if SAVE_MIDPOINT_EXPLORATION:
        mid_dir = OUT_DIR / "midpoint_exploration"
        mid_dir.mkdir(exist_ok=True)
        row_mid, col_mid = h // 2, w // 2
        epi_h_mid = make_horizontal_epi(frames, row_mid)
        epi_v_mid = make_perpendicular_epi(frames, col_mid)
        cv2.imwrite(str(mid_dir / f"EPI_horizontal_y{row_mid}_TRUE_MIDPOINT.png"), epi_h_mid)
        cv2.imwrite(str(mid_dir / f"EPI_perpendicular_x{col_mid}_TRUE_MIDPOINT.png"), epi_v_mid)
        print(f"Saved true-midpoint exploration EPIs (row={row_mid}, col={col_mid}).")

    # --- original EPIs (final chosen row/col) ---
    epi_h = make_horizontal_epi(frames, ROW_Y)
    epi_v = make_perpendicular_epi(frames, COL_X)
    cv2.imwrite(str(OUT_DIR / f"EPI_horizontal_y{ROW_Y}.png"), epi_h)
    cv2.imwrite(str(OUT_DIR / f"EPI_perpendicular_x{COL_X}.png"), epi_v)
    print("Saved original horizontal/perpendicular EPIs.")

    # --- save the scene photo (first frame) for the "picture of the scene" submission ---
    cv2.imwrite(str(OUT_DIR / "scene.jpg"), frames[0])

    # --- patched EPIs ---
    patched_frames = add_fixed_patch(frames, PATCH, PATCH_COLOR_BGR)
    epi_h_patch = make_horizontal_epi(patched_frames, ROW_Y)
    epi_v_patch = make_perpendicular_epi(patched_frames, COL_X)
    cv2.imwrite(str(OUT_DIR / f"EPI_horizontal_y{ROW_Y}_patch.png"), epi_h_patch)
    cv2.imwrite(str(OUT_DIR / f"EPI_perpendicular_x{COL_X}_patch.png"), epi_v_patch)
    print("Saved patched horizontal/perpendicular EPIs.")

    # optional: write out the patched video so you can eyeball the "HUD" effect
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(OUT_DIR / "patched_video.mp4"), fourcc, 30, (w, h))
    for f in patched_frames:
        writer.write(f)
    writer.release()
    print("Saved patched_video.mp4")

    print("\nShapes:")
    print("  horizontal EPI:", epi_h.shape)
    print("  perpendicular EPI:", epi_v.shape)


if __name__ == "__main__":
    main()
