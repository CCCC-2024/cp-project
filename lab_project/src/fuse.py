"""Fuse an aligned focal stack into an all-in-focus image + focus map."""
import cv2
import numpy as np


def focus_map_argmax(volume):
    """(N, H, W) sharpness volume -> (H, W) index of the sharpest frame."""
    return np.argmax(volume, axis=0)


def fuse_hard(frames, volume):
    """Each pixel copied from its sharpest frame. Sharp, but can show seams."""
    idx = focus_map_argmax(volume)
    stack = np.stack(frames)  # (N, H, W, 3)
    h, w = idx.shape
    aif = stack[idx, np.arange(h)[:, None], np.arange(w)[None, :]]
    return aif, idx


def fuse_soft(frames, volume, temperature=0.1):
    """Softmax-weighted average over frames. Smoother transitions, slightly less crisp.

    Weights are computed on the sharpness normalised by its per-pixel max, so
    `temperature` means the same thing for every scene / measure.
    """
    v = volume / (volume.max(axis=0, keepdims=True) + 1e-8)
    wts = np.exp((v - 1.0) / temperature)
    wts /= wts.sum(axis=0, keepdims=True)
    stack = np.stack(frames)
    aif = (wts[..., None] * stack).sum(axis=0)
    return aif, focus_map_argmax(volume)


def focus_map_to_color(idx, n_frames):
    """Colorise the focus map (blue = near-focused frame ... red = far)."""
    gray = (idx / max(n_frames - 1, 1) * 255).astype(np.uint8)
    return cv2.applyColorMap(gray, cv2.COLORMAP_JET).astype(np.float32) / 255


def selective_dof(frames, idx, focus_frame, falloff=1.5):
    """Stretch goal: fake a shallow DoF around `focus_frame` using the focus map as depth.

    Pixels whose focus index is far from focus_frame are blurred more.
    """
    aif, _ = fuse_hard(frames, np.eye(len(frames))[idx].transpose(2, 0, 1))  # idx -> one-hot volume
    dist = np.abs(idx.astype(np.float32) - focus_frame)
    levels = [cv2.GaussianBlur(aif, (0, 0), s) if s else aif for s in (0, 3, 6, 12, 20)]
    level = np.clip(dist * falloff, 0, len(levels) - 1.001)
    lo = level.astype(int)
    t = (level - lo)[..., None]
    lv = np.stack(levels)
    h, w = idx.shape
    r, c = np.arange(h)[:, None], np.arange(w)[None, :]
    return (1 - t) * lv[lo, r, c] + t * lv[np.minimum(lo + 1, len(levels) - 1), r, c]
