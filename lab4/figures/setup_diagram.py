"""Draw the Lab 4 capture setup: top view (scene layout) + side view (pen distance).

    conda run -n cv python figures/setup_diagram.py
Writes figures/setup_diagram.png.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle

FONT = "/Library/Fonts/Arial Unicode.ttf"
font_manager.fontManager.addfont(FONT)
plt.rcParams["font.family"] = font_manager.FontProperties(fname=FONT).get_name()

OUT = Path(__file__).with_suffix(".png")

YELLOW = "#f2c200"
WALL_EDGE = "#555555"


def arrow(ax, p, q, color="k", style="-|>", ls="-", lw=1.5, rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, color=color, lw=lw,
                                 linestyle=ls, mutation_scale=14,
                                 connectionstyle=f"arc3,rad={rad}"))


def top_view(ax):
    ax.set_title("① 俯视图（从上往下看桌面）", fontsize=15, pad=12)

    # table
    ax.add_patch(Rectangle((0.3, 0.3), 9.4, 9.2, fc="#efe6d8", ec="#b9a88c", lw=1.5))
    ax.text(0.5, 0.45, "桌面", fontsize=9, color="#8a7a60")

    # camera field of view
    cam = (4.8, 0.9)
    ax.add_patch(Polygon([cam, (0.7, 8.9), (8.9, 8.9)], fc="#9ecbff", alpha=0.15, ec="none"))
    ax.plot([cam[0], 0.7], [cam[1], 8.9], color="#3a7bd5", lw=1, ls="--")
    ax.plot([cam[0], 8.9], [cam[1], 8.9], color="#3a7bd5", lw=1, ls="--")

    # walls: white back wall + yellow side wall, touching at the back-left corner
    ax.add_patch(Rectangle((1.0, 8.5), 7.8, 0.25, fc="white", ec=WALL_EDGE, lw=1.5))
    ax.add_patch(Rectangle((0.75, 4.3), 0.25, 4.45, fc=YELLOW, ec=WALL_EDGE, lw=1.5))
    ax.text(4.9, 9.0, "白纸 = 后墙 / 背景（立起来）", ha="center", fontsize=11)
    ax.text(0.45, 6.5, "黄纸 = 侧墙（立起来）", rotation=90, va="center", ha="center", fontsize=11)
    ax.annotate("两张纸贴紧成 90°", xy=(1.0, 8.5), xytext=(1.6, 9.35), fontsize=9,
                arrowprops=dict(arrowstyle="->", color="k"))

    # objects
    ax.add_patch(Circle((2.2, 7.4), 0.45, fc="#d62f2f", ec="k"))
    ax.text(2.2, 6.65, "苹果\n(靠近墙角)", ha="center", va="top", fontsize=9.5)
    ax.add_patch(Circle((4.2, 6.9), 0.5, fc="#cfe8f3", ec="#4d7f99", lw=2))
    ax.text(4.2, 6.2, "香薰罐", ha="center", va="top", fontsize=9.5)
    # doll and its real cast shadow (points away from the light, toward back-left)
    ax.add_patch(Polygon([(6.66, 6.51), (5.74, 5.89), (4.94, 7.09), (5.86, 7.71)],
                         fc="#222", alpha=0.45, ec="none"))
    ax.add_patch(Circle((6.2, 6.2), 0.6, fc="#b07a4a", ec="k"))
    ax.text(6.2, 5.35, "玩偶", ha="center", va="top", fontsize=9.5)
    ax.text(5.1, 7.95, "真阴影", ha="center", fontsize=9.5)

    # fake shadow: dark paper cut to the same shape, lying flat on the table
    ax.add_patch(Polygon([(7.3, 7.2), (7.8, 7.2), (7.2, 8.1), (6.7, 8.1)],
                         fc="#222", ec="#000", lw=1.2, hatch="///"))
    ax.annotate("假阴影\n(深色纸剪的，平铺在桌上)\n测量: Direct/Global 都暗\nAI: 当成真阴影 → 骗 AI",
                xy=(7.6, 7.5), xytext=(8.05, 5.3), fontsize=8.5, color="#a33",
                arrowprops=dict(arrowstyle="->", color="#a33"))

    # camera
    ax.add_patch(Rectangle((cam[0] - 0.45, cam[1] - 0.35), 0.9, 0.55, fc="#333", ec="k"))
    ax.text(cam[0], cam[1] - 0.55, "DJI 相机（正前方，固定）", ha="center", va="top", fontsize=10.5)

    # light + pen
    light = (9.2, 1.8)
    ax.add_patch(Circle(light, 0.28, fc="#fff38a", ec="#c79a00", lw=2))
    ax.text(light[0], light[1] - 0.45, "光源\n(右前方偏高，固定)", ha="center", va="top", fontsize=10)
    pen = (7.95, 3.25)
    ax.add_patch(Circle(pen, 0.12, fc="#1d3fbf", ec="k"))
    ax.text(pen[0] + 0.25, pen[1] - 0.1, "笔（竖拿）\n约在光源→场景 1/3 处\n在画面外", fontsize=8.5,
            color="#1d3fbf", va="top")
    arrow(ax, (pen[0] - 0.35, pen[1] - 0.35), (pen[0] + 0.35, pen[1] + 0.35),
          color="#1d3fbf", style="<|-|>", lw=1.3)

    # pen shadow sweeping across the scene
    ax.plot([pen[0], 4.1], [pen[1], 8.45], color="#444", lw=9, alpha=0.18, solid_capstyle="butt")
    ax.text(6.75, 4.2, "笔影（扫过全场）", fontsize=8.5, color="#444", rotation=-53)

    # interreflection path: light -> yellow wall -> white wall
    arrow(ax, light, (1.05, 5.3), color="#e0a800", lw=1.4)
    arrow(ax, (1.05, 5.3), (2.9, 8.45), color="#e0a800", ls="--", lw=1.8)
    ax.text(1.35, 4.35, "① 光照到黄纸内侧", fontsize=9, color="#a07600")
    ax.text(2.45, 8.05, "② 黄光反弹到白墙", fontsize=9, color="#a07600")
    ax.add_patch(Rectangle((1.0, 8.5), 2.4, 0.25, fc=YELLOW, alpha=0.45, ec="none"))

    ax.set_xlim(0, 10.2)
    ax.set_ylim(-0.3, 10.3)
    ax.set_aspect("equal")
    ax.axis("off")


def side_view(ax):
    ax.set_title("② 侧视图：笔放在哪里", fontsize=15, pad=12)

    # table + scene
    ax.add_patch(Rectangle((0, -0.3), 10, 0.3, fc="#d8c7a8", ec="none"))
    ax.add_patch(Rectangle((9.3, 0), 0.15, 3.2, fc="white", ec=WALL_EDGE))
    ax.text(9.7, 1.6, "白墙", rotation=90, va="center", fontsize=10)
    ax.add_patch(Circle((8.3, 0.45), 0.45, fc="#b07a4a", ec="k"))
    ax.text(8.3, 1.05, "物品", ha="center", fontsize=9.5)

    # light on a stand
    light = (0.8, 3.6)
    ax.plot([light[0], light[0]], [0, light[1] - 0.25], color="#888", lw=3)
    ax.add_patch(Circle(light, 0.25, fc="#fff38a", ec="#c79a00", lw=2))
    ax.text(light[0], light[1] + 0.4, "光源", ha="center", fontsize=11)

    # pen cross-section at ~D/3, shadow wedge
    pen_x, pen_y, half = 3.3, 2.75, 0.09
    tgt_x = 9.3

    def hit(y0):
        s = (tgt_x - light[0]) / (pen_x - light[0])
        return light[1] + (y0 - light[1]) * s

    top, bot = hit(pen_y + half), hit(pen_y - half)
    ax.add_patch(Polygon([(pen_x, pen_y + half), (tgt_x, top), (tgt_x, bot), (pen_x, pen_y - half)],
                         fc="#444", alpha=0.25, ec="none"))
    for y in (pen_y + half, pen_y - half):
        ax.plot([light[0], tgt_x], [light[1], hit(y)], color="#c79a00", lw=0.8)
    ax.add_patch(Circle((pen_x, pen_y), 0.1, fc="#1d3fbf", ec="k", zorder=5))
    ax.text(pen_x, pen_y + 0.35, "笔", ha="center", color="#1d3fbf", fontsize=11)
    ax.annotate("影子宽 ≈ 笔粗 × D/d\n≈ 3 cm", xy=(tgt_x - 0.05, (top + bot) / 2), xytext=(5.6, 3.3),
                fontsize=9.5, arrowprops=dict(arrowstyle="->"))

    # hand far from beam
    ax.plot([pen_x, pen_x], [pen_y, 4.4], color="#8b5a2b", lw=2)
    ax.text(pen_x + 0.15, 4.35, "捏住末端 / 绑在尺子上\n手不进光路", fontsize=8.5, va="top")

    # distances
    arrow(ax, (light[0], -0.8), (tgt_x, -0.8), style="<|-|>", lw=1)
    ax.text((light[0] + tgt_x) / 2, -1.2, "D ≈ 50–100 cm", ha="center", va="top", fontsize=10)
    arrow(ax, (light[0], -0.35 - 0.1), (pen_x, -0.45), style="<|-|>", lw=1, color="#1d3fbf")
    ax.text((light[0] + pen_x) / 2, -0.55, "d ≈ D/3", ha="center", va="top", fontsize=9.5,
            color="#1d3fbf")

    ax.text(5.0, -2.1, "笔离光源太近 → 影子太宽；离场景太近 → 笔进画面",
            ha="center", fontsize=9.5, color="#a33")

    ax.set_xlim(-0.2, 10.3)
    ax.set_ylim(-2.5, 4.9)
    ax.set_aspect("equal")
    ax.axis("off")


def main():
    fig, (a, b) = plt.subplots(1, 2, figsize=(17, 8.5), gridspec_kw={"width_ratios": [1.05, 1]})
    top_view(a)
    side_view(b)
    fig.text(0.5, 0.02,
             "只有笔在动：相机、光源、所有物品全程固定。横扫 = 笔竖拿左→右；竖扫 = 笔横拿上→下。"
             "影子起点、终点都在画面外。",
             ha="center", fontsize=11.5)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(OUT, dpi=150)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
