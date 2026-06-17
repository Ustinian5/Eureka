from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "extension" / "icons"
FONT = Path("C:/Windows/Fonts/msyhbd.ttc")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for size in (16, 32, 48, 128):
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        radius = max(3, size // 6)
        draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill="#1f6feb")
        draw.ellipse([size * 0.18, size * 0.16, size * 0.82, size * 0.8], fill="#ffffff")
        draw.ellipse([size * 0.32, size * 0.3, size * 0.68, size * 0.66], fill="#1f6feb")
        if size >= 48:
            font = ImageFont.truetype(str(FONT), size // 3) if FONT.is_file() else ImageFont.load_default()
            draw.text((size * 0.34, size * 0.26), "E", font=font, fill="#ffffff")
        image.save(OUT / f"icon-{size}.png")


if __name__ == "__main__":
    main()
