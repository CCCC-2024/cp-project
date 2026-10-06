# Lab 5 pipeline

```
pip install -r requirements.txt     # (use a venv)
# put the photo here as image.jpg
python depth.py                     # depth.npy, depth.png
python make_masks_objects.py         # used for this photo: objects (GrabCut boxes) + depth bands
# python make_masks.py -n 3          # plain depth thresholds (cuts objects across the sloped table)
python defocus.py 15                # defocus*.png, masks.png (colour), masks_gray.png
python clean.py 15                  # defocus*_clean.png   (extra credit)
python compare.py 1 6               # compare_1.png, compare_1_crops.png (args: layer, zoom, [x y])
python test_clean.py 15             # synthetic check of the extra credit, prints errors, writes test_clean.png
```
Check `mask_preview.png` before going on; tune with `-n`, `-t t1 t2 ...`,
`--open/--close/--min-area`. Use the same sigma in defocus.py and clean.py.
