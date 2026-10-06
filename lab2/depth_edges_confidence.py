"""Registered and denoised multi-flash depth edges.

Usage: python depth_edges_confidence.py LEFT RIGHT TOP BOTTOM
Directions describe the light position relative to the camera in image axes.
Outputs are PNG files in output/code/. A homography approximately compensates
for camera motion; it cannot undo parallax or motion of individual objects.
Use --raw --threshold 0.8 for the original full-resolution course calculation.
"""

import argparse
import json
from pathlib import Path

import cv2
import numpy as np


def load_gray_float(path):
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(path)
    return img.astype(np.float32) / 255.0


def compute_confidence(left, right, top, bottom):
    """Positive directional Sobel responses before thresholding.

    Matches depthEdgesKey.ipynb: left +x, right -x, top +y, bottom -y.
    BORDER_REFLECT matches scipy.ndimage.sobel's default boundary behavior.
    """
    inputs = (left, right, top, bottom)
    if any(im.ndim != 2 or im.shape != left.shape for im in inputs):
        raise ValueError("All four images must be grayscale and have equal dimensions.")
    maximg = np.maximum.reduce(inputs)
    maximg = np.maximum(maximg, np.finfo(np.float32).eps)
    responses = []
    for im, dx, dy, sign in (
        (left, 1, 0, 1), (right, 1, 0, -1),
        (top, 0, 1, 1), (bottom, 0, 1, -1),
    ):
        derivative = cv2.Sobel(im / maximg, cv2.CV_32F, dx, dy,
                               ksize=3, borderType=cv2.BORDER_REFLECT)
        responses.append(sign * derivative)
    return np.maximum(np.maximum.reduce(responses), 0)


def register_images(images):
    """Align other views to the left-light image using SIFT + RANSAC.

    A broad feature-selection rectangle covers the foreground object and table.
    It selects registration features only: no region is masked out of the output.
    """
    height, width = images[0].shape[:2]
    mask = np.zeros((height, width), np.uint8)
    mask[round(height * 280/1200):round(height * 1040/1200),
         round(width * 90/1600):round(width * 1510/1600)] = 255
    sift = cv2.SIFT_create(nfeatures=7000)
    gray = [cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) for im in images]
    ref_key, ref_desc = sift.detectAndCompute(gray[0], mask)
    if ref_desc is None:
        raise ValueError("Not enough reference-image features for registration.")
    aligned = [images[0]]
    valid = np.ones((height, width), np.uint8)
    reports = [{"direction": "left", "reference": True}]
    for direction, im, g in zip(("right", "top", "bottom"), images[1:], gray[1:]):
        keys, desc = sift.detectAndCompute(g, mask)
        if desc is None:
            raise ValueError(f"No usable features for {direction}.")
        pairs = cv2.BFMatcher().knnMatch(desc, ref_desc, k=2)
        good = [pair[0] for pair in pairs
                if len(pair) == 2 and pair[0].distance < 0.7 * pair[1].distance]
        if len(good) < 10:
            raise ValueError(f"Too few feature matches for {direction}.")
        source = np.float32([keys[m.queryIdx].pt for m in good])
        target = np.float32([ref_key[m.trainIdx].pt for m in good])
        transform, inliers = cv2.findHomography(source, target, cv2.RANSAC, 3.0)
        if transform is None or inliers is None or int(inliers.sum()) < 10:
            raise ValueError(f"Registration failed for {direction}.")
        predicted = cv2.perspectiveTransform(source[:, None], transform)[:, 0]
        error = np.linalg.norm(predicted - target, axis=1)
        median = float(np.median(error[inliers[:, 0] > 0]))
        if not np.isfinite(transform).all() or median > 2.5:
            raise ValueError(f"Unreliable registration for {direction}.")
        aligned.append(cv2.warpPerspective(im, transform, (width, height)))
        support = cv2.warpPerspective(np.ones((height, width), np.uint8),
                                      transform, (width, height), flags=cv2.INTER_NEAREST)
        valid = np.minimum(valid, support)
        reports.append({"direction": direction, "matches": len(good),
                        "inliers": int(inliers.sum()), "median_error_px": median,
                        "homography": transform.tolist()})
    valid = cv2.erode(valid, np.ones((15, 15), np.uint8))
    valid[:4] = valid[-4:] = 0
    valid[:, :4] = valid[:, -4:] = 0
    return aligned, valid, reports


