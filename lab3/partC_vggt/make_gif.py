"""
Part C - convert a screen recording of the VGGT 3D viewer into a GIF.

Usage:
    python make_gif.py --video output/vggt_recording.mov --out output/vggt.gif \
        --fps 10 --max_width 800
"""

import argparse
import imageio.v2 as imageio
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=10, help="output GIF fps (subsamples source)")
    ap.add_argument("--max_width", type=int, default=800, help="resize width to keep GIF small")
    args = ap.parse_args()

    reader = imageio.get_reader(args.video)
    src_fps = reader.get_meta_data().get("fps", 30)
    step = max(1, round(src_fps / args.fps))

    frames = []
    for i, frame in enumerate(reader):
        if i % step != 0:
            continue
        if args.max_width and frame.shape[1] > args.max_width:
            scale = args.max_width / frame.shape[1]
            new_size = (args.max_width, int(frame.shape[0] * scale))
            from PIL import Image
            frame = np.array(Image.fromarray(frame).resize(new_size))
        frames.append(frame)
    reader.close()

    imageio.mimsave(args.out, frames, fps=args.fps)
    print(f"Saved {args.out} ({len(frames)} frames)")


if __name__ == "__main__":
    main()
