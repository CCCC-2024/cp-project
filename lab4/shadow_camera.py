"""Shadow camera (Koppal & Narasimhan, ICCV 2009): render the scene as seen
from the light source, from two videos in which a thin occluder's shadow
sweeps the scene once horizontally and once vertically.

    conda run -n cv python shadow_camera.py data/sweep_h.mp4 data/sweep_v.mp4

For every camera pixel (x, y) the time the shadow passes over it in the
horizontal sweep, t_h, and in the vertical sweep, t_v, identify the light ray
that reaches that scene point (Sec. 2.1 of the paper). With the occluder
translating in a plane at roughly constant speed, (t_h, t_v) are the pixel
coordinates of a perspective camera centred at the light, so by reciprocity
    I_light(t_h, t_v) = I_camera(x, y).
Pixels the shadow never darkens (cast/attached shadows, i.e. points the light
cannot see) carry no ray and are left out.

Needs output/floodlit.png from forsep.py for the colours.
Writes output/shadow_camera/{light_view.png, t_h.png, t_v.png, comparison.png}.

Rendering is done backwards: the valid camera pixels are triangulated in
(t_h, t_v) space, every light-view pixel looks up the camera position it
corresponds to, and the colour is sampled from the full-resolution floodlit
image. Triangles that are stretched in the camera image straddle a depth
edge; the light sees what is behind them but the camera does not, so they
stay black.
"""

import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy.spatial import Delaunay

args = [a for a in sys.argv[1:] if a != "--reuse"]
REUSE = "--reuse" in sys.argv      # reuse output/shadow_camera/shadow_times.npy from a previous run
paths = args[:2] or ["data/sweep_h.mp4", "data/sweep_v.mp4"]
ROOT = Path(__file__).parent
OUT = ROOT / "output" / "shadow_camera"
WIDTH = 960          # camera resolution used for the timing (height follows)
GAMMA = 2.2
MIN_DEPTH = 0.6      # the shadow must remove at least this fraction of a pixel's light
PX_PER_FRAME = 1.0   # light-view pixels per video frame of shadow motion
CHUNK = 60           # image rows processed at once (bounds memory)
STEP = 2             # camera pixels sampled every STEP px for the triangulation
MAX_CAM_EDGE = 5.0   # triangle edges longer than this (in STEP units) in the camera image
                     # span a depth discontinuity: the camera does not see that surface
EDGE_GRAD = 4.0      # drop pixels whose shadow time changes this many times faster than typical
                     # (they straddle a depth edge and their timing is a mix of two surfaces)
LEVEL = True         # rotate the light view about its optical axis so it is upright
MAX_HOLE = 1500      # holes smaller than this (light-view px) are sampling gaps and get inpainted


def luminance_frames(path):
    """All frames of `path` as linear luminance, shape T x H x W, float32."""
    cap = cv2.VideoCapture(path)
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    height = h * WIDTH // w
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={WIDTH}:{height}:flags=area",
           "-f", "rawvideo", "-pix_fmt", "gray16le", "-"]
    raw = subprocess.run(cmd, stdout=subprocess.PIPE, check=True).stdout
    lum = np.frombuffer(raw, np.uint16).reshape(-1, height, WIDTH)
    return (lum.astype(np.float32) / 65535.0) ** GAMMA


def shadow_times(path):
    """Sub-frame time at which the shadow is centred on each pixel, and a validity mask."""
    lum = luminance_frames(path)
    T = len(lum)
    # Divide out global flicker of the (hand-held) light, measured on unshadowed pixels.
    ref = np.median(lum, axis=0) + 1e-5
    gain = np.array([np.median((f / ref)[(f / ref) > 0.85]) for f in lum], dtype=np.float32)
    lum /= gain[:, None, None]

    t_c = np.full(lum.shape[1:], np.nan, np.float32)
    idx = np.arange(T, dtype=np.float32)[:, None, None]
    for y0 in range(0, lum.shape[1], CHUNK):
        s = cv2.blur(lum[:, y0:y0 + CHUNK].reshape(T, -1), (1, 5)).reshape(T, -1, WIDTH)  # 5-frame box
        lo, hi = s.min(axis=0), np.percentile(s, 90, axis=0)
        mid = (lo + hi) / 2
        t_min = s.argmin(axis=0)
        below = s < mid
        # Keep only the contiguous run of shadowed frames around the darkest one,
        # so a second, unrelated dip (e.g. the hand) cannot pull the estimate.
        run_start = np.where(~below & (idx <= t_min), idx, -1).max(axis=0) + 1
        run_end = np.where(~below & (idx >= t_min), idx, T).min(axis=0) - 1
        inside = (idx >= run_start) & (idx <= run_end)
        w = np.where(inside, mid - s, 0).clip(min=0)
        centre = (w * idx).sum(axis=0) / (w.sum(axis=0) + 1e-12)
        ok = (hi - lo) > MIN_DEPTH * hi
        t_c[y0:y0 + CHUNK][ok] = centre[ok]
    print(f"{path}: {T} frames, gain {gain.min():.3f}..{gain.max():.3f}, "
          f"{np.isfinite(t_c).mean():.1%} of pixels see the light")
    return t_c


def colour_map(t, valid):
    lo, hi = np.nanpercentile(t, [1, 99])
    im = cv2.applyColorMap(((np.nan_to_num(t, nan=lo) - lo) / (hi - lo) * 255).clip(0, 255).astype(np.uint8),
                           cv2.COLORMAP_JET)
    im[~valid] = 0
    return im