def refined_edges(images, sigma=3.0, low=0.05, high=0.2, min_component=35):
    aligned, valid, registration = register_images(images)
    gray = [cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)/255,
                            (0, 0), sigma) for im in aligned]
    denominator = np.maximum(np.maximum.reduce(gray), 0.02)
    responses, peaks = [], []
    for im, (dx, dy, sign) in zip(gray, ((1, 0, 1), (1, 0, -1), (0, 1, 1), (0, 1, -1))):
        response = sign * cv2.Sobel(im / denominator, cv2.CV_32F, dx, dy,
                                    ksize=3, borderType=cv2.BORDER_REFLECT)
        response = np.maximum(response, 0)
        axis = 1 if dx else 0
        is_peak = ((response >= np.roll(response, 1, axis)) &
                   (response > np.roll(response, -1, axis)))
        responses.append(response)
        peaks.append(response * is_peak)
    confidence = np.maximum.reduce(responses) * valid
    thin = np.maximum.reduce(peaks) * valid
    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        np.uint8(thin > low), connectivity=8)
    has_strong = np.bincount(labels[thin > high].ravel(), minlength=count) > 0
    keep = has_strong & (stats[:, cv2.CC_STAT_AREA] >= min_component)
    keep[0] = False
    edges = np.uint8(keep[labels]) * 255
    return confidence, edges, registration


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for direction in ("left", "right", "top", "bottom"):
        parser.add_argument(direction, type=Path)
    parser.add_argument("--raw", action="store_true", help="Skip registration and refinement")
    parser.add_argument("--threshold", type=float, default=None,
                        help="Strong threshold; default 0.2 refined / 0.8 raw")
    parser.add_argument("--low-threshold", type=float, default=0.05)
    parser.add_argument("--max-width", type=int, default=1600)
    parser.add_argument("--sigma", type=float, default=3.0)
    parser.add_argument("--min-component", type=int, default=35)
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).parent / "output" / "code")
    args = parser.parse_args()
    if args.threshold is None:
        args.threshold = 0.8 if args.raw else 0.2
    if not np.isfinite(args.threshold) or args.threshold < 0:
        parser.error("Threshold must be finite and nonnegative.")
    paths = [getattr(args, key) for key in ("left", "right", "top", "bottom")]
    metadata = {"inputs": dict(zip(("left", "right", "top", "bottom"), map(str, paths))),
                "mode": "raw" if args.raw else "registered_refined"}
    if args.raw:
        confidence = compute_confidence(*(load_gray_float(path) for path in paths))
        edges = np.uint8(confidence > args.threshold) * 255
    else:
        if (args.max_width < 100 or not np.isfinite(args.sigma) or args.sigma <= 0 or
                not 0 <= args.low_threshold <= args.threshold or args.min_component < 1):
            parser.error("Invalid resize, smoothing, hysteresis, or component parameter.")
        images = [cv2.imread(str(path)) for path in paths]
        if any(im is None for im in images):
            raise FileNotFoundError("Could not load all four input images.")
        if any(im.shape != images[0].shape for im in images):
            raise ValueError("All four input images must have equal dimensions.")
        height, width = images[0].shape[:2]
        scale = min(1.0, args.max_width / width)
        size = (round(width * scale), round(height * scale))
        images = [cv2.resize(im, size, interpolation=cv2.INTER_AREA) for im in images]
        confidence, edges, registration = refined_edges(
            images, args.sigma, args.low_threshold, args.threshold, args.min_component)
        metadata.update({"size": size, "sigma": args.sigma, "low_threshold": args.low_threshold,
                         "min_component": args.min_component, "registration": registration})
    metadata["high_threshold"] = args.threshold
    metadata["edge_pixel_fraction"] = float(np.count_nonzero(edges) / edges.size)
    # Display only: map the theoretical positive Sobel range [0, 4] to [0, 255].
    preview = np.rint(np.clip(confidence / 4, 0, 1) * 255).astype(np.uint8)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, data in (("confidence.png", preview), ("depth_edges.png", edges)):
        path = args.output_dir / name
        if not cv2.imwrite(str(path), data):
            raise OSError(f"Could not save {path}")
        print(f"Saved {path}")
    (args.output_dir / "processing.json").write_text(json.dumps(metadata, indent=2) + "\n")


if __name__ == "__main__":
    main()
