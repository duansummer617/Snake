"""生成 PWA 图标（像素风）。运行：python tools/make_icons.py"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "icons"

BG = (6, 10, 7)
GRID = (13, 23, 16)
BODY = (61, 255, 110)
BODY_DARK = (31, 174, 70)
HEAD = (141, 255, 171)
EYE = (4, 22, 11)
FOOD = (255, 46, 77)
FOOD_LIGHT = (255, 235, 240)
SEAM = (4, 12, 7)

# 32x32 逻辑网格：蛇身路径（左下起，向右、向上、向左），格宽 3
PATH = [(4, 21), (7, 21), (10, 21), (13, 21), (16, 21), (16, 18), (16, 15), (13, 15), (10, 15)]
CELL = 3


def cell(draw, x, y, color, size=CELL):
    draw.rectangle([x, y, x + size - 1, y + size - 1], fill=color)


def draw_base() -> Image.Image:
    img = Image.new("RGB", (32, 32), BG)
    d = ImageDraw.Draw(img)

    for gy in range(2, 31, 4):
        for gx in range(2, 31, 4):
            d.point((gx, gy), fill=GRID)

    for i, (x, y) in enumerate(PATH):
        cell(d, x, y, BODY if i % 3 else BODY_DARK)
        # 分节缝
        d.point((x, y), fill=SEAM)
        d.point((x + CELL - 1, y + CELL - 1), fill=SEAM)

    hx, hy = PATH[-1]
    cell(d, hx, hy, HEAD)
    d.point((hx, hy + 1), fill=EYE)
    d.point((hx, hy + CELL - 2), fill=EYE)

    cell(d, 22, 10, FOOD)
    d.rectangle([23, 11, 24, 12], fill=FOOD_LIGHT)
    return img


def save(img: Image.Image, size: int, name: str) -> None:
    img.resize((size, size), Image.NEAREST).save(OUT / name)


def main() -> None:
    base = draw_base()
    save(base, 512, "icon-512.png")
    save(base, 192, "icon-192.png")
    save(base, 180, "apple-touch-icon-180.png")

    # maskable：内容收在中心 ~78% 安全区内，四周留底色
    pad = 26
    maskable = Image.new("RGB", (32, 32), BG)
    maskable.paste(base.resize((pad, pad), Image.NEAREST), ((32 - pad) // 2, (32 - pad) // 2))
    save(maskable, 512, "icon-maskable-512.png")

    for f in sorted(OUT.glob("*.png")):
        print(f"{f.name}: {f.stat().st_size} bytes")


if __name__ == "__main__":
    main()
