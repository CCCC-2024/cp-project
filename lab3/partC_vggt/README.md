# Part C - VGGT

VGGT itself runs as a hosted Hugging Face Space demo, so there is no local
Python pipeline to write for the model itself — reuse the *same* photo set
as Part B.

## Steps

1. Pick ~8-20 photos from `../partB_colmap/data/images/` that cover the main
   viewpoints around the object (you don't need all 30-50).
2. Open the VGGT demo (Facebook/Meta's Hugging Face Space) and upload those
   images.
3. Run the reconstruction and rotate the resulting 3D viewer to inspect the
   point cloud / cameras.
4. Screen-record the rotating viewer (e.g. QuickTime screen recording on
   macOS), then convert the recording to a GIF with `make_gif.py` below.

## make_gif.py

Converts a screen recording (mp4/mov) of the VGGT viewer into a GIF.

```
pip install imageio imageio-ffmpeg
python make_gif.py --video output/vggt_recording.mov --out output/vggt.gif
```
