from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess

out_dir = Path("assets/logos/journey")
out_dir.mkdir(parents=True, exist_ok=True)
SIZE = 128


def make_text_logo(text: str, color: tuple[int, int, int], filename: str) -> None:
    canvas = Image.new("RGBA", (SIZE, SIZE), (13, 21, 38, 255))
    draw = ImageDraw.Draw(canvas)
    draw.ellipse((2, 2, SIZE - 3, SIZE - 3), outline=color + (255,), width=3)
    try:
        font = ImageFont.truetype("arialbd.ttf", 28 if len(text) <= 3 else 18)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((SIZE - tw) / 2, (SIZE - th) / 2 - 2), text, fill=color + (255,), font=font)
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, SIZE - 1, SIZE - 1), fill=255)
    canvas.putalpha(mask)
    canvas.save(out_dir / filename)
    print("created", filename)


def circle_logo(src: str, name: str, color: tuple[int, int, int]) -> None:
    p = Path(src)
    if not p.exists() or p.stat().st_size < 500:
        print("skip missing", src)
        return
    im = Image.open(p).convert("RGBA")
    logo = im.copy()
    logo.thumbnail((SIZE - 28, SIZE - 28), Image.Resampling.LANCZOS)
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, SIZE - 1, SIZE - 1), fill=255)
    bx = Image.new("RGBA", (SIZE, SIZE), (13, 17, 23, 255))
    bx.putalpha(mask)
    x = (SIZE - logo.width) // 2
    y = (SIZE - logo.height) // 2
    bx.paste(logo, (x, y), logo)
    ring = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((2, 2, SIZE - 3, SIZE - 3), outline=color + (230,), width=3)
    bx = Image.alpha_composite(bx, ring)
    bx.save(out_dir / name)
    print("saved", name, bx.size)


# Render official NTT DATA SVG to PNG
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
html = Path("assets/_tmp_ntt.html")
svg = Path("assets/logos/ntt-data.svg").read_text(encoding="utf-8", errors="ignore")
html.write_text(
    "<!DOCTYPE html><html><body style='margin:0;background:#0d1117;display:flex;"
    f"align-items:center;justify-content:center;width:420px;height:160px'>{svg}</body></html>",
    encoding="utf-8",
)
png_path = Path("assets/logos/ntt-data-render.png")
subprocess.run(
    [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--window-size=420,160",
        f"--screenshot={png_path.resolve()}",
        html.resolve().as_uri(),
    ],
    capture_output=True,
)
print("ntt render", png_path.exists(), png_path.stat().st_size if png_path.exists() else 0)

circle_logo("assets/logos/ntt-data-render.png", "ntt-data.png", (59, 130, 246))
circle_logo("assets/logos/metasoft.png", "metasoft.png", (245, 158, 11))
circle_logo("assets/logos/millennium.png", "millennium.png", (168, 85, 247))
circle_logo("assets/logos/storagedata.png", "storagedata.png", (6, 182, 212))

# No public logos found for Tracker Mobility / GastroSuite (product brands)
make_text_logo("TM", (34, 197, 94), "tracker.png")
make_text_logo("GS", (249, 115, 22), "gastrosuite.png")

print("done:", sorted(p.name for p in out_dir.iterdir()))
