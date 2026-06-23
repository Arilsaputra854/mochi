# MeowMate — Sprite Generation Guide

## Tool: Recraft.ai (free)
1. Buka recraft.ai → New Project
2. Style: **Pixel Art**
3. Canvas: **288 x 256 px** (4× dari 72×64, lalu downscale dengan script)
4. Download: PNG, centang **transparent background**

---

## BASE CHARACTER (buat ini DULU — jadi referensi semua frame)

Generate 1 gambar dulu sebagai character reference. Upload hasilnya ke Recraft sebagai "Image Reference" di semua generasi berikutnya.

```
cute chibi orange tabby cat sitting, pixel art, front view,
big round shiny green eyes with white highlight, round chubby body,
cream white belly patch, two pointed ears with pink inner ear,
orange fur with subtle dark orange tabby stripes,
long curvy tail resting beside body, dark brown pixel outline 1px,
transparent background, game sprite, kawaii, no background,
288x256 resolution, centered
```

---

## IDLE FRAMES — 12 frame

Generate **4 sprite sheet terpisah** (masing-masing 4 frame horizontal).

### Idle Sheet A — Neutral breathing (idle_1 s/d idle_4)
Canvas: **1152 x 256 px** (4 frame × 288px)
```
sprite sheet of 4 frames, cute chibi orange tabby cat sitting, pixel art,
sequential idle animation, slight body breathing movement,
frame 1: neutral pose, frame 2: body slightly raised, 
frame 3: neutral, frame 4: body slightly lower,
big round green eyes open, long tail curled beside,
transparent background, no background, evenly spaced frames, 
horizontal layout, 4 identical cat positions with subtle differences,
kawaii pixel art game sprite
```

### Idle Sheet B — Looking around (idle_5 s/d idle_8)
Canvas: **1152 x 256 px**
```
sprite sheet of 4 frames, cute chibi orange tabby cat sitting, pixel art,
sequential animation looking around,
frame 1: looking straight, frame 2: head tilted left, pupils looking left,
frame 3: looking straight, frame 4: head tilted right, pupils looking right,
big round green eyes, round chubby orange body, cream belly,
transparent background, no background, horizontal layout evenly spaced,
kawaii pixel art game sprite
```

### Idle Sheet C — Blink + tail wag (idle_9 s/d idle_12)
Canvas: **1152 x 256 px**
```
sprite sheet of 4 frames, cute chibi orange tabby cat sitting, pixel art,
sequential animation blinking and tail wagging,
frame 1: eyes fully open, tail straight,
frame 2: eyes half closed blinking, tail curved up,
frame 3: eyes closed blinking, tail wagging right,
frame 4: eyes open again, tail back to normal,
transparent background, no background, horizontal layout evenly spaced,
kawaii pixel art game sprite
```

---

## SLEEPING — 6 frame (transisi duduk → melingkar tidur)

Canvas: **1728 x 256 px** (6 frame × 288px) — atau 2 sheet terpisah.

### Sleep Sheet A — Mengantuk (sleeping_1 s/d sleeping_3)
Canvas: **864 x 256 px**
```
sprite sheet of 3 frames, cute chibi orange tabby cat, pixel art,
sequential falling asleep animation,
frame 1: cat sitting, eyes drooping half closed, yawning mouth open,
frame 2: cat sitting, eyes almost closed, head drooping slightly,
frame 3: cat starting to curl, eyes closed, body lowering,
transparent background, no background, horizontal layout,
kawaii pixel art game sprite
```

### Sleep Sheet B — Tidur pulas (sleeping_4 s/d sleeping_6)
Canvas: **864 x 256 px**
```
sprite sheet of 3 frames, cute chibi orange tabby cat, pixel art,
cat curled up sleeping, sequential animation,
frame 1: cat curling into ball, side view, eyes closed,
frame 2: cat fully curled round, tail wrapped around body,
frame 3: cat sleeping deeply, small smile, tiny Zzz bubble above head,
round curled body, transparent background, no background, horizontal layout,
kawaii pixel art game sprite
```

---

## WALK LEFT — 4 frame

Canvas: **1152 x 256 px**
```
sprite sheet of 4 frames, cute chibi orange tabby cat walking left, pixel art,
side view walking animation cycle, cat facing left,
frame 1: left front paw and right back paw forward,
frame 2: all paws neutral walking position,
frame 3: right front paw and left back paw forward,  
frame 4: neutral walking position returning,
tail raised behind, head slightly bobbing, determined cute expression,
transparent background, no background, horizontal layout evenly spaced,
kawaii pixel art game sprite
```

---

## WALK RIGHT — 4 frame

Canvas: **1152 x 256 px**
```
sprite sheet of 4 frames, cute chibi orange tabby cat walking right, pixel art,
side view walking animation cycle, cat facing right, mirrored direction,
frame 1: right front paw and left back paw forward,
frame 2: all paws neutral walking position,
frame 3: left front paw and right back paw forward,
frame 4: neutral walking position returning,
tail raised behind, head slightly bobbing, happy cute expression,
transparent background, no background, horizontal layout evenly spaced,
kawaii pixel art game sprite
```

> **Tip:** Kalau hasil Walk Right kurang memuaskan, generate Walk Left dulu,
> lalu flip horizontal pakai script di bawah.

---

## ZZZ PARTICLES — 4 frame (32×32 px each)

Canvas: **128 x 32 px** (4 frame × 32px)
```
sprite sheet of 4 frames, floating Zzz sleep particles, pixel art,
sequential floating upward animation, cute blue-purple Z letters,
frame 1: one small Z at bottom, faded,
frame 2: small Z middle, one tiny Z at bottom,
frame 3: Z near top fading, Z middle, tiny Z at bottom,
frame 4: all Z's shifted up, lowest one appearing,
transparent background, no background, horizontal layout,
kawaii pixel art game sprite, 128x32 pixels total
```

