"""Direct/global separation of a static scene from a video taken while a
light or shadow sweeps across it. Every pixel must be directly lit in some
frames and shadowed in others.

    conda run -n cv python forsep.py data/sweep_h.mp4 [data/sweep_v.mp4 ...]

Several videos of the same (unmoved) scene can be passed; the min/max is then
taken over all of their frames, so every pixel gets more than one shadow pass.
Writes output/floodlit.png, output/direct.png and output/global.png.

On top of the starter's plain min/max this version
  * works on linear intensities (video pixels are gamma encoded, and
    floodlit = direct + global only holds for linear light),
  * divides out slow global brightness drift of the light, measured per frame
    on the pixels the shadow is not covering,
  * uses only the frames around the sweep, and averages 3 consecutive frames
    to suppress sensor noise before taking min/max.
"""

import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

args = sys.argv[1:]
OUT = Path(__file__).parent / "output"
if "--out" in args:                  # optional: --out DIR
    i = args.index("--out")
    OUT = Path(args[i + 1])
    del args[i:i + 2]
paths = args or ["video.mp4"]
WORK_WIDTH = 1920    # resolution of the output images
PROBE_WIDTH = 480    # resolution used to measure brightness drift / shadow timing
GAMMA = 2.2
MARGIN = 30          # unshadowed frames kept before and after the sweep
SMOOTH = 3           # frames averaged together before min/max
WHITE = 99.5         # this percentile of the floodlit image is shown as 0.95 (same scale for all three)

def frames(path, width):
    """Yield linear-light BGR float32 frames scaled to `width`.

    The camera records 10-bit video; cv2.VideoCapture would round it to 8 bits,
    which leaves only a handful of levels in the dark global image. ffmpeg
    decodes to 16 bits per channel instead.
    """
    cap = cv2.VideoCapture(path)
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    height = h * width // w
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={width}:{height}:flags=area",
           "-f", "rawvideo", "-pix_fmt", "bgr48le", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    size = width * height * 3 * 2
    while True:
        buf = proc.stdout.read(size)
        if len(buf) < size:
            break
        frame = np.frombuffer(buf, np.uint16).reshape(height, width, 3)
        yield (frame.astype(np.float32) / 65535.0) ** GAMMA
    proc.stdout.close()
    proc.wait()


def probe(path):
    """Per-frame brightness gain and the frame range where the shadow is visible."""
    lum = np.stack([f.mean(axis=2) for f in frames(path, PROBE_WIDTH)])
    ref = np.median(lum, axis=0) + 1e-4          # the shadow covers any pixel only briefly
    ratio = lum / ref
    lit = ratio > 0.85                           # pixels not under the shadow in that frame
    gain = np.array([np.median(r[m]) for r, m in zip(ratio, lit)], dtype=np.float32)
    shadowed = ((ratio / gain[:, None, None]) < 0.6).mean(axis=(1, 2))
    active = np.nonzero(shadowed > 0.002)[0]
    first = max(active[0] - MARGIN, 0)
    last = min(active[-1] + MARGIN, len(lum) - 1)
    return gain, first, last


floodlit_im = None
global_im = None
for path in paths:
    gain, first, last = probe(path)
    print(f"{path}: frames {first}..{last} used, brightness gain {gain.min():.3f}..{gain.max():.3f}")
    window = []
    for k, frame in enumerate(frames(path, WORK_WIDTH)):
        if k < first:
            continue
        if k > last:
            break
        window.append(frame / gain[k])
        if len(window) < SMOOTH:
            continue
        avg = sum(window) / SMOOTH
        window.pop(0)
        if floodlit_im is None:
            floodlit_im, global_im = avg.copy(), avg.copy()
        # The floodlit image is the maximum over time, the global image the minimum.
        np.maximum(floodlit_im, avg, out=floodlit_im)
        np.minimum(global_im, avg, out=global_im)

# The direct image is floodlit minus global (in linear light, never negative).
direct_im = np.clip(floodlit_im - global_im, 0, None)


# One exposure for all three images, so they stay comparable (floodlit = direct + global).
scale = 0.95 / np.percentile(floodlit_im, WHITE)


def to_png(linear):
    return (np.clip(linear * scale, 0, 1) ** (1 / GAMMA) * 255 + 0.5).astype(np.uint8)


OUT.mkdir(exist_ok=True)
cv2.imwrite(str(OUT / "floodlit.png"), to_png(floodlit_im))
cv2.imwrite(str(OUT / "global.png"), to_png(global_im))
cv2.imwrite(str(OUT / "direct.png"), to_png(direct_im))
np.save(OUT / "separation_linear.npy", np.stack([floodlit_im, direct_im, global_im]).astype(np.float16))
share = global_im.mean() / floodlit_im.mean()
print(f"wrote floodlit.png, direct.png, global.png to {OUT}  (global share of floodlit: {share:.1%})")
