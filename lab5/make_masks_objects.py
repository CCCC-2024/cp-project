"""Step 3 (object-aware variant): depth layers that keep each object whole.

The table here is one continuous slope in depth, so plain thresholds (make_masks.py)
slice objects across table bands. Here each object is cut out first (GrabCut,
started from a box you give) and joins the layer its own depth falls in; the
rest of the scene (table, wall) is split by the same depth thresholds, so every
layer is "an object plus the table at its depth": a plane of focus.

Run:
    python make_masks_objects.py                 # uses BOXES / THRESHOLDS below
    python make_masks_objects.py -t 0.2 0.4      # other thresholds on depth 0..1
Outputs: mask1.png (nearest) ... maskN.png, mask_preview.png
"""

import argparse
import glob
import os

import cv2
import numpy as np

# Boxes x0, y0, x1, y1 around each object, in image.jpg pixels (1500 px wide).
BOXES = {
    "plush": (805, 325, 1390, 895),
    "spray": (335, 330, 455, 745),
    "cup": (630, 150, 845, 672),
}
FORCE = {}  # objects whose layer (1 = nearest) is set by hand, not by depth, e.g. {"chair": 2}
TABLE_FIX = {"plush": 0.0, "spray": 0.6, "cup": 0.6}  # drop table-coloured pixels GrabCut kept, below this fraction of the box height
# Small boxes where dark pixels (pupils sitting on the silhouette) belong to the object.
ADD_DARK = {"plush": [(990, 380, 1035, 425), (865, 450, 915, 500)]}
CLOSE = {"plush": 25}  # closing kernel (px), default 9
SEED = 0.4  # fraction of the box's depth range above which a pixel seeds the object
THRESHOLDS = [0.13, 0.23, 0.36]  # wall | cup | spray | plush, on the 0..1 depth of depth.npy

ap = argparse.ArgumentParser()
ap.add_argument("-t", type=float, nargs="+", default=THRESHOLDS)
ap.add_argument("--min-area", type=float, default=0.002)
args = ap.parse_args()

im = cv2.imread("image.jpg")
depth = cv2.GaussianBlur(np.load("depth.npy"), (9, 9), 0)
th = sorted(args.t)
n = len(th) + 1
label = np.digitize(depth, th)  # 0 = far ... n-1 = near

# 1. Cut out each object.
objects = {}
for name, (x0, y0, x1, y1) in BOXES.items():
    # Seed GrabCut with depth: inside the box, pixels clearly nearer than the
    # box's far background are probable object, the rest probable background.
    box = depth[y0:y1, x0:x1]
    lo, hi = np.percentile(box, 10), np.percentile(box, 90)
    near = box > lo + SEED * (hi - lo)
    gc = np.full(im.shape[:2], cv2.GC_BGD, np.uint8)
    gc[y0:y1, x0:x1] = np.where(near, cv2.GC_PR_FGD, cv2.GC_PR_BGD)
    sure = cv2.erode(near.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
    gc[y0:y1, x0:x1][sure] = cv2.GC_FGD
    bg, fg = np.zeros((1, 65)), np.zeros((1, 65))
    cv2.grabCut(im, gc, None, bg, fg, 8, cv2.GC_INIT_WITH_MASK)
    m = ((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD)).astype(np.uint8)
    cnt, cc, st, _ = cv2.connectedComponentsWithStats(m)  # keep the biggest blob
    m = (cc == 1 + st[1:, cv2.CC_STAT_AREA].argmax()).astype(np.uint8)
    if name in TABLE_FIX:  # Mahalanobis distance in Lab to a patch of bare near table
        lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32)
        tab = lab[int(0.85 * im.shape[0]) :].reshape(-1, 3)
        icov = np.linalg.inv(np.cov(tab.T))
        diff = lab - tab.mean(0)
        dist = np.sqrt(np.einsum("hwi,ij,hwj->hw", diff, icov, diff))
        zone = np.zeros(m.shape, bool)
        zone[y0 + int(TABLE_FIX[name] * (y1 - y0)) :] = True  # only the lower part of the box touches the table
        m = cv2.morphologyEx(m & ~(zone & (dist < 4)).astype(np.uint8), cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
        cnt, cc, st, _ = cv2.connectedComponentsWithStats(m)
        m = (cc == 1 + st[1:, cv2.CC_STAT_AREA].argmax()).astype(np.uint8)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    for ax0, ay0, ax1, ay1 in ADD_DARK.get(name, []):
        m[ay0:ay1, ax0:ax1] |= (gray[ay0:ay1, ax0:ax1] < 80).astype(np.uint8)
    ck = CLOSE.get(name, 9)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ck, ck)))
    # Fill holes (eyes, labels): background pixels not connected to the frame border.
    pad = np.pad(1 - m, 1, constant_values=1).astype(np.uint8)
    cv2.floodFill(pad, None, (0, 0), 2)
    m = (pad[1:-1, 1:-1] != 2).astype(np.uint8)
    objects[name] = m > 0

# 2. Everything else is split by depth; each object goes to the layer of its own depth.
owner = label.copy()
for name, m in objects.items():
    layer = n - FORCE[name] if name in FORCE else int(np.digitize(np.median(depth[m]), th))
    owner[m] = layer
    print(f"{name}: median depth {np.median(depth[m]):.3f} -> layer {n - layer}")

# 3. Tidy each layer: drop specks, fill small holes, and re-tile the image.
for i in range(n):
    m = (owner == i).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    cnt, cc, st, _ = cv2.connectedComponentsWithStats(m)
    for j in range(1, cnt):
        if st[j, cv2.CC_STAT_AREA] < args.min_area * m.size:
            owner[(cc == j) & (owner == i)] = -1
# specks go to the layer that surrounds them
unassigned = (owner < 0).astype(np.uint8)
if unassigned.any():
    filled = cv2.medianBlur(np.where(owner < 0, label, owner).astype(np.uint8), 15)
    owner[owner < 0] = filled[owner < 0]

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
