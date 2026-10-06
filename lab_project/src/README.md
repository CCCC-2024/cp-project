# src/ — planned modules (one file each, written by us)

| file | job |
|---|---|
| `capture_notes.md` | how each stack was shot (camera, tripod, focus steps, settings) |
| `align.py` | register every frame to a reference (ECC / ORB+homography); compensate focus breathing (scale change between frames) |
| `sharpness.py` | per-pixel / per-patch focus measure: Laplacian variance, Tenengrad (Sobel), modified Laplacian; Gaussian smoothing of the measure |
| `fuse.py` | argmax over the stack -> focus map; hard selection vs. soft (weighted) blending; seam smoothing |
| `experiments.py` | vary stack size N, patch size, focus measure; save outputs to `results/` |
| `make_figures.py` | comparison panels for the report/slides |
