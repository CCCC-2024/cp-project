"""Build the four numbered PNG deliverables, review figures, and PNG-only ZIP.

Run after the two edge scripts and the three recorded image_gen calls.
This script lays out existing evidence; it does not synthesize or retouch scenes.
"""
from pathlib import Path
import hashlib
import json
import zipfile
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output'
SUBMISSION = ROOT / 'submission'
FONT_DIR = Path('/System/Library/Fonts/Supplemental')
BG, INK, MUTED, ACCENT = '#ffffff', '#172735', '#4c5b67', '#174d69'


def font(size, bold=False):
    names = [FONT_DIR / ('Arial Bold.ttf' if bold else 'Arial.ttf'),
             Path('/usr/share/fonts/truetype/dejavu') /
             ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')]
    for name in names:
        if name.exists():
            return ImageFont.truetype(str(name), size)
    return ImageFont.load_default(size=size)


def text(draw, xy, value, size, color=INK, bold=False, max_width=None):
    face = font(size, bold)
    box = draw.textbbox((0, 0), value, font=face)
    if max_width is not None and box[2] - box[0] > max_width:
        raise ValueError(f'Text exceeds panel: {value}')
    draw.text(xy, value, font=face, fill=color)


def paste_image(canvas, path, box):
    with Image.open(path) as source:
        source = ImageOps.exif_transpose(source).convert('RGB')
        fitted = ImageOps.contain(source, (box[2], box[3]), Image.Resampling.LANCZOS)
        canvas.paste(fitted, (box[0] + (box[2]-fitted.width)//2,
                              box[1] + (box[3]-fitted.height)//2))


def pair(number, title, filename, left, right, left_label, right_label, notes):
    sheet = Image.new('RGB', (3320, 1520), BG)
    draw = ImageDraw.Draw(sheet)
    text(draw, (40, 22), f'{number}  |  {title}', 46, ACCENT, True, 3240)
    text(draw, (40, 96), left_label, 29, bold=True, max_width=1600)
    text(draw, (1680, 96), right_label, 29, bold=True, max_width=1600)
    paste_image(sheet, left, (40, 150, 1600, 1200))
    paste_image(sheet, right, (1680, 150, 1600, 1200))
    for i, note in enumerate(notes):
        text(draw, (40, 1378 + i * 38), note, 27, MUTED, max_width=3240)
    sheet.save(SUBMISSION / filename)


def review_figures():
    panels = [
        (OUT/'claude/depth_edges.png', 'Claude: original result'),
        (OUT/'code/depth_edges.png', 'Code: registered + denoised depth edges'),
        (OUT/'original_scene.png', 'RGB reference: left-light photograph'),
        (OUT/'code/all_edges.png', 'Code: ALL edges (Canny)'),
    ]
    canvas = Image.new('RGB', (2480, 2060), BG)
    draw = ImageDraw.Draw(canvas)
    text(draw, (30, 20), 'Lab 2 | Existing result and improved code', 36, ACCENT, True)
    for i, (path, label) in enumerate(panels):
        x, y = 30 + (i % 2)*1240, 90 + (i // 2)*980
        text(draw, (x, y), label, 27, bold=True, max_width=1180)
        paste_image(canvas, path, (x, y+48, 1180, 885))
    canvas.save(OUT/'comparison.png')
    panels = [(OUT/'original_scene.png', 'Original scene'),
              (OUT/'ai/reconstruction_depth_edges.png', 'Reconstructed from depth edges'),
              (OUT/'ai/reconstruction_all_edges.png', 'Reconstructed from ALL edges')]
    canvas = Image.new('RGB', (4520, 1310), BG)
    draw = ImageDraw.Draw(canvas)
    text(draw, (30, 20), 'Lab 2 | Reconstruction comparison', 42, ACCENT, True)
    for i, (path, label) in enumerate(panels):
        x = 30 + i*1500
        text(draw, (x, 88), label, 30, bold=True, max_width=1460)
        paste_image(canvas, path, (x, 145, 1460, 1095))
    text(draw, (30, 1260), 'The same prompt and color/material hints were used; each reconstruction call supplied only its corresponding edge image.', 27, MUTED, max_width=4460)
    canvas.save(OUT/'reconstruction_comparison.png')


def main():
    SUBMISSION.mkdir(exist_ok=True)
    with Image.open(ROOT/'images/IMG_2082_left.jpg') as image:
        ImageOps.exif_transpose(image).convert('RGB').save(OUT/'original_scene.png')
    pair('1', 'MULTI-FLASH DEPTH EDGES', '1_depth_edges.png',
         OUT/'original_scene.png', OUT/'code/depth_edges.png',
         'Original scene', 'Depth edges computed from four lighting directions',
         ['SIFT/RANSAC alignment; directional Sobel on intensity ratios; thinning, hysteresis, and small-component removal.',
          'Selected for contour continuity and texture suppression. Residual gaps and displaced shadow boundaries remain.'])
    pair('2', 'AI-INFERRED DEPTH EDGES', '2_ai_depth_edges.png',
         OUT/'original_scene.png', OUT/'ai/depth_edges.png',
         'Original scene supplied to the AI', 'AI-inferred depth edges from a single RGB image',
         ['Generated directly from the RGB image with image_gen; the prompt requests silhouette and occlusion boundaries.',
          'The AI suppresses texture, but it may simplify geometry or infer uncertain background contours. This is not measured depth.'])
    pair('3', 'RECONSTRUCTION FROM DEPTH EDGES', '3_reconstruction_depth_edges.png',
         OUT/'ai/reconstruction_depth_input.png', OUT/'ai/reconstruction_depth_edges.png',
         'Input: computed depth edges', 'AI reconstruction',
         ['Only this edge image was supplied as a visual reference. The same color/material hints were used for both reconstructions.',
          'The bent arrangement is retained, with smoother wood and tabletop detail than in the ALL-edges reconstruction.'])
    pair('4', 'RECONSTRUCTION FROM ALL EDGES', '4_reconstruction_all_edges.png',
         OUT/'code/all_edges.png', OUT/'ai/reconstruction_all_edges.png',
         'Input: ALL edges (Canny)', 'AI reconstruction',
         ['Only this edge image was supplied as a visual reference. The same color/material hints were used for both reconstructions.',
          'Wood grain and tabletop speckles are stronger here. Both reconstructions change some block details and the classroom background.'])
    review_figures()
    files = sorted(SUBMISSION.glob('*.png'))
    expected = ['1_depth_edges.png', '2_ai_depth_edges.png',
                '3_reconstruction_depth_edges.png', '4_reconstruction_all_edges.png']
    if [f.name for f in files] != expected:
        raise ValueError('Unexpected submission PNG inventory')
    manifest = []
    for file in files:
        with Image.open(file) as image:
            image.verify()
        manifest.append({'file': file.name, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
                         'bytes': file.stat().st_size, 'dimensions': [3320, 1520]})
    (OUT/'submission_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    archive = ROOT/'lab2_submission.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for file in files:
            z.write(file, file.name)
    with zipfile.ZipFile(archive) as z:
        assert z.namelist() == expected and z.testzip() is None
        for file in files:
            assert z.read(file.name) == file.read_bytes()
    print('Created and verified exactly four numbered PNGs:', archive)


if __name__ == '__main__':
    main()
