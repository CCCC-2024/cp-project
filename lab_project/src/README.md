# src/ — modules

| file | job |
|---|---|
| `stack_io.py` | load a scene folder (JPG/PNG/HEIC) sorted by name, subsample N frames, save images |
| `align.py` | ECC affine registration to a reference frame (affine absorbs focus-breathing scale) |
| `sharpness.py` | focus measures: Laplacian, Tenengrad, modified Laplacian + Gaussian smoothing (`sigma` ~ patch size) |
| `fuse.py` | argmax focus map, hard vs. soft blending, colorised focus map, `selective_dof` (stretch goal) |
| `experiments.py` | baseline + ablations (N frames, measure, sigma, hard/soft) -> `results/` |
| `make_figures.py` | near / mid / far crop comparison panel |
| `capture_notes.md` | how each stack was shot + what failed |

Run: `pip install -r requirements.txt`, put frames in `data/raw/scene01/01.jpg …`, then
`python src/experiments.py scene01`.

Status: first draft, only smoke-tested on a synthetic stack — not yet on real photos.
Everything here must be understood (and tuned/rewritten) by the person presenting it.
