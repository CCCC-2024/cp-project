"""Check the extra credit against a known answer, with a synthetic scene.

A red textured disc sits in front of a smooth cream wall. We know the wall
behind the disc, so the correct defocus (disc sharp, wall blurred, wall colour
only) is computed directly. Each method is scored on the ring of wall pixels
just outside the disc, where halo and dark fringe live.

Run:  python test_clean.py [sigma]      Writes test_clean.png
"""

import sys

import cv2
import numpy as np

from clean import defocus_clean

sigma = int(sys.argv[1]) if len(sys.argv) > 1 else 15
k = 6 * sigma + 1
rng = np.random.RandomState(1)
H, W = 600, 800
yy, xx = np.mgrid[:H, :W].astype(np.float32)
wall = np.dstack([200 + 0 * xx, 215 + 8 * yy / H, 225 + 10 * xx / W]) + rng.randn(H, W, 3) * 1.5  # BGR cream
wall = np.clip(wall, 0, 255).astype(np.float32)
m = (xx - 400) ** 2 + (yy - 300) ** 2 < 140**2
subject = np.dstack([40 + 0 * xx, 30 + 0 * xx, 200 + 40 * np.sin(xx / 6)]) + rng.randn(H, W, 3) * 3  # saturated red
im = np.where(m[:, :, None], subject, wall).astype(np.float32)


def blur(a):
    return cv2.GaussianBlur(a, (k, k), sigma, borderType=cv2.BORDER_REPLICATE)


truth = np.where(m[:, :, None], im, blur(wall))  # subject sharp, wall blurred, wall colour only
naive = np.where(m[:, :, None], im, blur(im))  # step 4: blur everything, then mask
cutout = np.where(m[:, :, None], im, blur(im * (~m)[:, :, None]))  # cut subject out (black), then blur
clean = defocus_clean(im, m, sigma)

dist = cv2.distanceTransform((~m).astype(np.uint8), cv2.DIST_L2, 5)
ring = (dist > 0) & (dist <= 3 * sigma)
print(f"sigma={sigma}: error vs the correct wall colour, ring of 3*sigma px outside the disc")
print(f"{'method':8s} {'mean abs err':>12s} {'max abs err':>12s} {'mean signed (dark<0)':>22s}")
lum = lambda a: a.mean(2)
for name, a in [("step 4", naive), ("cutout", cutout), ("clean", clean)]:
    e = lum(a - truth)[ring]
    print(f"{name:8s} {np.abs(e).mean():12.2f} {np.abs(e).max():12.2f} {e.mean():22.2f}")

def tag(a, text):
    a = a.clip(0, 255).astype(np.uint8).copy()
    cv2.putText(a, text, (12, 36), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    return a


cv2.imwrite("test_clean.png", np.vstack([
    np.hstack([tag(truth, "correct answer"), tag(naive, "step 4: halo")]),
    np.hstack([tag(cutout, "cut out first: dark fringe"), tag(clean, "clean")]),
]))
