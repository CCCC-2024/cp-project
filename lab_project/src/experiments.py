"""Run the baseline + ablations on one scene.

    python src/experiments.py scene01 [--max-side 1600]

Writes to results/: all_in_focus/, focus_maps/ (and prints a summary).
"""
import argparse
from pathlib import Path

from align import align_to_reference
from fuse import focus_map_to_color, fuse_hard, fuse_soft
from sharpness import MEASURES, focus_volume
from stack_io import load_stack, save_image, subsample

ROOT = Path(__file__).resolve().parent.parent


def run(frames, tag, out, measure="laplacian", sigma=5.0, blend="hard"):
    vol = focus_volume(frames, measure, sigma)
    aif, idx = fuse_hard(frames, vol) if blend == "hard" else fuse_soft(frames, vol)
    save_image(ROOT / "results/all_in_focus" / f"{out}_{tag}.png", aif)
    save_image(ROOT / "results/focus_maps" / f"{out}_{tag}.png", focus_map_to_color(idx, len(frames)))
    print(f"[{out}] {tag}: done")
    return aif, idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene")
    ap.add_argument("--max-side", type=int, default=1600)
    ap.add_argument("--no-align", action="store_true")
    a = ap.parse_args()

    frames = load_stack(ROOT / "data/raw" / a.scene, a.max_side)
    if not a.no_align:
        frames, _ = align_to_reference(frames)
    n = len(frames)

    run(frames, "baseline", a.scene)                          # Laplacian + argmax, hard
    for k in (3, 5, n):                                       # number of frames
        if k <= n:
            run(subsample(frames, k)[0], f"n{k}", a.scene)
    for m in MEASURES:                                        # focus measure
        run(frames, f"measure-{m}", a.scene, measure=m)
    for s in (1, 3, 5, 10, 20):                               # patch size ~ Gaussian sigma
        run(frames, f"sigma{s}", a.scene, sigma=s)
    run(frames, "soft", a.scene, blend="soft")                # hard vs soft


if __name__ == "__main__":
    main()
