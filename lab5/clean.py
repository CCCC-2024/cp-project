"""Extra credit: defocus with no halo and no dark fringe, no holes.

Why the two naive versions fail (I = photo, M = mask, 1 = in focus):
  * blur(I) then mask: the blurred value just outside the subject is an
    average over a window that reaches INTO the subject, so the background
    next to the subject carries subject colour: a halo.
  * cut out the subject (I*(1-M)) then blur: the removed subject is black,
    and the blur averages those zeros in: the background fades to black near
    the subject: a dark fringe (and a hole where the subject was).
Both are the same mistake: the blur window contains pixels that are not
background. Fix: normalised convolution, which averages background pixels only:
    B = blur(I * W) / blur(W),   W = background weight (1 - M, slightly eroded)
Dividing by blur(W) renormalises the weights to sum to one, so the zeros that
stood for "no data" never pull the average down, and the hole is filled with
what its background neighbours say. The in-focus layer is then composited with
a soft (feathered) alpha so the edge has neither a staircase nor a gap.

Run:
    python clean.py [sigma]
Outputs:  defocus1_clean.png, defocus2_clean.png, ...
"""

import glob
import sys

import cv2
import numpy as np

FEATHER = 1.5  # sigma (px) of the edge softening of the focus mask
ERODE = 3  # px by which the background weight stays away from the subject edge
SHRINK = 1  # px by which the sharp region is pulled in, to drop edge pixels that mix subject and background


def defocus_clean(im, m, sigma):
    """im: float32 HxWx3 photo. m: bool HxW, True where in focus. Returns float32 image."""
    k = 6 * sigma + 1

    def blur(a):
        return cv2.GaussianBlur(a, (k, k), sigma, borderType=cv2.BORDER_REPLICATE)

    # Background weight: keep clear of the (anti-aliased, imprecise) subject edge.
    w = (~m).astype(np.float32)
    if ERODE:
        w = cv2.erode(w, np.ones((2 * ERODE + 1,) * 2, np.uint8))
    num = blur(im * w[:, :, None])
    den = blur(w)[:, :, None]
    # Where the window holds almost no background (deep inside a big subject)
    # the value is never shown; fall back to the plain blur to avoid 0/0.
    bg = np.where(den > 1e-4, num / np.maximum(den, 1e-4), blur(im))
    sharp = cv2.erode(m.astype(np.float32), np.ones((2 * SHRINK + 1,) * 2, np.uint8)) if SHRINK else m.astype(np.float32)
    alpha = cv2.GaussianBlur(sharp, (0, 0), FEATHER)[:, :, None]
    return alpha * im + (1 - alpha) * bg


if __name__ == "__main__":
    sigma = int(sys.argv[1]) if len(sys.argv) > 1 else 10  # keep equal to defocus.py
    im = cv2.imread("image.jpg").astype(np.float32)
    for n, name in enumerate(sorted(glob.glob("mask[0-9]*.png"), key=lambda s: int(s[4:-4])), start=1):
        m = cv2.imread(name, cv2.IMREAD_GRAYSCALE) > 127
        cv2.imwrite(f"defocus{n}_clean.png", np.clip(defocus_clean(im, m, sigma), 0, 255).astype(np.uint8))
    print("wrote defocus*_clean.png")
