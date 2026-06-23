"""Generate Mochi tray icon (run once). Needs Pillow."""
import math
from PIL import Image, ImageDraw

def make_mochi_icon(size=256):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)
    s   = size

    def r(x): return int(x * s)
    def c(x, y, rx, ry, fill, outline=None, width=1):
        d.ellipse([r(x-rx), r(y-ry), r(x+rx), r(y+ry)],
                  fill=fill, outline=outline, width=max(1, r(width)))

    # Palette
    CREAM   = (255, 220, 168, 255)
    ORANGE  = (230, 130, 40,  255)
    DARK    = (80,  45,  20,  255)
    WHITE   = (255, 255, 255, 255)
    PINK    = (255, 175, 175, 255)
    NOSE    = (220, 100, 120, 255)
    EYE_C   = (60,  35,  15,  255)
    SHINE   = (255, 255, 255, 220)
    STRIPE  = (215, 110, 25,  200)

    # ── Shadow (subtle, behind everything) ────────────────────────────────
    c(0.50, 0.56, 0.38, 0.08, (0, 0, 0, 40))

    # ── Ears (behind head) ────────────────────────────────────────────────
    # Left ear — rotated triangle via polygon
    def ear(cx, tip_x, tip_y, outer, inner):
        bx, by = r(cx - 0.11), r(0.30)
        bx2, by2 = r(cx + 0.11), r(0.30)
        tx, ty = r(tip_x), r(tip_y)
        d.polygon([(bx, by), (bx2, by2), (tx, ty)], fill=outer)
        # inner ear
        bxi  = int(bx  + (tx - bx ) * 0.25)
        byi  = int(by  + (ty - by ) * 0.30)
        bx2i = int(bx2 + (tx - bx2) * 0.25)
        by2i = int(by2 + (ty - by2) * 0.30)
        txi  = int(bx  + (tx - bx ) * 0.75)
        tyi  = int(by  + (ty - by ) * 0.75)
        d.polygon([(bxi, byi), (bx2i, by2i), (txi, tyi)], fill=inner)

    ear(0.335, 0.265, 0.13, ORANGE, PINK)
    ear(0.665, 0.735, 0.13, ORANGE, PINK)

    # ── Head (big round circle) ────────────────────────────────────────────
    c(0.50, 0.52, 0.36, 0.355, CREAM, ORANGE, 0.012)

    # ── Forehead tabby stripes ─────────────────────────────────────────────
    for ox in (-0.07, 0.0, 0.07):
        x0 = r(0.50 + ox - 0.025)
        x1 = r(0.50 + ox + 0.025)
        y0 = r(0.20)
        y1 = r(0.30)
        d.rounded_rectangle([x0, y0, x1, y1], radius=r(0.015), fill=STRIPE)

    # ── Eyes ──────────────────────────────────────────────────────────────
    for ex in (0.365, 0.635):
        ey = 0.50
        # white sclera
        c(ex, ey, 0.075, 0.065, WHITE)
        # iris (golden brown)
        c(ex, ey, 0.055, 0.055, (180, 120, 40, 255))
        # pupil
        c(ex, ey, 0.033, 0.044, EYE_C)
        # catchlight
        c(ex - 0.018, ey - 0.018, 0.018, 0.018, SHINE)
        c(ex + 0.022, ey + 0.014, 0.010, 0.010, SHINE)

    # ── Nose ──────────────────────────────────────────────────────────────
    nx, ny = r(0.50), r(0.615)
    hw, hh = r(0.038), r(0.030)
    d.polygon([(nx, ny - hh), (nx - hw, ny + hh), (nx + hw, ny + hh)], fill=NOSE)

    # ── Mouth ─────────────────────────────────────────────────────────────
    lw = max(1, r(0.018))
    mx = r(0.50)
    my = r(0.645)
    d.line([(mx, my), (r(0.46), r(0.675))], fill=DARK, width=lw)
    d.line([(mx, my), (r(0.54), r(0.675))], fill=DARK, width=lw)

    # ── Whiskers ──────────────────────────────────────────────────────────
    ww = max(1, r(0.010))
    # left
    d.line([(r(0.15), r(0.60)), (r(0.43), r(0.625))], fill=DARK, width=ww)
    d.line([(r(0.15), r(0.635)), (r(0.43), r(0.640))], fill=DARK, width=ww)
    d.line([(r(0.15), r(0.670)), (r(0.43), r(0.655))], fill=DARK, width=ww)
    # right
    d.line([(r(0.85), r(0.60)), (r(0.57), r(0.625))], fill=DARK, width=ww)
    d.line([(r(0.85), r(0.635)), (r(0.57), r(0.640))], fill=DARK, width=ww)
    d.line([(r(0.85), r(0.670)), (r(0.57), r(0.655))], fill=DARK, width=ww)

    # ── Blush cheeks ──────────────────────────────────────────────────────
    c(0.31, 0.63, 0.065, 0.040, (255, 160, 160, 90))
    c(0.69, 0.63, 0.065, 0.040, (255, 160, 160, 90))

    return img


if __name__ == '__main__':
    import os
    out = os.path.join(os.path.dirname(__file__), 'assets', 'icons')
    os.makedirs(out, exist_ok=True)

    # Full-res
    img256 = make_mochi_icon(256)
    img256.save(os.path.join(out, 'tray_icon.png'))
    print('  tray_icon.png (256x256)')

    # Resize to 64×64 for tray (pystray uses this)
    img64 = img256.resize((64, 64), Image.LANCZOS)
    img64.save(os.path.join(out, 'tray_icon.png'))  # overwrite with 64px version
    print('  tray_icon.png (64x64, overwrite)')

    # ICO with multiple sizes
    sizes = [16, 24, 32, 48, 64, 128, 256]
    icons = [make_mochi_icon(sz) for sz in sizes]
    icons[0].save(
        os.path.join(out, 'tray_icon.ico'),
        format='ICO',
        sizes=[(sz, sz) for sz in sizes],
        append_images=icons[1:],
    )
    print('  tray_icon.ico (multi-size: ' + ', '.join(str(s) for s in sizes) + ')')
    print('Done.')
