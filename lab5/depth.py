"""Step 0: estimate a depth map with Depth Anything V2.

Run:
    python depth.py [image.jpg]
Outputs:
    depth.npy   float32 relative depth, 0..1, LARGER = NEARER
    depth.png   the same as a grey image (white = near) for inspection
"""

import sys

import cv2
import numpy as np
from PIL import Image
from transformers import pipeline

MODEL = "depth-anything/Depth-Anything-V2-Small-hf"  # swap for -Base-hf / -Large-hf for better quality

path = sys.argv[1] if len(sys.argv) > 1 else "image.jpg"
img = Image.open(path).convert("RGB")

pipe = pipeline("depth-estimation", model=MODEL)
depth = np.array(pipe(img)["predicted_depth"].squeeze(), dtype=np.float32)

# The network output is at its own resolution: resize to the photo.
depth = cv2.resize(depth, img.size, interpolation=cv2.INTER_CUBIC)
depth = (depth - depth.min()) / (depth.max() - depth.min() + 1e-8)

np.save("depth.npy", depth)
cv2.imwrite("depth.png", (255 * depth).astype(np.uint8))
print(f"wrote depth.npy and depth.png ({img.size[0]}x{img.size[1]})")
