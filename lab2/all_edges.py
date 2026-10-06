"""
Extract ALL edges (ordinary Canny edges) from a single normally-lit RGB
photo of the scene. Used as the counterpart to depth_edges_confidence.py
for the comparison required in Lab 2 step 3.

Usage:
    python all_edges.py ambient.jpg
"""

import argparse
from pathlib import Path
import cv2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--max-width", type=int, default=1600,
                        help="Match refined depth-edge resolution; 0 keeps full resolution")
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).parent / "output" / "code" / "all_edges.png")
    args = parser.parse_args()
    if args.output.suffix.lower() != ".png":
        parser.error("Output must be a PNG file.")
    img = cv2.imread(str(args.image), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(args.image)
    if args.max_width < 0:
        parser.error("max-width must be nonnegative.")
    if args.max_width and img.shape[1] > args.max_width:
        scale = args.max_width / img.shape[1]
        img = cv2.resize(img, (args.max_width, round(img.shape[0] * scale)),
                         interpolation=cv2.INTER_AREA)

    blurred = cv2.GaussianBlur(img, (3, 3), 0)
    edges = cv2.Canny(blurred, 50, 150)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(args.output), edges):
        raise OSError(f"Could not save {args.output}")
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