---

## TRAY ICON — 1 frame (64×64 px)

Canvas: **256 x 256 px** (4× dari 64×64)
```
cute chibi orange tabby cat face, pixel art icon,
front view portrait, big round shiny green eyes,
two pointed ears with pink inside, happy expression,
round chubby face, small pink nose, transparent background,
app icon style, centered, 256x256 pixels, kawaii pixel art
```

---

## DIMENSI RINGKASAN

| Aset | Frame | Canvas di Recraft | Target Final |
|------|-------|-------------------|--------------|
| Idle A/B/C | 4×3 = 12 | 1152×256 px (tiap sheet) | 288×256 → slice → 72×64 |
| Sleep A/B | 3×2 = 6 | 864×256 px (tiap sheet) | slice → 72×64 |
| Walk Left | 4 | 1152×256 px | slice → 72×64 |
| Walk Right | 4 | 1152×256 px | slice → 72×64 |
| Zzz | 4 | 128×32 px | slice → 32×32 |
| Tray Icon | 1 | 256×256 px | resize → 64×64 |

---

## POST-PROCESSING SCRIPT

Setelah download semua PNG dari Recraft, jalankan script ini:

```python
# slice_sprites.py
# Taruh di folder yang sama dengan hasil download dari Recraft.
# Edit SHEET_MAP sesuai nama file yang kamu download.

from PIL import Image
import os

os.makedirs('assets/sprites', exist_ok=True)
os.makedirs('assets/icons', exist_ok=True)

FRAME_W, FRAME_H = 72, 64   # final sprite size
SHEET_W, SHEET_H = 288, 256  # per-frame size in downloaded sheet

def slice_sheet(src_path, prefix, count, frame_w=SHEET_W, frame_h=SHEET_H,
                out_w=FRAME_W, out_h=FRAME_H):
    img = Image.open(src_path).convert('RGBA')
    for i in range(count):
        box = (i * frame_w, 0, (i + 1) * frame_w, frame_h)
        frame = img.crop(box).resize((out_w, out_h), Image.NEAREST)
        frame.save(f'assets/sprites/{prefix}_{i+1}.png')
    print(f"  {prefix}: {count} frames saved")

# EDIT nama file sesuai hasil download kamu:
SHEET_MAP = {
    'idle_sheet_a.png':  ('idle',       4,  SHEET_W, SHEET_H, FRAME_W, FRAME_H),
    'idle_sheet_b.png':  ('idle',       4,  SHEET_W, SHEET_H, FRAME_W, FRAME_H),
    'idle_sheet_c.png':  ('idle',       4,  SHEET_W, SHEET_H, FRAME_W, FRAME_H),
    'sleep_a.png':       ('sleeping',   3,  SHEET_W, SHEET_H, FRAME_W, FRAME_H),
    'sleep_b.png':       ('sleeping',   3,  SHEET_W, SHEET_H, FRAME_W, FRAME_H),
    'walk_left.png':     ('walk_left',  4,  SHEET_W, SHEET_H, FRAME_W, FRAME_H),
    'walk_right.png':    ('walk_right', 4,  SHEET_W, SHEET_H, FRAME_W, FRAME_H),
    'zzz.png':           ('zzz',        4,  32,       32,      32,       32),
}

# Offset counter per prefix (for idle: sheet A = 1-4, B = 5-8, C = 9-12)
prefix_counter = {}

for filename, (prefix, count, fw, fh, ow, oh) in SHEET_MAP.items():
    if not os.path.exists(filename):
        print(f"  SKIP (not found): {filename}")
        continue
    
    start = prefix_counter.get(prefix, 0)
    img   = Image.open(filename).convert('RGBA')
    for i in range(count):
        box   = (i * fw, 0, (i + 1) * fw, fh)
        frame = img.crop(box).resize((ow, oh), Image.NEAREST)
        frame.save(f'assets/sprites/{prefix}_{start + i + 1}.png')
    prefix_counter[prefix] = start + count
    print(f"  {prefix} [{start+1}-{start+count}]: saved from {filename}")

# Tray icon
if os.path.exists('tray_icon.png'):
    img = Image.open('tray_icon.png').convert('RGBA').resize((64, 64), Image.NEAREST)
    img.save('assets/icons/tray_icon.png')
    img.resize((32, 32), Image.NEAREST).save('assets/icons/tray_icon.ico', format='ICO')
    print("  tray icon: saved")

# Flip walk_right dari walk_left kalau perlu
if not os.path.exists('walk_right.png') and os.path.exists('walk_left.png'):
    img = Image.open('walk_left.png').transpose(Image.FLIP_LEFT_RIGHT)
    for i in range(4):
        box   = (i * SHEET_W, 0, (i + 1) * SHEET_W, SHEET_H)
        frame = img.crop(box).resize((FRAME_W, FRAME_H), Image.NEAREST)
        frame.save(f'assets/sprites/walk_right_{i+1}.png')
    print("  walk_right: auto-flipped from walk_left")

print("Done!")
```

Jalankan:
```
py slice_sprites.py
```

---

## TIPS KONSISTENSI DI RECRAFT

1. **Generate BASE CHARACTER dulu** → upload hasilnya sebagai "Image Reference" (strength 70-80%) di semua generasi berikutnya
2. **Style lock**: di Recraft ada fitur "Style" — generate 1 image, save style, apply ke semua
3. Kalau ada frame yang jelek, **regenerate frame itu saja** dengan prompt lebih spesifik
4. **Walk Right** bisa auto-flip dari Walk Left pakai script — hemat 1 generasi
