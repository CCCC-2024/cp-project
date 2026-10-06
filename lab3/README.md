# Lab 3 - EPI, COLMAP SfM, VGGT

**Due: Sep 18, 2026, 11:59pm**

## Official deliverables (per assignment text)

- **A**: (a) a picture of the scene, (b) the two EPI images (horizontal +
  perpendicular), (c) a text file with observations — including the patch
  experiment explanation and what happens on playback.
- **B**: a GIF of the 3D structure of the scene, **and** a screenshot of the
  reconstruction + camera positions (colmap gui).
- **C**: a GIF of the VGGT output.

B and C should use one object each; A must use several objects at different
depths.

## Layout

```
partA_epi/
  data/scene_video.mp4       <- your horizontal-translation video goes here
  generate_epi.py            <- builds horizontal/perpendicular EPI + patch experiment
  observations.txt           <- written observations
  output/                    <- generated EPI images, scene.jpg, patched video

partB_colmap/
  data/images/                <- 30-50 photos circling one textured object
  run_colmap.sh               <- feature extraction -> matching -> sparse mapping
  make_gif.py                 <- renders rotating GIF of points + camera poses
  output/                     <- database.db, sparse/, reconstruction.gif

partC_vggt/
  README.md                   <- steps for the hosted VGGT demo (reuses Part B photos)
  make_gif.py                 <- converts a screen recording of the VGGT viewer to GIF
  output/
```

## Part A - EPI

1. Put your video in `partA_epi/data/scene_video.mp4`.
2. Edit `ROW_Y`, `COL_X`, and `PATCH` at the top of `generate_epi.py` to match
   your video's resolution and object placement.
3. `cd partA_epi && python generate_epi.py`
4. Fill in `observations.txt` with what you actually see.

Deliverables: `output/scene.jpg`, the four EPI pngs (original + patched,
horizontal + perpendicular), `observations.txt`.

## Part B - COLMAP

1. Install COLMAP (`brew install colmap`).
2. Put 30-50 photos of one textured object in `partB_colmap/data/images/`.
3. `cd partB_colmap && ./run_colmap.sh`
4. `pip install open3d pycolmap imageio` then `python make_gif.py` to produce
   `output/reconstruction.gif` (point cloud + camera positions, rotating).

Deliverables: `output/reconstruction.gif` **and** a screenshot from
`colmap gui` (File > Import Model) showing the point cloud + camera
positions.

## Part C - VGGT

Reuses the same photos as Part B (see `partC_vggt/README.md`). Upload a
subset to the hosted VGGT demo, screen-record the resulting 3D view, then
convert to GIF with `partC_vggt/make_gif.py`.

Deliverable: `partC_vggt/output/vggt.gif`.
