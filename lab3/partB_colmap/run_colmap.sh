#!/usr/bin/env bash
# Part B - Structure from Motion with COLMAP
#
# Prereqs: `brew install colmap` (or build from source), video frames placed
# in data/images/ (see extract_frames.sh / the fps note below).
#
# IMPORTANT: extract frames DENSELY (~6-8 fps) from an orbit video rather
# than a handful of far-apart photos. With sparse/wide-baseline frames,
# COLMAP's incremental mapper can fail to find a valid initial pair (a
# "rotation-only"-looking degenerate geometry) even when the camera genuinely
# translated around the object, especially for rotationally-symmetric or
# low-texture objects. Dense frames let the incremental reconstruction grow
# one small, well-conditioned step at a time instead of needing one big
# wide-baseline pair to succeed. sequential_matcher (not exhaustive_matcher)
# is used below because it's built for this ordered/dense-video case.
#
# Usage:
#   cd partB_colmap
#   ffmpeg -i data/video/<your_video>.MOV -vf fps=8 data/images/frame_%03d.jpg
#   ./run_colmap.sh

set -euo pipefail

PROJECT_DIR="$(pwd)"
IMAGE_DIR="$PROJECT_DIR/data/images"
DB_PATH="$PROJECT_DIR/output/database.db"
SPARSE_DIR="$PROJECT_DIR/output/sparse"

mkdir -p "$PROJECT_DIR/output"
rm -f "$DB_PATH"
rm -rf "$SPARSE_DIR"
mkdir -p "$SPARSE_DIR"

echo "== Feature extraction =="
colmap feature_extractor \
    --database_path "$DB_PATH" \
    --image_path "$IMAGE_DIR" \
    --ImageReader.single_camera 1 \
    --FeatureExtraction.use_gpu 0

echo "== Feature matching (sequential, for ordered video frames) =="
colmap sequential_matcher \
    --database_path "$DB_PATH" \
    --FeatureMatching.use_gpu 0 \
    --SequentialMatching.overlap 15

echo "== Sparse reconstruction (mapper) =="
colmap mapper \
    --database_path "$DB_PATH" \
    --image_path "$IMAGE_DIR" \
    --output_path "$SPARSE_DIR"

echo "== Done. Sparse model(s) written to $SPARSE_DIR/0, /1, ... =="
echo "Registered-image count per model (pick the largest one for make_gif.py --model):"
for d in "$SPARSE_DIR"/*/; do
    n=$(colmap model_analyzer --path "$d" 2>&1 | grep "Registered images" | grep -o '[0-9]*')
    echo "  $d -> $n images"
done
echo "Open with: colmap gui  (File > Import Model -> output/sparse/<N>)"
echo "Or run make_gif.py --model output/sparse/<N> to render a rotating GIF."
