"""Create a paper-style 2x2 comparison figure for Lab 0."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdf_canvas


ROOT = Path(__file__).resolve().parent
PNG_OUTPUT = ROOT / "lab0_final_2x2.png"
PDF_OUTPUT = ROOT / "output" / "pdf" / "lab0_final_2x2.pdf"

PANELS = [
    ("(a) Original image", ROOT / "mountains.png"),
    (
        "(b) 8-level quantization",
        ROOT / "quantization_candidates" / "quantized_8_levels.png",
    ),
    ("(c) ControlNet image", ROOT / "cai.jpeg"),
    ("(d) GPT-generated image", ROOT / "gptai.jpeg"),
]

# A 3:2 canvas at 300 dpi. The PDF uses the same 12 x 8 inch layout.
CANVAS_WIDTH = 3600
CANVAS_HEIGHT = 2400
PAGE_MARGIN_X = 120
PAGE_MARGIN_Y = 100
COLUMN_GAP = 100
ROW_GAP = 100
LABEL_HEIGHT = 95
IMAGE_LABEL_GAP = 22

BACKGROUND = "white"
TEXT_COLOR = "black"


def get_caption_font(size: int) -> ImageFont.ImageFont:
    """Use a conventional serif font similar to a LaTeX paper caption."""
    font_paths = [
        "/System/Library/Fonts/Times.ttc",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf",
    ]
    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size=size)
        except (OSError, ValueError):
            continue
    return ImageFont.load_default()


def create_figure() -> Image.Image:
    """Build the four-panel image without cropping or stretching any source."""
    figure = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(figure)
    caption_font = get_caption_font(42)

    grid_width = CANVAS_WIDTH - 2 * PAGE_MARGIN_X
    grid_height = CANVAS_HEIGHT - 2 * PAGE_MARGIN_Y
    panel_width = (grid_width - COLUMN_GAP) // 2
    panel_height = (grid_height - ROW_GAP) // 2
    image_height = panel_height - LABEL_HEIGHT

    for index, (label, image_path) in enumerate(PANELS):
        row, column = divmod(index, 2)
        panel_x = PAGE_MARGIN_X + column * (panel_width + COLUMN_GAP)
        panel_y = PAGE_MARGIN_Y + row * (panel_height + ROW_GAP)

        source = ImageOps.exif_transpose(Image.open(image_path)).convert("RGB")
        fitted = ImageOps.contain(
            source,
            (panel_width, image_height),
            method=Image.Resampling.LANCZOS,
        )

        image_x = panel_x + (panel_width - fitted.width) // 2
        image_y = panel_y + (image_height - fitted.height) // 2
        figure.paste(fitted, (image_x, image_y))

        caption_box = draw.textbbox((0, 0), label, font=caption_font)
        caption_width = caption_box[2] - caption_box[0]
        caption_y = panel_y + image_height + IMAGE_LABEL_GAP
        draw.text(
            (panel_x + (panel_width - caption_width) // 2, caption_y),
            label,
            fill=TEXT_COLOR,
            font=caption_font,
        )

    return figure


def save_pdf(png_path: Path, pdf_path: Path) -> None:
    """Place the figure on a borderless 12 x 8 inch PDF page."""
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    page_width = 12 * 72
    page_height = 8 * 72
    pdf = pdf_canvas.Canvas(str(pdf_path), pagesize=(page_width, page_height))
    pdf.drawImage(
        ImageReader(str(png_path)),
        0,
        0,
        width=page_width,
        height=page_height,
        preserveAspectRatio=True,
        mask="auto",
    )
    pdf.showPage()
    pdf.save()


def main() -> None:
    figure = create_figure()
    figure.save(PNG_OUTPUT, format="PNG", dpi=(300, 300), optimize=True)
    save_pdf(PNG_OUTPUT, PDF_OUTPUT)
    print(f"Saved PNG: {PNG_OUTPUT}")
    print(f"Saved PDF: {PDF_OUTPUT}")


if __name__ == "__main__":
    main()
