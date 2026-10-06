"""Demonstration: step-4 result beside the clean result, plus zoomed edge crops.

Run:
    python compare.py [k] [zoom] [x y]   # layer k (default 1), zoom (default 4), crop centre (default: automatic)
Outputs:
    compare_k.png        full images side by side (step 4 | clean)
    compare_k_crops.png  the same edge crop, zoomed, step 4 | clean
The crop is centred where the layer's boundary shows the biggest difference between the two.
"""

import sys

import cv2
import numpy as np

k = int(sys.argv[1]) if len(sys.argv) > 1 else 1
zoom = int(sys.argv[2]) if len(sys.argv) > 2 else 4
CENTRE = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else None  # optional: x y of the crop
a = cv2.imread(f"defocus{k}.png")
b = cv2.imread(f"defocus{k}_clean.png")
m = cv2.imread(f"mask{k}.png", cv2.IMREAD_GRAYSCALE)


def label(img, text):
    img = img.copy()
    cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
    cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    return img


cv2.imwrite(f"compare_{k}.png", np.hstack([label(a, "step 4"), label(b, "clean")]))

edge = cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
half = 40
diff = np.abs(a.astype(np.float32) - b.astype(np.float32)).mean(2)
# Only count edges where the in-focus photo itself has strong contrast (the
# subject's outline), not the soft boundaries between blurred regions.
src = cv2.cvtColor(cv2.imread("image.jpg"), cv2.COLOR_BGR2GRAY).astype(np.float32)
diff = diff * np.hypot(cv2.Sobel(src, cv2.CV_32F, 1, 0), cv2.Sobel(src, cv2.CV_32F, 0, 1))
near_edge = cv2.dilate(edge.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
density = cv2.boxFilter(diff * near_edge, -1, (2 * half, 2 * half))
density[:half], density[-half:], density[:, :half], density[:, -half:] = 0, 0, 0, 0
y, x = np.unravel_index(density.argmax(), density.shape)
if CENTRE:
    x, y = CENTRE
crop = lambda img: cv2.resize(img[y - half : y + half, x - half : x + half], None, fx=zoom, fy=zoom, interpolation=cv2.INTER_NEAREST)
cv2.imwrite(f"compare_{k}_crops.png", np.hstack([label(crop(a), "step 4"), label(crop(b), "clean")]))
print(f"wrote compare_{k}.png and compare_{k}_crops.png (crop centre x={x}, y={y})")
