"""Generate pixel art cat sprites for MeowMate."""
from PIL import Image, ImageDraw
import os
import math

# Colors (RGBA)
T   = (0, 0, 0, 0)            # transparent
OG  = (255, 140, 60, 255)     # orange main fur
OD  = (200, 90, 20, 255)      # orange dark / stripes
WH  = (245, 240, 225, 255)    # cream/white belly
OL  = (45, 22, 8, 255)        # dark brown outline
EP  = (255, 180, 165, 255)    # ear pink
GE  = (75, 200, 90, 255)      # green eyes
PU  = (15, 10, 5, 255)        # pupil black
NS  = (255, 150, 145, 255)    # nose pink
ZC  = (120, 120, 220, 255)    # zzz blue

S   = (72, 64)   # sprite size
ZS  = (32, 32)   # zzz size

os.makedirs('assets/sprites', exist_ok=True)
os.makedirs('assets/icons', exist_ok=True)


def new_img(size=S):
    img = Image.new('RGBA', size, T)
    return img, ImageDraw.Draw(img)


# ── Sitting cat ────────────────────────────────────────────────────────────────

def draw_sitting(draw, cx=36, cy=60, blink=False, look=0, tail=0):
    """
    cx,cy = center-bottom of cat on canvas.
    look: -1=left 0=forward 1=right
    tail: 0-3 wag phase
    """
    # Tail (behind body, drawn first)
    tb = (cx + 15, cy - 14)
    tail_tips = [
        (cx + 26, cy - 28),
        (cx + 28, cy - 32),
        (cx + 22, cy - 30),
        (cx + 24, cy - 35),
    ]
    tip = tail_tips[tail % 4]
    mid = ((tb[0] + tip[0]) // 2 + 8, (tb[1] + tip[1]) // 2)
    for t in range(16):
        f = t / 15
        tx = int((1-f)**2 * tb[0] + 2*(1-f)*f * mid[0] + f**2 * tip[0])
        ty = int((1-f)**2 * tb[1] + 2*(1-f)*f * mid[1] + f**2 * tip[1])
        r = 4 - int(f * 2)
        draw.ellipse([tx-r, ty-r, tx+r, ty+r], fill=OG)
    # tail outline hint
    draw.line([tb, mid, tip], fill=OL, width=1)

    # Body
    draw.ellipse([cx-19, cy-30, cx+19, cy-2], fill=OG, outline=OL, width=1)
    # Belly
    draw.ellipse([cx-10, cy-25, cx+10, cy-5], fill=WH)
    # Body stripe
    draw.arc([cx-15, cy-24, cx+15, cy-10], 200, 340, fill=OD, width=2)

    # Head
    hcy = cy - 42
    draw.ellipse([cx-14, hcy-12, cx+14, hcy+12], fill=OG, outline=OL, width=1)
    # Muzzle
    draw.ellipse([cx-8, hcy+2, cx+8, hcy+12], fill=WH)

    # Left ear
    draw.polygon([(cx-14, hcy-8), (cx-9, hcy-22), (cx-3, hcy-8)],
                 fill=OG, outline=OL)
    draw.polygon([(cx-12, hcy-9), (cx-9, hcy-19), (cx-4, hcy-9)], fill=EP)
    # Right ear
    draw.polygon([(cx+3, hcy-8), (cx+9, hcy-22), (cx+14, hcy-8)],
                 fill=OG, outline=OL)
    draw.polygon([(cx+4, hcy-9), (cx+9, hcy-19), (cx+12, hcy-9)], fill=EP)

    # Eyes
    if blink:
        draw.arc([cx-11, hcy-6, cx-3, hcy+1], 0, 180, fill=OL, width=2)
        draw.arc([cx+3, hcy-6, cx+11, hcy+1], 0, 180, fill=OL, width=2)
    else:
        px = look  # pupil offset
        draw.ellipse([cx-11, hcy-7, cx-3, hcy+1], fill=GE, outline=OL)
        draw.ellipse([cx+3, hcy-7, cx+11, hcy+1], fill=GE, outline=OL)
        draw.ellipse([cx-9+px, hcy-5, cx-4+px, hcy-1], fill=PU)
        draw.ellipse([cx+4+px, hcy-5, cx+9+px, hcy-1], fill=PU)

    # Nose
    draw.polygon([(cx, hcy+4), (cx-2, hcy+7), (cx+2, hcy+7)], fill=NS, outline=OL)
    # Mouth
    draw.line([(cx, hcy+7), (cx-3, hcy+10)], fill=OL, width=1)
    draw.line([(cx, hcy+7), (cx+3, hcy+10)], fill=OL, width=1)
    # Whiskers
    draw.line([(cx-8, hcy+5), (cx-22, hcy+3)], fill=WH, width=1)
    draw.line([(cx-8, hcy+7), (cx-22, hcy+9)], fill=WH, width=1)
    draw.line([(cx+8, hcy+5), (cx+22, hcy+3)], fill=WH, width=1)
    draw.line([(cx+8, hcy+7), (cx+22, hcy+9)], fill=WH, width=1)

    # Paws
    draw.ellipse([cx-18, cy-9, cx-7, cy+1], fill=OG, outline=OL)
    draw.ellipse([cx+7, cy-9, cx+18, cy+1], fill=OG, outline=OL)
    # Toe lines
    for xo in [-16, -12]:
        draw.line([(cx+xo, cy-1), (cx+xo, cy+2)], fill=OL, width=1)
    for xo in [12, 16]:
        draw.line([(cx+xo, cy-1), (cx+xo, cy+2)], fill=OL, width=1)


# ── Sleeping cat ───────────────────────────────────────────────────────────────

def draw_sleeping(draw, cx=36, cy=60, phase=0):
    """
    phase 0-2: curling down transition
    phase 3-5: fully curled
    """
    if phase < 3:
        # Sinking/drooping eyes
        yo = phase * 2
        draw_sitting(draw, cx=cx, cy=cy + yo, blink=True, look=0, tail=0)
        return

    # Fully curled
    bw = 26
    bh = 15
    draw.ellipse([cx-bw, cy-bh*2, cx+bw, cy], fill=OG, outline=OL, width=1)
    # Belly patch
    draw.ellipse([cx-14, cy-bh*2+4, cx+14, cy-4], fill=WH)
    # Stripe
    draw.arc([cx-20, cy-bh*2+2, cx+20, cy-bh], 200, 340, fill=OD, width=2)
    # Tail wrapped to front
    for i in range(12):
        a = math.pi * 0.5 + i * 0.18
        tx = cx + int(bw * math.cos(a))
        ty = cy - 3 + int(4 * math.sin(a * 0.5))
        draw.ellipse([tx-4, ty-3, tx+4, ty+3], fill=OG)
    draw.arc([cx-bw+2, cy-7, cx+bw-2, cy+4], 180, 0, fill=OL, width=1)

    # Head resting, left side
    hx = cx - bw + 14
    hy = cy - bh * 2 + 8
    draw.ellipse([hx-10, hy-9, hx+10, hy+9], fill=OG, outline=OL)
    # Closed eyes
    draw.arc([hx-8, hy-4, hx-1, hy+2], 0, 180, fill=OL, width=2)
    draw.arc([hx+1, hy-4, hx+8, hy+2], 0, 180, fill=OL, width=2)
    # Ear
    draw.polygon([(hx-10, hy-6), (hx-7, hy-16), (hx-2, hy-6)], fill=OG, outline=OL)
    draw.polygon([(hx-1, hy-6), (hx+3, hy-16), (hx+8, hy-6)], fill=OG, outline=OL)


# ── Walking cat ────────────────────────────────────────────────────────────────

def draw_walking(draw, cx=36, cy=58, direction='right', phase=0):
    flip = direction == 'left'
    sx = -1 if flip else 1  # sign for direction

    # Tail (opposite end from head)
    tx0 = cx - sx * 18
    ty0 = cy - 14
    tx1 = cx - sx * 28
    ty1 = cy - 24 - (phase % 2) * 4
    for i in range(12):
        f = i / 11
        bx = int((1-f)*tx0 + f*tx1)
        by = int((1-f)*ty0 + f*ty1)
        r = 4 - int(f * 2)
        draw.ellipse([bx-r, by-r, bx+r, by+r], fill=OG)
    draw.line([(tx0, ty0), (tx1, ty1)], fill=OL, width=1)

    # Body (horizontal)
    draw.ellipse([cx-22, cy-20, cx+22, cy-4], fill=OG, outline=OL, width=1)
    # Belly
    draw.ellipse([cx-14, cy-17, cx+14, cy-7], fill=WH)
    # Body stripe
    draw.arc([cx-18, cy-18, cx+18, cy-8], 200, 340, fill=OD, width=2)

    # Legs (phase animation)
    leg_swings = [
        [-5, 0, 5, 0],
        [-2, 3, 2, -3],
        [5, 0, -5, 0],
        [2, -3, -2, 3],
    ]
    swings = leg_swings[phase % 4]
    leg_xs = [cx - 14, cx - 5, cx + 5, cx + 14]
    for i, (lx, sw) in enumerate(zip(leg_xs, swings)):
        draw.ellipse([lx-3, cy-6+sw, lx+3, cy+10+sw], fill=OG, outline=OL)
        # Paw
        draw.ellipse([lx-4, cy+8+sw, lx+4, cy+13+sw], fill=WH, outline=OL)

    # Head
    hcx = cx + sx * 18
    hcy = cy - 22
    draw.ellipse([hcx-11, hcy-10, hcx+11, hcy+10], fill=OG, outline=OL)
    # Muzzle
    mox = sx * 5
    draw.ellipse([hcx+mox-6, hcy+1, hcx+mox+6, hcy+10], fill=WH)
    # Ear
    draw.polygon([(hcx-6, hcy-8), (hcx, hcy-19), (hcx+6, hcy-8)], fill=OG, outline=OL)
    draw.polygon([(hcx-4, hcy-9), (hcx, hcy-16), (hcx+4, hcy-9)], fill=EP)
    # Eye
    ex = hcx + sx * 4
    draw.ellipse([ex-4, hcy-5, ex+4, hcy+3], fill=GE, outline=OL)
    draw.ellipse([ex-2, hcy-3, ex+2, hcy+1], fill=PU)
    # Nose
    nx = hcx + sx * 8
    draw.polygon([(nx, hcy+3), (nx-2, hcy+6), (nx+2, hcy+6)], fill=NS, outline=OL)
    # Whiskers
    draw.line([(hcx+mox-5, hcy+5), (hcx+mox-5-12*sx, hcy+3)], fill=WH, width=1)
    draw.line([(hcx+mox-5, hcy+7), (hcx+mox-5-12*sx, hcy+9)], fill=WH, width=1)


# ── Zzz frame ─────────────────────────────────────────────────────────────────

def draw_zzz(draw, frame):
    """Three Z's floating upward."""
    # Each Z at different height based on frame, cycling
    sizes  = [10, 8, 6]
    base_y = [22, 14, 6]
    for i, (sz, by) in enumerate(zip(sizes, base_y)):
        # Cycle offset so Z's appear to float up continuously
        offset = (frame * 3 + i * 8) % 24
        y = by - offset
        if y < -sz:
            continue
        alpha = max(40, 220 - offset * 8)
        color = (*ZC[:3], alpha)
        x = 8 + i * 6
        # Draw Z shape
        w = sz
        draw.line([(x, y), (x+w, y)], fill=color, width=max(1, sz//6))
        draw.line([(x+w, y), (x, y+w)], fill=color, width=max(1, sz//6))
        draw.line([(x, y+w), (x+w, y+w)], fill=color, width=max(1, sz//6))


# ── Generate all sprites ───────────────────────────────────────────────────────

print("Generating idle frames (12)...")
idle_params = [
    # (blink, look, tail, y_offset)
    (False, 0, 0, 0),
    (False, 0, 1, 0),
    (False, -1, 1, -1),
    (False, -1, 2, -1),
    (False, 0, 2, 0),
    (True,  0, 2, 0),   # blink
    (False, 0, 3, 0),
    (False, 1, 3, 0),
    (False, 1, 0, 1),
    (False, 0, 0, 1),
    (False, 0, 1, 0),
    (False, 0, 0, 0),
]
for i, (bl, lk, tl, yo) in enumerate(idle_params, 1):
    img, draw = new_img()
    draw_sitting(draw, cx=36, cy=60+yo, blink=bl, look=lk, tail=tl)
    img.save(f'assets/sprites/idle_{i}.png')

print("Generating sleeping frames (6)...")
for i in range(1, 7):
    img, draw = new_img()
    draw_sleeping(draw, cx=36, cy=61, phase=i-1)
    img.save(f'assets/sprites/sleeping_{i}.png')

print("Generating zzz frames (4)...")
for i in range(1, 5):
    img, draw = new_img(ZS)
    draw_zzz(draw, i-1)
    img.save(f'assets/sprites/zzz_{i}.png')

print("Generating walk_left frames (4)...")
for i in range(1, 5):
    img, draw = new_img()
    draw_walking(draw, cx=36, cy=58, direction='left', phase=i-1)
    img.save(f'assets/sprites/walk_left_{i}.png')

print("Generating walk_right frames (4)...")
for i in range(1, 5):
    img, draw = new_img()
    draw_walking(draw, cx=36, cy=58, direction='right', phase=i-1)
    img.save(f'assets/sprites/walk_right_{i}.png')

print("Generating tray icon...")
img, draw = new_img((64, 64))
draw_sitting(draw, cx=32, cy=60, blink=False, look=0, tail=0)
img.save('assets/icons/tray_icon.png')
img_ico = img.resize((32, 32), Image.LANCZOS)
img_ico.save('assets/icons/tray_icon.ico', format='ICO', sizes=[(16,16),(32,32)])

print("All assets generated!")
