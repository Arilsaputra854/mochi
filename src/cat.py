import os
import tkinter as tk
from enum import Enum


class State(Enum):
    IDLE        = 'idle'
    WALK_LEFT   = 'walk_left'
    WALK_RIGHT  = 'walk_right'
    SLEEP_ENTER = 'sleep_enter'
    SLEEPING    = 'sleeping'
    SLEEP_EXIT  = 'sleep_exit'
    TYPING      = 'typing'
    CLICKED     = 'clicked'
    PLAYING     = 'playing'
    HUNGRY      = 'hungry'
    BETE        = 'bete'
    PULANG      = 'pulang'
    EATING      = 'eating'
    MOUSE_CLICK = 'mouse_click'
    DRAGGED     = 'dragged'
    PAT         = 'pat'
    FALLING     = 'falling'
    LANDING     = 'landing'
    DANCE       = 'dance'
    SCARE       = 'scare'
    YAWN        = 'yawn'
    STRETCH     = 'stretch'
    CLEAN       = 'clean'
    JUMP        = 'jump'
    SIT         = 'sit'
    SCRATCH     = 'scratch'
    WAVE        = 'wave'
    HISS        = 'hiss'


_SPRITE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'sprites')


def _load(pattern, count):
    frames = []
    for i in range(1, count + 1):
        path = os.path.join(_SPRITE_DIR, f'{pattern}_{i}.png')
        if os.path.exists(path):
            frames.append(tk.PhotoImage(file=path))
    return frames


