"""Step 3: turn the depth map into depth-layer masks, near to far.

Run:
    python make_masks.py                    # 3 layers, split by 1-D k-means
    python make_masks.py -n 4               # 4 layers
    python make_masks.py -t 0.35 0.7        # your own thresholds on depth 0..1
Outputs:
    mask1.png (nearest) ... maskN.png (farthest), white = this layer
    mask_preview.png    masks coloured over the photo, to check them by eye
Layers partition the image: every pixel belongs to exactly one mask.
"""

import argparse
import glob
import os

import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("-n", type=int, default=3, help="number of layers (ignored with -t)")
ap.add_argument("-t", type=float, nargs="+", help="thresholds on depth (0..1, ascending)")
ap.add_argument("--min-area", type=float, default=0.002, help="drop specks smaller than this fraction of the image")
ap.add_argument("--close", type=int, default=7, help="closing kernel (px) to fill holes")
ap.add_argument("--open", type=int, default=5, help="opening kernel (px) to remove specks")
ap.add_argument("--smooth", type=int, default=9, help="median/blur kernel on depth before splitting (odd)")
args = ap.parse_args()

depth = np.load("depth.npy")
im = cv2.imread("image.jpg")
if args.smooth > 1:
    depth = cv2.GaussianBlur(depth, (args.smooth | 1,) * 2, 0)

if args.t:
    th = sorted(args.t)
else:  # 1-D k-means on depth values; initial centres at quantiles
    v = depth.ravel()[:: max(1, depth.size // 200000)]
    c = np.quantile(v, (np.arange(args.n) + 0.5) / args.n)
    for _ in range(50):
        lab = np.abs(v[:, None] - c[None]).argmin(1)
        c = np.array([v[lab == i].mean() if (lab == i).any() else c[i] for i in range(args.n)])
    c.sort()
    th = list((c[:-1] + c[1:]) / 2)
print("thresholds:", [round(float(t), 3) for t in th])

# Layer index 0 = farthest (smallest depth value) ... last = nearest.
label = np.digitize(depth, th)
n = len(th) + 1


def clean(m):
    m = m.astype(np.uint8)
    if args.close > 1:
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((args.close,) * 2, np.uint8))
    if args.open > 1:
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((args.open,) * 2, np.uint8))
    cnt, cc, st, _ = cv2.connectedComponentsWithStats(m)
    keep = np.zeros_like(m)
    for i in range(1, cnt):
        if st[i, cv2.CC_STAT_AREA] >= args.min_area * m.size:
            keep[cc == i] = 1
    return keep


# Clean each layer, then give any pixel left unassigned to the nearest layer
# by depth so the masks still tile the image.
layers = [clean(label == i) for i in range(n)]
owner = np.full(depth.shape, -1, np.int32)
for i, m in enumerate(layers):
    owner[(m > 0) & (owner < 0)] = i
holes = owner < 0
if holes.any():
    owner[holes] = label[holes]

for f in glob.glob("mask[0-9]*.png"):
    os.remove(f)
colors = cv2.applyColorMap(np.linspace(0, 255, n).astype(np.uint8).reshape(-1, 1)[::-1], cv2.COLORMAP_VIRIDIS)[:, 0]
preview = im.copy()
for k, i in enumerate(range(n - 1, -1, -1), start=1):  # k=1 is the nearest layer
    m = owner == i
    cv2.imwrite(f"mask{k}.png", (255 * m).astype(np.uint8))
    preview[m] = (0.5 * im[m] + 0.5 * colors[k - 1]).astype(np.uint8)
    print(f"mask{k}.png  {100 * m.mean():.1f}% of image")
cv2.imwrite("mask_preview.png", preview)
