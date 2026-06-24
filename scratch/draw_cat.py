import os
from PIL import Image

def create_sprite():
    # Define color palette
    BG = (0, 0, 0, 0)
    ORANGE = (242, 133, 34, 255)
    SHADOW_ORANGE = (204, 102, 15, 255)
    DARK_ORANGE = (171, 74, 10, 255) # Tabby stripes
    CREAM = (255, 233, 212, 255) # Chest, muzzle, paws
    WHITE = (255, 255, 255, 255) # Eye shine
    GREEN_DARK = (14, 82, 46, 255)
    GREEN_MID = (32, 145, 82, 255)
    GREEN_LIGHT = (60, 219, 126, 255)
    PUPIL = (11, 26, 17, 255)
    PINK = (247, 168, 184, 255) # Ears, nose
    DARK_PINK = (214, 114, 134, 255) # Mouth/nose shadow
    
    # 32x32 grid size
    grid_w, grid_h = 32, 32
    
    def set_px(pixels, x, y, color):
        if 0 <= x < grid_w and 0 <= y < grid_h:
            pixels[x, y] = color

    def draw_line(pixels, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            set_px(pixels, x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def draw_cat(frame_idx):
        # Create empty image
        img = Image.new('RGBA', (grid_w, grid_h), BG)
        pixels = img.load()
        
        # Frame specific details
        # Frame 1-2: Normal hanging, tail straight down
        # Frame 3-4: Same, tail left
        # Frame 5-6: Tail right, body swayed right by 1 pixel
        
        body_sway = 0
        if frame_idx in (5, 6):
            body_sway = 1
            
        # Draw arms hanging from top
        # Left arm
        for y in range(0, 6):
            set_px(pixels, 9, y, ORANGE)
            set_px(pixels, 10, y, SHADOW_ORANGE)
        # Right arm
        for y in range(0, 6):
            set_px(pixels, 21 + body_sway, y, ORANGE)
            set_px(pixels, 22 + body_sway, y, SHADOW_ORANGE)
            
        # Draw paws at y=0 (cream color)
        set_px(pixels, 8, 0, CREAM)
        set_px(pixels, 9, 0, CREAM)
        set_px(pixels, 10, 0, CREAM)
        
        set_px(pixels, 20 + body_sway, 0, CREAM)
        set_px(pixels, 21 + body_sway, 0, CREAM)
        set_px(pixels, 22 + body_sway, 0, CREAM)
        
        # Draw ears
        # Left ear
        for y in range(2, 6):
            for x in range(8, 8 + (y - 1)):
                set_px(pixels, x, y, ORANGE)
        # Pink inside left ear
        set_px(pixels, 9, 3, PINK)
        set_px(pixels, 9, 4, PINK)
        set_px(pixels, 10, 4, PINK)
        # Left ear stripe
        set_px(pixels, 8, 3, DARK_ORANGE)
        set_px(pixels, 8, 4, DARK_ORANGE)

        # Right ear
        for y in range(2, 6):
            for x in range(23 + body_sway - (y - 2), 24 + body_sway):
                set_px(pixels, x, y, ORANGE)
        # Pink inside right ear
        set_px(pixels, 22 + body_sway, 3, PINK)
        set_px(pixels, 22 + body_sway, 4, PINK)
        set_px(pixels, 21 + body_sway, 4, PINK)
        # Right ear stripe
        set_px(pixels, 23 + body_sway, 3, DARK_ORANGE)
        set_px(pixels, 23 + body_sway, 4, DARK_ORANGE)

        # Draw Head Base (y=5..14)
        for y in range(5, 15):
            x_start = 8 + body_sway
            x_end = 23 + body_sway
            if y == 5:
                x_start += 3
                x_end -= 3
            elif y == 6:
                x_start += 1
                x_end -= 1
            elif y == 14:
                x_start += 1
                x_end -= 1
                
            for x in range(x_start, x_end + 1):
                set_px(pixels, x, y, ORANGE)
                
        # Tabby stripes on forehead
        for y in range(5, 7):
            set_px(pixels, 15 + body_sway, y, DARK_ORANGE)
            set_px(pixels, 16 + body_sway, y, DARK_ORANGE)
        set_px(pixels, 13 + body_sway, 5, DARK_ORANGE)
        set_px(pixels, 18 + body_sway, 5, DARK_ORANGE)
        
        # Tabby stripes on cheeks
        set_px(pixels, 8 + body_sway, 9, DARK_ORANGE)
        set_px(pixels, 9 + body_sway, 9, DARK_ORANGE)
        set_px(pixels, 8 + body_sway, 10, DARK_ORANGE)
        set_px(pixels, 22 + body_sway, 9, DARK_ORANGE)
        set_px(pixels, 23 + body_sway, 9, DARK_ORANGE)
        set_px(pixels, 23 + body_sway, 10, DARK_ORANGE)

        # Draw Eyes (y=8..11)
        eye_y_centers = [8, 9, 10, 11]
        for ey in eye_y_centers:
            # Left eye
            for ex in range(11 + body_sway, 15 + body_sway):
                if (ey == 8 and ex in (11 + body_sway, 14 + body_sway)) or \
                   (ey == 11 and ex in (11 + body_sway, 14 + body_sway)):
                    continue
                # Color based on depth
                if ey == 8:
                    color = GREEN_DARK
                elif ey == 11:
                    color = GREEN_LIGHT
                else:
                    color = GREEN_MID
                set_px(pixels, ex, ey, color)
                
            # Right eye
            for ex in range(17 + body_sway, 21 + body_sway):
                if (ey == 8 and ex in (17 + body_sway, 20 + body_sway)) or \
                   (ey == 11 and ex in (17 + body_sway, 20 + body_sway)):
                    continue
                # Color based on depth
                if ey == 8:
                    color = GREEN_DARK
                elif ey == 11:
                    color = GREEN_LIGHT
                else:
                    color = GREEN_MID
                set_px(pixels, ex, ey, color)
                
        # Pupils
        # Left pupil
        set_px(pixels, 13 + body_sway, 9, PUPIL)
        set_px(pixels, 13 + body_sway, 10, PUPIL)
        # Right pupil
        set_px(pixels, 19 + body_sway, 9, PUPIL)
        set_px(pixels, 19 + body_sway, 10, PUPIL)
        
        # Eye shines
        set_px(pixels, 12 + body_sway, 9, WHITE)
        set_px(pixels, 18 + body_sway, 9, WHITE)

        # Muzzle (cream)
        for y in range(11, 14):
            for x in range(13 + body_sway, 19 + body_sway):
                if y == 11 and x in (13 + body_sway, 18 + body_sway):
                    continue
                if y == 13 and x in (13 + body_sway, 18 + body_sway):
                    continue
                set_px(pixels, x, y, CREAM)
                
        # Nose
        set_px(pixels, 15 + body_sway, 11, PINK)
        set_px(pixels, 16 + body_sway, 11, PINK)
        
        # Mouth
        set_px(pixels, 15 + body_sway, 12, DARK_PINK)
        set_px(pixels, 16 + body_sway, 12, DARK_PINK)
        set_px(pixels, 14 + body_sway, 12, SHADOW_ORANGE)
        set_px(pixels, 17 + body_sway, 12, SHADOW_ORANGE)

        # Draw Body
        for y in range(14, 23):
            x_start = 10 + body_sway
            x_end = 21 + body_sway
            if y == 14:
                x_start += 1
                x_end -= 1
            elif y == 22:
                x_start += 1
                x_end -= 1
            for x in range(x_start, x_end + 1):
                # Check for shading
                if x in (x_start, x_end):
                    set_px(pixels, x, y, SHADOW_ORANGE)
                else:
                    set_px(pixels, x, y, ORANGE)
                    
        # Body stripes
        for y in (16, 17, 19, 20):
            set_px(pixels, 10 + body_sway, y, DARK_ORANGE)
            set_px(pixels, 21 + body_sway, y, DARK_ORANGE)
        # Vertical stripes on lower back
        set_px(pixels, 13 + body_sway, 21, DARK_ORANGE)
        set_px(pixels, 18 + body_sway, 21, DARK_ORANGE)

        # Chest patch (cream)
        for y in range(14, 21):
            x_start = 13 + body_sway
            x_end = 18 + body_sway
            if y == 14:
                x_start += 1
                x_end -= 1
            for x in range(x_start, x_end + 1):
                set_px(pixels, x, y, CREAM)
                
        # Draw dangling legs
        # Left leg (orange with cream paw)
        for y in range(23, 27):
            color = CREAM if y >= 25 else ORANGE
            set_px(pixels, 10 + body_sway, y, color)
            set_px(pixels, 11 + body_sway, y, color)
            if y < 25:
                set_px(pixels, 12 + body_sway, y, SHADOW_ORANGE)
            else:
                set_px(pixels, 12 + body_sway, y, CREAM)
                
        # Right leg (orange with cream paw)
        for y in range(23, 27):
            color = CREAM if y >= 25 else ORANGE
            set_px(pixels, 20 + body_sway, y, color)
            set_px(pixels, 21 + body_sway, y, color)
            if y < 25:
                set_px(pixels, 19 + body_sway, y, SHADOW_ORANGE)
            else:
                set_px(pixels, 19 + body_sway, y, CREAM)

        # Draw Tail (Frame specific)
        if frame_idx in (1, 2):
            # Tail straight down
            for y in range(22, 31):
                color = DARK_ORANGE if y in (24, 27, 30) else ORANGE
                set_px(pixels, 15, y, color)
                set_px(pixels, 16, y, color)
        elif frame_idx in (3, 4):
            # Tail swaying left
            # y=22: 15..16
            # y=23: 15..16
            # y=24: 14..15
            # y=25: 14..15
            # y=26: 13..14
            # y=27: 13..14
            # y=28: 12..13
            # y=29: 12..13
            # y=30: 11..12
            tail_x_offsets = {
                22: 0, 23: 0,
                24: -1, 25: -1,
                26: -2, 27: -2,
                28: -3, 29: -3,
                30: -4
            }
            for y in range(22, 31):
                offset = tail_x_offsets[y]
                color = DARK_ORANGE if y in (24, 27, 30) else ORANGE
                set_px(pixels, 15 + offset, y, color)
                set_px(pixels, 16 + offset, y, color)
        elif frame_idx in (5, 6):
            # Tail swaying right (body is shifted by +1)
            # y=22: 15..16 + 1
            # y=23: 15..16 + 1
            # y=24: 16..17 + 1
            # y=25: 16..17 + 1
            # y=26: 17..18 + 1
            # y=27: 17..18 + 1
            # y=28: 18..19 + 1
            # y=29: 18..19 + 1
            # y=30: 19..20 + 1
            tail_x_offsets = {
                22: 0, 23: 0,
                24: 1, 25: 1,
                26: 2, 27: 2,
                28: 3, 29: 3,
                30: 4
            }
            for y in range(22, 31):
                offset = tail_x_offsets[y]
                color = DARK_ORANGE if y in (24, 27, 30) else ORANGE
                set_px(pixels, 15 + body_sway + offset, y, color)
                set_px(pixels, 16 + body_sway + offset, y, color)

        # Scale image up 3x using Nearest Neighbor
        scaled_img = img.resize((96, 96), Image.NEAREST)
        return scaled_img

    # Ensure output directories exist
    os.makedirs('assets/sprites', exist_ok=True)
    artifact_dir = r"C:\Users\tunas\.gemini\antigravity\brain\81eef777-5ced-45e7-826c-114552f227b0"
    os.makedirs(artifact_dir, exist_ok=True)

    for i in range(1, 7):
        img = draw_cat(i)
        
        # Save to assets/sprites
        path = os.path.join('assets/sprites', f'clinging_{i}.png')
        img.save(path)
        print(f"Saved sprite to {path}")
        
        # Save copy to artifact dir for preview
        artifact_path = os.path.join(artifact_dir, f'clinging_{i}.png')
        img.save(artifact_path)
        print(f"Saved artifact preview to {artifact_path}")

if __name__ == '__main__':
    create_sprite()