class Cat:
    WALK_SPEED  = 3
    MARGIN      = 5
    SPRITE_W    = 96
    SPRITE_H    = 96

    def __init__(self):
        from win32api import GetMonitorInfo, MonitorFromPoint
        work = GetMonitorInfo(MonitorFromPoint((0, 0)))['Work']
        self.screen_x = work[0]
        self.screen_y = work[1]
        self.screen_w = work[2]
        self.screen_h = work[3]

        self.x = self.screen_w // 2
        self.y = self.screen_h - self.SPRITE_H
        self.vy = 0.0

        self.state      = State.IDLE
        self._frame_idx = 0
        self._tick_counter = 0
        self.on_anim_end = None  # callback(State)

        # Define delay per state (number of 50ms ticks to wait before advancing frame)
        self._anim_delays = {
            State.IDLE: 4,         # 200ms per frame
            State.WALK_LEFT: 3,    # 150ms per frame
            State.WALK_RIGHT: 3,   # 150ms per frame
            State.SLEEP_ENTER: 4,  # 200ms per frame
            State.SLEEPING: 8,     # 400ms per frame
            State.SLEEP_EXIT: 4,   # 200ms per frame
            State.TYPING: 2,       # 100ms per frame (fast typing!)
            State.CLICKED: 3,      # 150ms per frame
            State.PLAYING: 3,      # 150ms per frame
            State.HUNGRY: 8,       # 400ms per frame
            State.BETE: 8,         # 400ms per frame
            State.PULANG: 8,       # 400ms per frame
            State.EATING: 4,       # 200ms per frame
            State.MOUSE_CLICK: 2,  # 100ms per frame (fast click reaction!)
            State.DRAGGED: 2,      # 100ms per frame (wiggling feet!)
            State.PAT: 3,          # 150ms per frame (love heart animation!)
            State.FALLING: 2,      # 100ms per frame (flailing paws!)
            State.LANDING: 3,      # 150ms per frame (landing bounce!)
            State.DANCE:   3,
            State.SCARE:   2,
            State.YAWN:    4,
            State.STRETCH: 4,
            State.CLEAN:   3,
            State.JUMP:    2,
            State.SIT:     6,
            State.SCRATCH: 2,
            State.WAVE:    3,
            State.HISS:    2,
        }

        self._look_frames = {}
        for d in ['center', 'left', 'right', 'up', 'down', 'up_left', 'up_right', 'down_left', 'down_right']:
            self._look_frames[d] = _load(f'idle_look_{d}', 6)

        sleeping_enter = _load('sleeping', 6)
        sleeping_exit  = sleeping_enter[::-1]

        self._frames = {
            State.IDLE:        _load('idle', 6),
            State.WALK_LEFT:   _load('walk_left', 6),
            State.WALK_RIGHT:  _load('walk_right', 6),
            State.SLEEP_ENTER: sleeping_enter,
            State.SLEEPING:    _load('zzz', 4),
            State.SLEEP_EXIT:  sleeping_exit,
            State.TYPING:      _load('typing', 4),
            State.CLICKED:     _load('clicked', 4),
            State.PLAYING:     _load('play', 6),
            State.HUNGRY:      _load('hungry', 2),
            State.BETE:        _load('bete', 2),
            State.PULANG:      _load('pulang', 2),
            State.EATING:      _load('eating', 6),
            State.MOUSE_CLICK: _load('mouse_click', 4),
            State.DRAGGED:     _load('dragged', 6),
            State.PAT:         _load('pat', 8),
            State.FALLING:     _load('falling', 2),
            State.LANDING:     _load('landing', 3),
            State.DANCE:       _load('dance', 8),
            State.SCARE:       _load('scare', 6),
            State.YAWN:        _load('yawn', 4),
            State.STRETCH:     _load('stretch', 5),
            State.CLEAN:       _load('clean', 5),
            State.JUMP:        _load('jump', 4),
            State.SIT:         _load('sit', 3),
            State.SCRATCH:     _load('scratch', 6),
            State.WAVE:        _load('wave', 6),
            State.HISS:        _load('hiss', 7),
        }

    def set_state(self, new_state: State):
        if self.state != new_state:
            self.state      = new_state
            self._frame_idx = 0
            self._tick_counter = 0
            if new_state == State.FALLING:
                self.vy = 0.0

    def get_frame(self, rx=None, ry=None):
        frames = self._frames.get(self.state, [])
        if not frames:
            return None

        # Custom logic for eye tracking during idle state
        if self.state == State.IDLE:
            idx = self._frame_idx % len(frames)
            
            d = 'center'
            if rx is not None and ry is not None:
                cx, cy = self.SPRITE_W // 2, self.SPRITE_H // 2
                dx = rx - cx
                dy = ry - cy
                
                if abs(dx) < 40 and abs(dy) < 40:
                    d = 'center'
                elif dx < -40 and dy < -40:
                    d = 'up_left'
                elif dx > 40 and dy < -40:
                    d = 'up_right'
                elif dx < -40 and dy > 40:
                    d = 'down_left'
                elif dx > 40 and dy > 40:
                    d = 'down_right'
                elif dx < -40:
                    d = 'left'
                elif dx > 40:
                    d = 'right'
                elif dy < -40:
                    d = 'up'
                elif dy > 40:
                    d = 'down'
                    
            if hasattr(self, '_look_frames') and d in self._look_frames:
                return self._look_frames[d][idx]

            return frames[idx]

        return frames[self._frame_idx % len(frames)]

    def tick(self, mx=None, my=None):
        # Dynamically query monitor based on mouse position to support multi-screen!
        if mx is not None and my is not None:
            from win32api import GetMonitorInfo, MonitorFromPoint
            try:
                # Get the work area of the monitor containing the mouse cursor
                work = GetMonitorInfo(MonitorFromPoint((mx, my)))['Work']
                self.screen_x = work[0] # Left bound
                self.screen_y = work[1] # Top bound
                self.screen_w = work[2] # Right bound
                self.screen_h = work[3] # Bottom bound
            except Exception:
                pass

        if self.state == State.FALLING:
            self.vy = min(15.0, self.vy + 1.5)
            self.y += int(self.vy)
            if self.y >= self.screen_h - self.SPRITE_H:
                self.y = self.screen_h - self.SPRITE_H
                self.set_state(State.LANDING)

        frames = self._frames.get(self.state, [])
        if not frames:
            return

        # Advance animation frame index only after the delay ticks have passed
        delay = self._anim_delays.get(self.state, 1)
        self._tick_counter += 1
        if self._tick_counter >= delay:
            self._tick_counter = 0
            self._frame_idx += 1
            if self._frame_idx >= len(frames):
                self._frame_idx = 0
                if self.on_anim_end:
                    self.on_anim_end(self.state)

        # Slow down walking speed during weekday sleepy hours (9 PM to 4 AM)
        speed = self.WALK_SPEED
        if self.state in (State.WALK_LEFT, State.WALK_RIGHT):
            import datetime
            now = datetime.datetime.now()
            if now.weekday() < 5 and (now.hour >= 21 or now.hour < 4):
                speed = 1  # walk very slowly

        if self.state == State.WALK_LEFT:
            self.x = max(self.screen_x + self.MARGIN, self.x - speed)
        elif self.state == State.WALK_RIGHT:
            self.x = min(self.screen_w - self.SPRITE_W - self.MARGIN, self.x + speed)

    def at_edge(self):
        return (self.x <= self.screen_x + self.MARGIN or
                self.x >= self.screen_w - self.SPRITE_W - self.MARGIN)

    def snap_to_floor(self):
        self.y = self.screen_h - self.SPRITE_H

    def clamp(self):
        # Update monitor based on current self.x, self.y so dragging works across screens!
        from win32api import GetMonitorInfo, MonitorFromPoint
        try:
            work = GetMonitorInfo(MonitorFromPoint((self.x + self.SPRITE_W // 2, self.y + self.SPRITE_H // 2)))['Work']
            self.screen_x = work[0]
            self.screen_y = work[1]
            self.screen_w = work[2]
            self.screen_h = work[3]
        except Exception:
            pass
        self.x = max(self.screen_x, min(self.screen_w - self.SPRITE_W, self.x))
        self.y = max(self.screen_y, min(self.screen_h - self.SPRITE_H, self.y))
