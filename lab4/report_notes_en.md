# Lab 4 Report Reference Notes (for the teammate writing the report)

> ⚠️ The template requires **"2 Features" to be written by a group member, not by an AI**. Part 1 below contains only **observations and data** (where to look, what you see, why). Please write the paragraphs in your own words; do not copy these notes verbatim.
> Part 2 (Limitations) is not under that rule and can be used as a reference or as-is.
> All numbers are measured in linear intensity from `output/separation_linear.npy`. "Share" means Global / Floodlit.

---

## Part 1: Features — observation notes

### 1.1 Specularities → appear in the Direct image

**Where to look** (compare `output/direct.png` with `output/global.png`):
- Small bright highlight on the front-left of the apple
- **Curved bright line along the mug's inner rim**, plus a vertical streak of reflection inside the mug
- **Rim of the metal lid** on the candle jar
- **Edges of the silver metal baseboards** at the bottom-left and bottom-right of the frame
- The flashlight's **circular hot spot** on the white paper, which is the pattern of the direct illumination itself

**What you see**: these are the brightest pixels in Direct. At the same locations, Global has no highlight.

**Why**: a highlight is a mirror-like reflection. Light leaves the source, reflects once off the surface and goes straight into the camera, which is a single bounce and therefore direct. When the occluder's shadow passes, the direct light is blocked and the highlight disappears, so it shows up in `max − min`.

### 1.2 Shadows → dark in the Direct image

**Where to look**:
- **The doll's cast shadow on the red paper**, on the red paper to the left of the doll's head and body
- The contact shadow where the apple touches the table
- The side of the apple facing away from the light (attached shadow)

**Data** (doll's shadow vs. the lit red paper next to it):

| | Floodlit | Direct | Global |
|---|---|---|---|
| Inside the doll's shadow | 0.023 | 0.019 | 0.004 |
| Lit red paper nearby | 0.102 | 0.084 | 0.018 |

Direct inside the shadow is about **4.4× darker**.

**Why**: points inside a cast shadow cannot "see" the light source, so they receive no single-bounce light. The only light left there is light bounced from other surfaces.

**Worth adding honestly**: in theory, Global should be about the same inside and outside the shadow. Ours is darker inside the shadow too (0.004 vs 0.018). See Part 2, items 1 and 2, for why.

### 1.3 Interreflections → appear in the Global image

**Where to look** (`output/global.png`):
- **The mug turns yellow**: in Global the mug body is clearly yellow, while in Direct it is a neutral white.
  - Data: the blue/red ratio of the mug body is 0.42 in Floodlit and **0.05** in Global (lower = yellower).
  - Cause: the yellow envelope sits directly in front of the mug. Once lit, it bounces yellow light onto the mug.
- **The corner between the white and red paper glows red**: in Global, the white paper near the red paper and the corner itself take on a red tint (colour bleeding).
- **The mug interior is bright**: the inside wall is concave, so light bounces around inside it several times.

**Why**: Global is light that first hit another surface and then bounced toward the point. After one bounce, the light carries the colour of the first surface it hit, which is why white surfaces get "tinted" yellow or red.

---

## Part 2: Limitations (English draft, usable as-is)

**1. Hand-held light source.** The phone flashlight was held by hand. Its brightness varied by about ±10% during each sweep. We divided out this global flicker frame by frame, using pixels that were not in the occluder's shadow. Changes in the light's *direction* cannot be corrected this way, however: they slightly move highlights and shadow edges between frames, which can leave some spurious direct light near cast-shadow boundaries.

**2. Occluder width trade-off.** In a first capture with a thin pen, the shadow never became fully dark inside the flashlight's hot spot. Seen from there, the whole lens of the flashlight is lit and looks wider than the pen, so the pen formed only a penumbra, and part of the direct light leaked into the global image as a visible bright disk. We switched to a wider (about 1.5–2 cm) occluder, which produces a true umbra everywhere (the shadow now removes about 96% of the light even in the hot spot). The cost is a wider shadow: up to about 12% (horizontal sweep) and 25% (vertical sweep) of the frame was shadowed at the same time. This also blocks part of the indirect light, so our global image is probably an underestimate (it is about 6% of the floodlit image overall), and cast shadows stay darker in the global image than theory predicts. The clearest evidence is a pixel inside the doll's cast shadow on the red paper. It is never lit directly, yet its brightness falls slowly, over about 200 frames, to 30–40% as the wide shadow covers the surrounding surfaces that bounce light onto it. A directly lit pixel instead drops sharply to its floor in a few frames. That slow loss of indirect light is wrongly counted as "direct" inside cast shadows.

**3. Exposure and bit depth.** The final capture was about 1.5 stops underexposed. To keep precision in the dim global image, we decoded the 10-bit video at 16 bits per channel instead of 8.

**4. Linearization.** Separation has to be done in linear light. We assumed a gamma of 2.2 for the camera's "Normal" colour profile. However, the tone setting was "Vivid", which adds extra contrast and saturation, and DJI does not publish the exact curve. So the absolute direct/global ratios carry some uncertainty; which regions are direct and which are global is not affected.

**5. Shadow camera (extra credit).**
- The occluder was swept by hand. We assumed constant speed and mapped one video frame to one light-view pixel on both axes, so non-uniform speed shows up as mild stretching.
- Both sweeps were tilted by about 12.7°. We rolled the virtual camera about its optical axis to level the image.
- The black regions in the light view are of two kinds. Some are surfaces the light sees but the camera does not. The others are pixels whose shadow timing is unreliable: specular surfaces (the metal lid), the mug interior, and depth edges. We left them black instead of hallucinating content.

---

## Part 3: Extra credit — observations (see `output/shadow_camera/comparison.png`)

1. **The viewpoint changes**: the light is at the upper left, so the result looks as if seen from above and to the left. The perspective of the wall corner and the table changes, and the mug looks "taller".
2. **Cast shadows disappear**: the light cannot see what it does not illuminate, so the doll's and the apple's cast shadows in the camera view do not exist in the light's view. This is the effect pointed out in Fig. 3 of the paper.
3. **Implementation steps** (for "How you implemented the shadow camera"):
   - For each pixel, find the sub-frame time at which the occluder's shadow is centred on it, `t_h` and `t_v`. Smooth the brightness curve over 5 frames, take the contiguous shadowed run around the darkest frame, and compute its weighted centre.
   - Use `(t_h, t_v)` as the pixel coordinates of the light's view.
   - Build a Delaunay triangulation of the camera pixels in that coordinate system. Each light-view pixel looks up its corresponding camera position and takes its colour from the floodlit image (Helmholtz reciprocity: `I_light(t_h, t_v) = I_camera(x, y)`).
   - Triangles stretched long in the camera image straddle a depth edge, so those locations are left black.
