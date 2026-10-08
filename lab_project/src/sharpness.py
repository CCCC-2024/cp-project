"""Per-pixel focus measures. Higher value = sharper. Each returns an (H, W) float32 map."""
import cv2
import numpy as np


def _gray(img):
    return cv2.cvtColor(img.astype(np.float32), cv2.COLOR_BGR2GRAY)


def laplacian(img, ksize=3):
    """|Laplacian|: responds to high-frequency detail (edges, texture)."""
    return np.abs(cv2.Laplacian(_gray(img), cv2.CV_32F, ksize=ksize))


def tenengrad(img, ksize=3):
    """Squared Sobel gradient magnitude."""
    g = _gray(img)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=ksize)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=ksize)
    return gx * gx + gy * gy


def modified_laplacian(img):
    """|d2/dx2| + |d2/dy2| computed separately (does not cancel on diagonal edges)."""
    g = _gray(img)
    kx = np.array([[0, 0, 0], [-1, 2, -1], [0, 0, 0]], np.float32)
    return np.abs(cv2.filter2D(g, -1, kx)) + np.abs(cv2.filter2D(g, -1, kx.T))


MEASURES = {"laplacian": laplacian, "tenengrad": tenengrad, "mlap": modified_laplacian}


def focus_volume(frames, measure="laplacian", sigma=5.0):
    """Stack of smoothed sharpness maps, shape (N, H, W).

    sigma = Gaussian std in pixels; acts as the 'patch size' (larger = more stable
    choice per region, but blurrier depth boundaries).
    """
    fn = MEASURES[measure]
    vol = np.stack([fn(f) for f in frames])
    if sigma > 0:
        vol = np.stack([cv2.GaussianBlur(v, (0, 0), sigma) for v in vol])
    return vol
