"""Register every frame to a reference frame.

Changing focus slightly rescales the image (focus breathing), so we use an affine
ECC model (handles scale + translation + small rotation), not just a shift.
"""
import cv2
import numpy as np


def _gray(img):
    return cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255


def align_to_reference(frames, ref_idx=None, iters=200, eps=1e-6, downscale=0.5):
    """Warp each frame onto frames[ref_idx]. Returns (aligned_frames, warps).

    ECC is run on a downscaled grayscale copy for speed; the warp is rescaled and
    applied to the full-resolution frame. If ECC fails to converge we keep identity.
    """
    ref_idx = len(frames) // 2 if ref_idx is None else ref_idx
    ref_small = cv2.resize(_gray(frames[ref_idx]), None, fx=downscale, fy=downscale)
    h, w = frames[0].shape[:2]
    crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, iters, eps)

    aligned, warps = [], []
    for i, f in enumerate(frames):
        warp = np.eye(2, 3, dtype=np.float32)
        if i != ref_idx:
            small = cv2.resize(_gray(f), None, fx=downscale, fy=downscale)
            try:
                _, warp = cv2.findTransformECC(ref_small, small, warp, cv2.MOTION_AFFINE, crit, None, 5)
                warp[:, 2] /= downscale  # translation back to full-res pixels
            except cv2.error:
                print(f"[align] frame {i}: ECC did not converge, keeping identity")
                warp = np.eye(2, 3, dtype=np.float32)
        out = cv2.warpAffine(f, warp, (w, h), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP,
                             borderMode=cv2.BORDER_REPLICATE)
        aligned.append(out)
        warps.append(warp)
    return aligned, warps
