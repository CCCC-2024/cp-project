"""Lab 5: simulated defocus.

Over the next few weeks we cover camera focus and defocus, and projector
focus and defocus. This lab is a hand-crafted way of understanding them: a
real lens blurs each part of the scene by an amount that depends on its
depth, and here we fake that with masks drawn by hand.

Inputs, next to this file:
    image.jpg                  a photo with many different depths in it
    mask1.png, mask2.png, ...  one image per depth layer, the same size as
                               the photo, white where that layer is and
                               black elsewhere (paint them, or use Segment
                               Anything or Depth Anything, see the lab page)
Run:
    python defocus.py
Outputs:
    defocus1.png, ...   the photo with everything outside mask k blurred
    masks.png           every mask in one image; does it look like depth?
Extra credit (optional, not done here): defocus1_clean.png, ...
"""

import glob
import sys

import cv2
import numpy as np

im = cv2.imread("image.jpg")

# A Gaussian blur has two parameters: the kernel size and the standard
# deviation. The size should cover the bell, about six sigmas. This blur is
# the same everywhere in the image; defocus is not, which is the point.
sigma = int(sys.argv[1]) if len(sys.argv) > 1 else 10  # python defocus.py 15
im_blur = cv2.GaussianBlur(im, (6 * sigma + 1, 6 * sigma + 1), sigma, borderType=cv2.BORDER_REPLICATE)

masks = sorted(glob.glob("mask[0-9]*.png"), key=lambda s: int(s[4:-4]))
overall = np.zeros(im.shape[:2], np.uint8)

for k, name in enumerate(masks, start=1):
    # White in the mask means "in focus", so keep the photo there and take
    # the blurred version everywhere else.
    mask = cv2.imread(name, cv2.IMREAD_GRAYSCALE) > 127
    defocused = np.where(mask[:, :, None], im, im_blur)
    cv2.imwrite(f"defocus{k}.png", defocused)

    # Give each layer its own grey level so the masks can be shown together.
    overall[mask] = k

# Scale the layer numbers to the full grey range and look at the result:
# does it read as a depth image? Layer 1 is the nearest, so flip it to make
# near bright like a depth image, and also write a colour-mapped version.
grey = (255 * overall.astype(float) / len(masks)).astype(np.uint8)
cv2.imwrite("masks_gray.png", grey)
levels = np.where(overall > 0, 255 * (len(masks) - overall.astype(float) + 1) / len(masks), 0).astype(np.uint8)
cv2.imwrite("masks.png", cv2.applyColorMap(levels, cv2.COLORMAP_VIRIDIS))
print(f"wrote {len(masks)} defocused images, masks.png (colour) and masks_gray.png")
