"""
Part B - render a rotating GIF of the COLMAP sparse reconstruction,
showing both the 3D points and the recovered camera positions.

Uses matplotlib's offscreen (Agg) renderer instead of open3d's windowed
visualizer, since a windowed/headless GL context isn't reliably available
in every shell environment (e.g. no WindowServer access).

Requires: pip install pycolmap imageio numpy matplotlib

Usage:
    python make_gif.py --model output/sparse/0 --out output/reconstruction.gif
"""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
import pycolmap
import imageio.v2 as imageio
from scipy.spatial.transform import Rotation


def load_colmap_model(model_path, min_track_length=3, max_error=1.0):
    """Load points + cameras, keeping only well-triangulated points.

    Points seen by very few images or with high reprojection error are
    usually spurious (background clutter, reflections, moving objects) --
    dropping them makes the point cloud look much more like the actual
    object instead of a noisy blob.
    """
    rec = pycolmap.Reconstruction(model_path)

    pts3d = list(rec.points3D.values())
    keep = np.array([p.track.length() >= min_track_length and p.error <= max_error for p in pts3d])

    points = np.array([p.xyz for p in pts3d])[keep]
    colors = (np.array([p.color for p in pts3d])[keep]) / 255.0

    # sort cameras by filename (frame_001.jpg, frame_002.jpg, ...) so the
    # trajectory line follows the actual video order instead of COLMAP's
    # internal (arbitrary) image-id order, which zig-zags across the scene.
    images = sorted(rec.images.values(), key=lambda im: im.name)
    cam_centers = np.array([image.projection_center() for image in images])

    print(f"Kept {keep.sum()}/{len(pts3d)} points after track-length/error filtering")
    return points, colors, cam_centers


def filter_outliers(points, colors, pct=1.0):
    """Drop the most extreme points so autoscale isn't dominated by noise."""
    center = np.median(points, axis=0)
    dist = np.linalg.norm(points - center, axis=1)
    keep = dist < np.percentile(dist, 100 - pct)
    return points[keep], colors[keep]


def set_equal_aspect(ax, center, radius):
    """matplotlib 3D axes don't preserve aspect ratio by default -- without
    this the point cloud looks stretched/squashed as it rotates."""
    ax.set_xlim(center[0] - radius, center[0] + radius)
    ax.set_ylim(center[1] - radius, center[1] + radius)
    ax.set_zlim(center[2] - radius, center[2] + radius)
    ax.set_box_aspect((1, 1, 1))


def align_orbit_to_horizontal(points, cam_centers):
    """COLMAP's world frame has an arbitrary orientation (no gravity
    reference), so a real horizontal camera orbit can come out tilted at any
    angle in the reconstructed coordinates. Fit a plane to the camera
    centers (they should be roughly coplanar, circling the object) and
    rotate everything so that plane becomes horizontal (z = const) -- purely
    cosmetic, does not change the reconstruction itself, just makes the
    rendered orbit match the physical one.
    """
    centroid = cam_centers.mean(axis=0)
    _, _, vt = np.linalg.svd(cam_centers - centroid)
    normal = vt[2]  # least-variance direction = plane normal

    z_axis = np.array([0.0, 0.0, 1.0])
    R = Rotation.align_vectors([z_axis], [normal])[0].as_matrix()

    points_aligned = (points - centroid) @ R.T
    cam_centers_aligned = (cam_centers - centroid) @ R.T

    # Orientation convention: when photographing a small tabletop object by
    # walking around it, the camera is typically held at or above the
    # object's height, not below it. Pick the sign of "up" so the camera
    # ring ends up at or above the object's point cloud, matching the real
    # physical setup instead of an arbitrarily-flipped one.
    if cam_centers_aligned[:, 2].mean() < points_aligned[:, 2].mean():
        points_aligned[:, 2] *= -1
        cam_centers_aligned[:, 2] *= -1

    return points_aligned, cam_centers_aligned


def trajectory_segments(cam_centers, outlier_factor=3.0):
    """Split the camera path into runs, breaking wherever a step is much
    larger than the typical step (a mis-registered pose), so the plotted
    trajectory doesn't draw a misleading straight line across the scene."""
    steps = np.linalg.norm(np.diff(cam_centers, axis=0), axis=1)
    median_step = np.median(steps)
    breaks = np.where(steps > outlier_factor * median_step)[0]

    segments = []
    start = 0
    for b in breaks:
        segments.append(cam_centers[start:b + 1])
        start = b + 1
    segments.append(cam_centers[start:])
    return [s for s in segments if len(s) > 1]


def render_rotation_gif(points, colors, cam_centers, out_path, n_frames=90, dpi=120):
    points, colors = filter_outliers(points, colors, pct=3.0)
    points, cam_centers = align_orbit_to_horizontal(points, cam_centers)
    path_segments = trajectory_segments(cam_centers)

    all_pts = np.vstack([points, cam_centers])
    center = all_pts.mean(axis=0)
    radius = np.linalg.norm(all_pts - center, axis=1).max() * 1.05

    fig = plt.figure(figsize=(7, 7), dpi=dpi)
    ax = fig.add_subplot(111, projection="3d")
    fig.patch.set_facecolor("white")

    frames = []
    for i in range(n_frames):
        ax.clear()
        ax.scatter(points[:, 0], points[:, 1], points[:, 2],
                   c=colors, s=4, marker=".", depthshade=True)
        # camera trajectory as connected line segments (broken at outlier
        # jumps) + markers, easier to read than isolated dots
        for seg in path_segments:
            ax.plot(seg[:, 0], seg[:, 1], seg[:, 2], c="red", linewidth=1.5, alpha=0.7)
        ax.scatter(cam_centers[:, 0], cam_centers[:, 1], cam_centers[:, 2],
                   c="red", s=60, marker="^", edgecolor="black", linewidth=0.5,
                   label="camera positions", depthshade=False)

        set_equal_aspect(ax, center, radius)
        ax.set_axis_off()
        ax.legend(loc="upper right")

        azim = 360.0 * i / n_frames
        ax.view_init(elev=30, azim=azim)

        fig.canvas.draw()
        buf = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()
        frames.append(buf)

    plt.close(fig)
    imageio.mimsave(out_path, frames, fps=20)
    print(f"Saved {out_path} ({len(frames)} frames)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="output/sparse/0", help="path to COLMAP sparse model folder")
    ap.add_argument("--out", default="output/reconstruction.gif")
    ap.add_argument("--frames", type=int, default=60)
    args = ap.parse_args()

    points, colors, cam_centers = load_colmap_model(args.model)
    print(f"Loaded {len(points)} 3D points, {len(cam_centers)} cameras")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    render_rotation_gif(points, colors, cam_centers, args.out, n_frames=args.frames)


if __name__ == "__main__":
    main()