def sweep_angle(t, valid):
    """Direction (radians, image coords) in which the shadow time increases."""
    ys, xs = np.nonzero(valid)
    coef, *_ = np.linalg.lstsq(np.c_[xs, ys, np.ones_like(xs)], t[valid], rcond=None)
    return np.arctan2(coef[1], coef[0])


def denoise(t, valid):
    """5x5 median, then a Gaussian that only averages valid pixels."""
    filled = np.where(valid, t, np.nanmedian(t)).astype(np.float32)
    med = np.where(valid, cv2.medianBlur(filled, 5), 0).astype(np.float32)
    w = valid.astype(np.float32)
    smooth = cv2.GaussianBlur(med, (0, 0), 1.5) / np.maximum(cv2.GaussianBlur(w, (0, 0), 1.5), 1e-6)
    return np.where(valid, smooth, np.nan)


OUT.mkdir(parents=True, exist_ok=True)
cache = OUT / "shadow_times.npy"
if REUSE and cache.exists():
    t_h, t_v = np.load(cache)
else:
    t_h, t_v = shadow_times(paths[0]), shadow_times(paths[1])
    np.save(cache, np.stack([t_h, t_v]))
valid = np.isfinite(t_h) & np.isfinite(t_v)
t_h, t_v = denoise(t_h, valid), denoise(t_v, valid)


def gradient(t):
    g = np.nan_to_num(t, nan=0).astype(np.float32)
    return np.hypot(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)) / 8


eroded = cv2.erode(valid.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
for t in (t_h, t_v):
    g = gradient(t)
    eroded &= g < EDGE_GRAD * np.median(g[eroded])
valid = eroded

# Light-view coordinates. Both sweeps were done with the occluder tilted by
# about the same angle; rotating (t_h, t_v) by it only rolls the virtual
# camera about its optical axis.
roll = (sweep_angle(t_h, valid) + sweep_angle(t_v, valid) - np.pi / 2) / 2 if LEVEL else 0.0
c, s = np.cos(roll), np.sin(roll)
u_all = (c * t_h - s * t_v) * PX_PER_FRAME
v_all = (s * t_h + c * t_v) * PX_PER_FRAME

grid = np.zeros_like(valid)
grid[::STEP, ::STEP] = True
ys, xs = np.nonzero(valid & grid)
u, v = u_all[ys, xs], v_all[ys, xs]
lo_u, hi_u = np.percentile(u, [0.2, 99.8])
lo_v, hi_v = np.percentile(v, [0.2, 99.8])
inside = (u >= lo_u) & (u <= hi_u) & (v >= lo_v) & (v <= hi_v)
xs, ys, u, v = xs[inside], ys[inside], u[inside] - lo_u, v[inside] - lo_v
W, H = int(np.ceil(u.max())) + 1, int(np.ceil(v.max())) + 1

tri = Delaunay(np.c_[u, v])
cam = np.c_[xs, ys].astype(np.float64)
edges = np.stack([np.linalg.norm(cam[tri.simplices[:, i]] - cam[tri.simplices[:, (i + 1) % 3]], axis=1)
                  for i in range(3)]).max(axis=0)
good = edges <= MAX_CAM_EDGE * STEP

gu, gv = np.meshgrid(np.arange(W), np.arange(H))
q = np.c_[gu.ravel(), gv.ravel()].astype(np.float64)
simplex = tri.find_simplex(q)
hit = simplex >= 0
hit[hit] = good[simplex[hit]]
X = tri.transform[simplex[hit]]
b = np.einsum("nij,nj->ni", X[:, :2], q[hit] - X[:, 2])
bary = np.c_[b, 1 - b.sum(axis=1)]
cam_xy = np.einsum("ni,nij->nj", bary, cam[tri.simplices[simplex[hit]]])

floodlit = cv2.imread(str(ROOT / "output" / "floodlit.png"))
k = floodlit.shape[1] / WIDTH                     # timing ran at WIDTH, colours come from full res
map_x = np.full(W * H, -1, np.float32)
map_y = np.full(W * H, -1, np.float32)
map_x[hit], map_y[hit] = cam_xy[:, 0] * k, cam_xy[:, 1] * k
light_view = cv2.remap(floodlit, map_x.reshape(H, W), map_y.reshape(H, W), cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_CONSTANT, borderValue=0)

# Small unmapped specks are sampling gaps; large regions are surfaces the camera never saw.
holes = (~hit).reshape(H, W).astype(np.uint8)
n, labels, stats, _ = cv2.connectedComponentsWithStats(holes, connectivity=4)
small = np.isin(labels, np.nonzero(stats[:, cv2.CC_STAT_AREA] < MAX_HOLE)[0]) & (holes > 0)
light_view = cv2.inpaint(light_view, small.astype(np.uint8), 3, cv2.INPAINT_TELEA)
seen = (~small) & (holes == 0) | small

cv2.imwrite(str(OUT / "light_view.png"), light_view)
cv2.imwrite(str(OUT / "t_h.png"), colour_map(t_h, valid))
cv2.imwrite(str(OUT / "t_v.png"), colour_map(t_v, valid))

h = 540
row = [cv2.resize(floodlit, (h * floodlit.shape[1] // floodlit.shape[0], h), interpolation=cv2.INTER_AREA),
       cv2.resize(light_view, (h * W // H, h))]
cv2.imwrite(str(OUT / "comparison.png"), np.hstack(row))
print(f"roll {np.degrees(roll):+.1f} deg; light view {W}x{H} px, {seen.mean():.1%} of it seen by the camera -> {OUT}")
