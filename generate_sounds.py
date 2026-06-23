"""Generate soft synthetic cat sound effects (run once).

Pure stdlib (math, struct, wave) — no external deps. All sounds are kept
intentionally quiet so the desktop pet never becomes annoying.

    python generate_sounds.py
"""
import os
import math
import wave
import struct
import random

SR = 22050  # sample rate
OUT = os.path.join(os.path.dirname(__file__), 'assets', 'sounds')


def _write(name, samples):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with wave.open(path, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = b''.join(struct.pack('<h', int(max(-1.0, min(1.0, s)) * 32767)) for s in samples)
        w.writeframes(frames)
    print(f'  wrote {name} ({len(samples)/SR:.2f}s)')


def _fade(samples, fade_ms=12):
    """Apply short fade in/out to remove clicks."""
    n = int(SR * fade_ms / 1000)
    n = min(n, len(samples) // 2)
    for i in range(n):
        g = i / n
        samples[i] *= g
        samples[-1 - i] *= g
    return samples


def meow():
    """Cute chirpy meow: pitch glide + vibrato + 2nd harmonic."""
    dur = 0.45
    n = int(SR * dur)
    out = []
    for i in range(n):
        t = i / n
        # pitch glide: rise then fall (550 -> 880 -> 480 Hz)
        if t < 0.4:
            f = 550 + (880 - 550) * (t / 0.4)
        else:
            f = 880 + (480 - 880) * ((t - 0.4) / 0.6)
        vib = 1.0 + 0.02 * math.sin(2 * math.pi * 18 * t)  # vibrato
        f *= vib
        ph = 2 * math.pi * f * (i / SR)
        s = math.sin(ph) + 0.35 * math.sin(2 * ph)
        # amplitude envelope: soft attack, gentle decay
        env = math.sin(math.pi * t) ** 0.7
        out.append(0.18 * s * env)
    _write('meow.wav', _fade(out))


def purr():
    """Low loopable rumble — AM-modulated bass."""
    dur = 0.6
    n = int(SR * dur)
    out = []
    for i in range(n):
        t = i / SR
        base = math.sin(2 * math.pi * 55 * t) + 0.4 * math.sin(2 * math.pi * 110 * t)
        am = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(2 * math.pi * 26 * t))  # purr flutter ~26Hz
        out.append(0.10 * base * am)
    # cross-fade ends so the loop is seamless
    _write('purr.wav', _fade(out, fade_ms=40))


def hiss():
    """Filtered noise burst — angry cat hiss."""
    dur = 0.5
    n = int(SR * dur)
    out = []
    prev = 0.0
    for i in range(n):
        t = i / n
        white = random.uniform(-1, 1)
        # simple low-pass to soften harshness
        prev = prev * 0.6 + white * 0.4
        env = math.sin(math.pi * t) ** 0.5
        out.append(0.14 * prev * env)
    _write('hiss.wav', _fade(out))


def eat():
    """Two soft 'nom' blips."""
    out = []
    for blip in range(2):
        dur = 0.12
        n = int(SR * dur)
        for i in range(n):
            t = i / n
            f = 180 - 40 * t
            s = math.sin(2 * math.pi * f * (i / SR))
            env = math.sin(math.pi * t)
            out.append(0.15 * s * env)
        out.extend([0.0] * int(SR * 0.06))  # gap between bites
    _write('eat.wav', _fade(out))


def chirp():
    """Quick rising trill — playful zoomies / excitement."""
    out = []
    for c in range(3):
        dur = 0.08
        n = int(SR * dur)
        base = 700 + c * 120
        for i in range(n):
            t = i / n
            f = base + 300 * t
            s = math.sin(2 * math.pi * f * (i / SR))
            env = math.sin(math.pi * t)
            out.append(0.15 * s * env)
        out.extend([0.0] * int(SR * 0.02))
    _write('chirp.wav', _fade(out))


if __name__ == '__main__':
    print('Generating soft cat SFX into assets/sounds/ ...')
    meow()
    purr()
    hiss()
    eat()
    chirp()
    print('Done.')
