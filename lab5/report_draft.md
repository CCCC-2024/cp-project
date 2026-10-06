# Lab 5 report text, matched to Lab5.docx (sections 1, 2, 4, 5, 6 only)

NOT in this file on purpose: section 3 Observations (the yes/no depth-image answer and the focus-pull text).
The template says a group member writes them, no AI.

---

## Header
Group XX / Member names: [fill in]

## 1 Defocus: images to insert
- Photo: image.jpg
- Combined masks: masks.png
- Layer 1: mask1.png | defocus1.png (plush rooster + table at its depth)
- Layer 2: mask2.png | defocus2.png (spray bottle + table at its depth)
- Layer 3: mask3.png | defocus3.png (tumbler + table at its depth)
- Layer 4: mask4.png | defocus4.png (wall)
The docx has one Layer subsection template: copy it for layers 2, 3, 4 and delete the "Layer X" placeholder.

## 2 Compositing
Each result keeps the sharp photo where the layer's mask is white and takes the Gaussian-blurred photo everywhere else: result_k = M_k * photo + (1 - M_k) * blurred photo. The mask is binary (white above 127 in the 8-bit mask image), so the switch between sharp and blurred happens at the mask boundary and the blurred part is the same strength everywhere. Because the masks come from a depth map and GrabCut, their edges are not perfect, and with this hard switch the edge shows a visible step and, in the blurred side next to a sharp object, a halo of the object's colour (see section 5 for the fix).

## 4 Details
**Scene.** A plush rooster toy on a sloping grey-green table in the foreground (nearest), a lavender hand-sanitizer spray bottle behind and to the left, a yellow tumbler further back, and a plain cream wall behind everything. [Add distances, e.g. rooster about X cm, spray about Y cm, tumbler about Z cm, wall about W cm.] Taken with [phone model], one sharp photo with everything in focus, resized to 1500 x 1125.

**Blur.** Gaussian blur, kernel size 91 x 91, standard deviation sigma = 15 pixels (kernel about 6 sigma + 1).

**Masks.** 4 layers, made with Depth Anything V2 (Small) plus GrabCut. The depth map (0 to 1, larger = nearer) was split into layers with thresholds 0.13, 0.23 and 0.36, so each layer is a band of the table plus the object standing in it; each object was cut out separately with GrabCut seeded from the depth map, so objects are not sliced across table bands. A few things were adjusted by hand: the three boxes around the objects, the thresholds, removal of table-coloured pixels at the objects' feet, and the black pupils of the rooster added to its mask. Layer 1 (rooster, 35.3% of the image), 2 (spray, 5.9%), 3 (tumbler, 7.3%), 4 (wall, 51.5%).

## 5 Extra credit: defocus without halos or holes

**Implementation.** Why both naive versions fail. Blurring the whole photo and then masking leaves a halo: just outside the in-focus object, each blurred pixel is an average over a window that reaches into the object, so the background next to it carries the object's colour. Cutting the object out first leaves a dark fringe and a hole: the removed object is black, and the blur averages those black pixels in, so the background darkens near the object. Both are the same mistake, the blur window contains pixels that are not background. The fix is normalised convolution: B = blur(I * W) / blur(W), where W is 1 on background pixels and 0 on the in-focus layer (W is eroded by 3 px so the imprecise mask edge is not used). Dividing by blur(W) makes the weights sum to one over real background pixels only, so no object colour and no black is averaged in, and the hole under the object is filled from its background neighbours. The in-focus layer is then put back with a soft alpha (mask pulled in 1 px, Gaussian feather sigma 1.5): out = alpha * I + (1 - alpha) * B. To check it we built a synthetic scene (red textured disc on a smooth cream wall) where the correct answer is known; on the ring of 3 sigma pixels outside the disc the mean absolute error is 14.25 for the lab result (halo), 24.52 for cut-out-then-blur (dark fringe) and 0.01 for the clean method (max 0.59). Files: clean.py (method, writes defocus1_clean.png ... defocus4_clean.png), test_clean.py (synthetic check, test_clean.png), compare.py (side-by-side and edge crops), make_masks_objects.py, depth.py, defocus.py.

**Demonstration images.**
- Lab result: defocus1.png | Clean result: defocus1_clean.png (the two halves of compare_1.png)
- Lab result, edge crop: left half of compare_1_crops.png | Clean result, edge crop: right half of compare_1_crops.png
(Crop the two halves from compare_1_crops.png; each half is one panel.)

**Crop caption.** The crops show the red edge of the rooster's head against the wall, enlarged 6 times. In the lab result a pink glow surrounds the edge and the outline is jagged; in the clean result the wall beside the rooster is plain wall colour right up to the edge, with a smooth edge. (Spray bottle: compare_2_crops.png. Tumbler: compare_3_crops.png.)

## 6 AI disclosure (one line per member, each member confirms their own)
[Your name]: Used Claude Code (Anthropic) to write and debug the Python code for the depth map, the layer masks (GrabCut), the defocus and the clean version, and to draft the text in sections 2, 4 and 5. The photo was taken by the group, mask boxes and thresholds were checked and adjusted by eye by [name], and the result was checked by [name].
[Other member]: [what AI tools they used, or "No AI used for ..."]
