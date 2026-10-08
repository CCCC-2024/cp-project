"""Comparison panels: single-focus frames vs. fused result, cropped at near / mid / far.

    python src/make_figures.py scene01 results/all_in_focus/scene01_baseline.png \
        --crops 100,200,300 ... (x,y,size triplets for near / mid / far)
"""
import argparse
from pathlib import Path

import cv2
import matplotlib.pyplot as plt

from stack_io import load_stack

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene")
    ap.add_argument("fused")
    ap.add_argument("--crops", nargs=3, required=True, help="three x,y,size boxes: near mid far")
    ap.add_argument("--max-side", type=int, default=1600)
    a = ap.parse_args()

    frames = load_stack(ROOT / "data/raw" / a.scene, a.max_side)
    fused = cv2.imread(a.fused).astype("float32") / 255
    boxes = [tuple(map(int, c.split(","))) for c in a.crops]
    rows = [("near-focus frame", frames[0]), ("mid-focus frame", frames[len(frames) // 2]),
            ("far-focus frame", frames[-1]), ("fused", fused)]

    fig, ax = plt.subplots(len(rows), 3, figsize=(9, 3 * len(rows)))
    for r, (name, img) in enumerate(rows):
        for c, (x, y, s) in enumerate(boxes):
            ax[r, c].imshow(img[y:y + s, x:x + s, ::-1])
            ax[r, c].axis("off")
            if c == 0:
                ax[r, c].set_title(name, loc="left", fontsize=9)
    out = ROOT / "results/comparisons" / f"{a.scene}_crops.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print("saved", out)


if __name__ == "__main__":
    main()
