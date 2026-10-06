# Lab 5: Simulated Defocus

Group [XX]: [Member], [Member], [Member]

Section numbers follow Lab5.docx. Figures are listed by file name.

---

## 1 Defocus

**Photo:** `image.jpg`  **Combined masks:** `masks.png`

| Layer | Content | Mask | Result |
|---|---|---|---|
| 1 (nearest) | plush rooster + table at its depth (35.3% of the image) | `mask1.png` | `defocus1.png` |
| 2 | spray bottle + table at its depth (5.9%) | `mask2.png` | `defocus2.png` |
| 3 | tumbler + table at its depth (7.3%) | `mask3.png` | `defocus3.png` |
| 4 (farthest) | wall (51.5%) | `mask4.png` | `defocus4.png` |

---

## 2 Compositing

Every result is built from two versions of the same photo: the sharp original `I` and a copy `B` blurred with one Gaussian (kernel 91 x 91, sigma 15) over the whole frame. The layer's mask `M_k` decides, pixel by pixel, which one is shown:

result_k = M_k · I + (1 − M_k) · B

Where the mask is white the pixel is copied unchanged from the sharp photo; where it is black the pixel comes from the blurred photo. The mask is binary, so there is no blending: the switch from sharp to blurred happens exactly on the mask boundary, and the blurred part has the same strength everywhere, whatever the true distance of the pixel. The four masks together cover every pixel exactly once, so each frame has one in-focus layer and three out-of-focus layers, and the four frames differ only in which mask is applied. Played in order 1 to 4 they imitate the focus being pulled from the nearest object to the wall.

At the mask edges this plain composite has two defects. The edge is a hard step (and follows the slightly jagged boundary of the mask), and the blurred side right next to a sharp object contains a blur window that reaches into the object, so it is tinted with the object's colour: a halo. Section 5 removes both.

---

## 3 Observations (Ari writes this; facts she may need)

**Settings used (from the code)**
- Blur: Gaussian, kernel 91 x 91, sigma 15, the same strength everywhere outside the in-focus layer.
- 4 layers from a Depth Anything V2 depth map (0 = far, 1 = near), split at 0.13 / 0.23 / 0.36; each object cut out separately, then joined to the layer of its own depth.
- Rough depth values: wall 0.09, tumbler 0.18, spray bottle 0.28, rooster 0.40 to 0.45; table from 0.04 (far edge) to 0.86 (bottom of frame).
- Layer sizes: 1 rooster + near table 35.3%, 2 spray bottle + table 5.9%, 3 tumbler + table 7.3%, 4 wall 51.5%.
- Each layer is "an object plus the table at the same depth".
- Colours in `masks.png` are assigned by layer number (viridis), nearest is yellow.

**Where to look for the two questions**
- Depth image: compare `masks.png` with `depth.png` (smooth gradient on the table vs flat bands).
- Focus pull: look at `defocus1.png` to `defocus4.png` in order; compare how blurred the spray bottle and the wall are in frame 1; look at where the sharp table band ends.

## 4 Details

**Scene.** A plush rooster toy sits in the foreground (nearest to the camera) on a sloping grey-green table. A lavender hand-sanitizer spray bottle stands behind it on the left, a yellow tumbler stands further back in the middle, and a plain cream wall is behind everything. Relative depths from the depth map (0 = far, 1 = near): wall about 0.09, tumbler about 0.18, spray bottle about 0.28, rooster about 0.40 to 0.45; the table runs from about 0.04 at its far edge to about 0.86 at the bottom of the frame. [Add real distances: rooster about __ cm, spray bottle __ cm, tumbler __ cm, wall __ cm.] One sharp photo with everything in focus was taken with [phone model], resized to 1500 x 1125.

**Blur.** Gaussian blur, kernel size 91 x 91, standard deviation sigma = 15 pixels (kernel = 6 sigma + 1), image borders replicated.

**Masks.** 4 layers, made with **Depth Anything V2 (Small)**. The depth map (normalised to 0 to 1, larger = nearer) was split with thresholds 0.13, 0.23 and 0.36 into four bands. Because the table is one continuous slope, plain thresholds would slice the objects across table bands, so each object (rooster, spray bottle, tumbler) was first cut out with GrabCut, started from a hand-drawn box and seeded from the depth map, and assigned to the layer of its own median depth (rooster layer 1, spray bottle layer 2, tumbler layer 3); the rest of the scene (table, wall) goes to the layer of its depth band. Small hand adjustments: the three boxes, the thresholds, removing table-coloured pixels that GrabCut kept at the objects' feet, and adding the rooster's two black pupils to its mask.

---

## 5 Extra credit: defocus without halos or holes

### Implementation

**Why both naive versions fail.** Write `I` for the photo, `M` for the mask of the in-focus object (1 on the object).

- *Blur the whole photo, then mask* (the lab result). A blurred pixel just outside the object is an average over a window of radius about 3 sigma, and that window reaches into the object. So the background beside the object is mixed with the object's colour: a **halo** of subject colour.
- *Cut the object out, then blur.* The removed object is filled with black (0), and these zeros are averaged into the blur like real data. The background darkens near the object: a **dark fringe**, and a **hole** where the object was.

Both come from the same mistake: the blur window contains pixels that are not background, either the object's colour or fake black.

**The fix: normalised convolution.** Let `W` = 1 on background pixels and 0 on the in-focus layer (eroded by 3 px so the imprecise mask edge is not used as background). The out-of-focus image is

B = blur(I · W) / blur(W)

The numerator adds up only background colours; the denominator is the total weight of the background pixels in the window. Dividing by it renormalises so the weights sum to one over real background pixels only: the object's colour never enters, the black stand-in never enters, and wherever the window overlaps the object the value is filled in from the surrounding background (no hole). The in-focus layer is then composited back with a soft alpha (mask pulled in by 1 px to drop edge pixels that mix object and background, then feathered with a Gaussian of sigma 1.5):

out = α · I + (1 − α) · B

**Check against a known answer.** A synthetic scene (red textured disc on a smooth cream wall) lets us compute the correct result directly: sharp disc, wall blurred using wall pixels only. On the ring of 3 sigma pixels just outside the disc (sigma 15):

| Method | mean abs error | max abs error |
|---|---|---|
| Lab result (halo) | 14.25 | 62.40 |
| Cut out, then blur (dark fringe) | 24.52 | 103.73 |
| Clean (normalised) | 0.01 | 0.59 |

On the real photo the clean frames (`defocus1_clean.png` to `defocus4_clean.png`) keep the in-focus region identical to the photo (mean difference below 0.04 grey levels) and remove the halo at every edge.

**Files.** `clean.py` (the method; writes `defocus1_clean.png` to `defocus4_clean.png`), `test_clean.py` (synthetic check, `test_clean.png`), `compare.py` (side-by-side images and edge crops), `make_masks_objects.py`, `depth.py`, `defocus.py`.

### Demonstration

- Lab result: `defocus1.png`  |  Clean result: `defocus1_clean.png`
- Lab result, edge crop: `crop_lab_result.png`  |  Clean result, edge crop: `crop_clean_result.png`

**Crop caption.** The crops show the lower-left edge of the rooster's red head against the wall in frame 1, enlarged 6 times. In the lab result the wall next to the edge is tinted pink, a halo of the rooster's red that fades over about 30 pixels, and the outline is jagged because the mask switches pixel by pixel. In the clean result the wall beside the rooster is plain wall colour right up to the edge, there is no dark or red band, and the edge is smooth because of the 1.5-pixel feather.

---
