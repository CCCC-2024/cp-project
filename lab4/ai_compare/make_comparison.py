"""2x2 figure: measured direct/global (top) vs AI direct/global (bottom).

    conda run -n cv python ai_compare/make_comparison.py
"""
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
panels = [("Measured direct", "output/direct.png"), ("Measured global", "output/global.png"),
          ("AI direct", "ai_compare/ai_direct.png"), ("AI global", "ai_compare/ai_global.png")]
fig, axs = plt.subplots(2, 2, figsize=(14, 8.2))
for ax, (title, path) in zip(axs.ravel(), panels):
    ax.imshow(cv2.cvtColor(cv2.imread(str(ROOT / path)), cv2.COLOR_BGR2RGB))
    ax.set_title(title, fontsize=13)
    ax.axis("off")
fig.tight_layout()
fig.savefig(ROOT / "ai_compare" / "comparison.png", dpi=120)
print("wrote ai_compare/comparison.png")
