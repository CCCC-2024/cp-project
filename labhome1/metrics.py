"""Take-Home Lab 1: image comparison metrics (MSE, MAE, PSNR) implemented by hand."""

from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

DIR = Path(__file__).resolve().parent


def load(path, size=None):
    img = Image.open(path).convert("RGB")
    if size is not None and img.size != size:
        img = img.resize(size, Image.BILINEAR)
    return np.asarray(img, dtype=np.float64)


def mse(a, b):
    # MSE = 1/(H*W*C) * sum (a - b)^2
    return np.mean((a - b) ** 2)


def mae(a, b):
    # MAE = 1/(H*W*C) * sum |a - b|
    return np.mean(np.abs(a - b))


def psnr(a, b, max_val=255.0):
    # PSNR = 10 * log10(MAX^2 / MSE)
    m = mse(a, b)
    return float("inf") if m == 0 else 10 * np.log10(max_val ** 2 / m)


def posterize(im):
    # every channel: <50 -> 50, 50-99 -> 100, 100-149 -> 150, >=150 -> 200
    return np.select(
        [im < 50, im < 100, im < 150], [50, 100, 150], default=200
    ).astype(np.uint8)


def perturb(im, sigma=28.7, seed=0):
    # Part 2 perturbation: additive Gaussian noise. sigma=28.7 is chosen so that the
    # clipped result has about the same MSE as the posterized image (see report).
    rng = np.random.default_rng(seed)
    noisy = im + rng.normal(0, sigma, im.shape)
    return np.clip(np.rint(noisy), 0, 255).astype(np.uint8)


def ssim(a, b, max_val=255.0):
    # Bonus: SSIM = (2*mu_a*mu_b + C1)(2*cov_ab + C2) / ((mu_a^2 + mu_b^2 + C1)(var_a + var_b + C2))
    # computed in an 11x11 Gaussian window (sigma 1.5), per channel, then averaged.
    c1, c2 = (0.01 * max_val) ** 2, (0.03 * max_val) ** 2
    scores = []
    for ch in range(a.shape[2]):
        x, y = a[:, :, ch], b[:, :, ch]
        f = lambda z: gaussian_filter(z, 1.5, truncate=3.5)
        mx, my = f(x), f(y)
        vx, vy, cxy = f(x * x) - mx * mx, f(y * y) - my * my, f(x * y) - mx * my
        s = ((2 * mx * my + c1) * (2 * cxy + c2)) / ((mx * mx + my * my + c1) * (vx + vy + c2))
        scores.append(s.mean())
    return float(np.mean(scores))


def main():
    original = load(DIR / "mountains.png")
    size = (original.shape[1], original.shape[0])

    # Part 1 inputs: posterized image is regenerated from the original
    Image.fromarray(posterize(original)).save(DIR / "quantized.png")
    results = {
        "quantized.png": load(DIR / "quantized.png", size),
        "controlnet.png": load(DIR / "controlnet.png", size),
        "favorite.png": load(DIR / "favorite.png", size),
    }

    # Part 2
    Image.fromarray(perturb(original)).save(DIR / "perturbed.png")
    results["perturbed.png"] = load(DIR / "perturbed.png", size)

    print(f"{'image':16s}{'MSE':>12s}{'MAE':>10s}{'PSNR (dB)':>12s}{'SSIM':>8s}")
    for name, im in results.items():
        print(f"{name:16s}{mse(original, im):12.2f}{mae(original, im):10.2f}"
              f"{psnr(original, im):12.2f}{ssim(original, im):8.3f}")


if __name__ == "__main__":
    main()
