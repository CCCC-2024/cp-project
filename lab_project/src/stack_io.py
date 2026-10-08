"""Load / save focal stacks. One folder per scene: data/raw/scene01/01.jpg, 02.jpg, ..."""
from pathlib import Path

import cv2
import numpy as np

try:  # iPhone HEIC support (optional)
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass
from PIL import Image

EXTS = {".jpg", ".jpeg", ".png", ".heic", ".tif", ".tiff"}


def load_stack(folder, max_side=None):
    """Return list of float32 BGR images in [0, 1], sorted by file name (near -> far focus)."""
    files = sorted(p for p in Path(folder).iterdir() if p.suffix.lower() in EXTS)
    if not files:
        raise FileNotFoundError(f"no images in {folder}")
    frames = []
    for p in files:
        img = np.asarray(Image.open(p).convert("RGB"), dtype=np.float32) / 255.0
        img = img[..., ::-1]  # RGB -> BGR for OpenCV
        if max_side and max(img.shape[:2]) > max_side:
            s = max_side / max(img.shape[:2])
            img = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        frames.append(np.ascontiguousarray(img))
    return frames


def subsample(frames, n):
    """Keep n frames evenly spread over the stack (for the 'number of frames' ablation)."""
    idx = np.linspace(0, len(frames) - 1, n).round().astype(int)
    return [frames[i] for i in idx], idx


def save_image(path, img):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), np.clip(img * 255, 0, 255).astype(np.uint8))
