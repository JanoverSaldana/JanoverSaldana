"""Generate mark-first circular logos for README Trayectoria (256px)."""

from __future__ import annotations

from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "logos" / "journey"
OUT.mkdir(parents=True, exist_ok=True)
SIZE = 256
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def circle_mark(
    mark: Image.Image,
    ring_color: tuple[int, int, int],
    pad: float = 0.18,
    bg: tuple[int, int, int] = (13, 17, 23),
) -> Image.Image:
    """Place a mark centered in a dark circle with colored ring."""
    mark = mark.convert("RGBA")
    inner = int(SIZE * (1 - 2 * pad))
    fitted = mark.copy()
    fitted.thumbnail((inner, inner), Image.Resampling.LANCZOS)

    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, SIZE - 1, SIZE - 1), fill=255)

    canvas = Image.new("RGBA", (SIZE, SIZE), bg + (255,))
    canvas.putalpha(mask)

    x = (SIZE - fitted.width) // 2
    y = (SIZE - fitted.height) // 2
    canvas.paste(fitted, (x, y), fitted)

    ring = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse(
        (3, 3, SIZE - 4, SIZE - 4),
        outline=ring_color + (240,),
        width=6,
    )
    return Image.alpha_composite(canvas, ring)


def crop_box(src: Path, box: tuple[float, float, float, float]) -> Image.Image:
    """Crop relative box (l,t,r,b) as fractions of width/height."""
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    l, t, r, b = box
    return im.crop((int(w * l), int(h * t), int(w * r), int(h * b)))


def render_svg_to_png(svg_path: Path, out_png: Path, width: int, height: int) -> None:
    tmp = ROOT / "assets" / "_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    svg = svg_path.read_text(encoding="utf-8", errors="ignore")
    # Inline SVG styles that GitHub/Chrome can paint on dark bg
    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>html,body{{margin:0;padding:24px;background:#0d1117;width:{width}px;"
        f"height:{height}px;box-sizing:border-box;display:flex;align-items:center;"
        "justify-content:center}}svg{{max-width:100%;height:auto;display:block}}</style>"
        f"</head><body>{svg}</body></html>"
    )
    html_path = tmp / "render.html"
    html_path.write_text(html, encoding="utf-8")
    subprocess.run(
        [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            f"--window-size={width},{height}",
            f"--screenshot={out_png.resolve()}",
            html_path.resolve().as_uri(),
        ],
        capture_output=True,
        check=False,
    )


def write_ntt_loop_svg(path: Path) -> None:
    """Official Dynamic Loop only (no wordmark)."""
    path.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 74 70" width="256" height="242">
  <path fill="#60a5fa" fill-rule="evenodd" d="M45.64,0c-3.32,0-6.59.72-8.9,1.67-2.31-.95-5.58-1.67-8.9-1.67C13.21,0,0,13.84,0,32.82c0,20.7,16.91,36.7,36.74,36.7s36.74-16,36.74-36.7C73.48,13.84,60.27,0,45.64,0h0ZM36.74,11.27c2.82,1.68,6.54,6.54,6.54,12.02,0,4.02-2.65,7.19-6.54,7.19s-6.54-3.16-6.54-7.19c0-5.48,3.72-10.34,6.54-12.02h0ZM36.74,60.48c-15.17,0-27.71-12.2-27.71-27.84,0-14.28,10.31-24.04,18.41-23.68-3.84,3.82-6.16,9.39-6.16,14.79,0,9.27,7.36,15.77,15.47,15.77s15.47-6.5,15.47-15.77c0-5.39-2.33-10.96-6.16-14.79,8.1-.36,18.41,9.39,18.41,23.68,0,15.64-12.55,27.84-27.71,27.84Z"/>
</svg>
""",
        encoding="utf-8",
    )


def write_brand_svg(path: Path, color: str, letter: str, icon_paths: str) -> None:
    path.write_text(
        f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="256" height="256">
  <g fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
    {icon_paths}
  </g>
  <text x="64" y="108" text-anchor="middle" fill="{color}"
        font-family="Segoe UI,Arial,sans-serif" font-size="28" font-weight="800">{letter}</text>
</svg>
""",
        encoding="utf-8",
    )


def save(name: str, img: Image.Image) -> None:
    out = OUT / name
    img.save(out, optimize=True)
    print(f"saved {out.relative_to(ROOT)} ({img.size[0]}x{img.size[1]})")


def main() -> None:
    tmp = ROOT / "assets" / "_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    logos = ROOT / "assets" / "logos"

    # --- NTT Dynamic Loop ---
    ntt_svg = tmp / "ntt-loop.svg"
    write_ntt_loop_svg(ntt_svg)
    ntt_png = tmp / "ntt-loop.png"
    render_svg_to_png(ntt_svg, ntt_png, 320, 320)
    ntt_im = Image.open(ntt_png).convert("RGBA")
    # Trim near-black padding from screenshot
    bbox = ntt_im.getbbox()
    if bbox:
        ntt_im = ntt_im.crop(bbox)
    save("ntt-data.png", circle_mark(ntt_im, (59, 130, 246), pad=0.16))

    # --- Metasoft monogram (left ~26%) ---
    meta = crop_box(logos / "metasoft.png", (0.0, 0.05, 0.26, 0.95))
    save("metasoft.png", circle_mark(meta, (245, 158, 11), pad=0.14))

    # --- Millennium: top icon only (upper ~42%) ---
    mill = crop_box(logos / "millennium.png", (0.18, 0.02, 0.82, 0.42))
    save("millennium.png", circle_mark(mill, (168, 85, 247), pad=0.16))

    # --- StorageData: left S icon only (avoid wordmark bleed) ---
    storage = crop_box(logos / "storagedata.png", (0.0, 0.0, 0.14, 1.0))
    save("storagedata.png", circle_mark(storage, (6, 182, 212), pad=0.18))

    # --- Tracker brand mark ---
    tracker_svg = tmp / "tracker-mark.svg"
    write_brand_svg(
        tracker_svg,
        "#4ade80",
        "TM",
        """
    <rect x="34" y="22" width="60" height="48" rx="8"/>
    <path d="M46 38h36M46 48h24"/>
    <circle cx="64" cy="78" r="6" fill="#4ade80" stroke="none"/>
    <path d="M64 84v8"/>
        """,
    )
    tracker_png = tmp / "tracker-mark.png"
    render_svg_to_png(tracker_svg, tracker_png, 320, 320)
    tr = Image.open(tracker_png).convert("RGBA")
    if tr.getbbox():
        tr = tr.crop(tr.getbbox())
    save("tracker.png", circle_mark(tr, (34, 197, 94), pad=0.12))

    # --- GastroSuite brand mark ---
    gastro_svg = tmp / "gastro-mark.svg"
    write_brand_svg(
        gastro_svg,
        "#fb923c",
        "GS",
        """
    <path d="M40 70c0-18 10-34 24-34s24 16 24 34"/>
    <path d="M48 70h32"/>
    <circle cx="52" cy="42" r="3" fill="#fb923c" stroke="none"/>
    <circle cx="76" cy="42" r="3" fill="#fb923c" stroke="none"/>
    <path d="M56 54h16"/>
        """,
    )
    gastro_png = tmp / "gastro-mark.png"
    render_svg_to_png(gastro_svg, gastro_png, 320, 320)
    gs = Image.open(gastro_png).convert("RGBA")
    if gs.getbbox():
        gs = gs.crop(gs.getbbox())
    save("gastrosuite.png", circle_mark(gs, (249, 115, 22), pad=0.12))

    print("done:", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
