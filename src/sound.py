import os

try:
    import winsound
    _HAS_SOUND = True
except ImportError:
    _HAS_SOUND = False

_SOUND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'sounds')


class SoundPlayer:
    """Plays soft cat SFX via winsound (async, one sound at a time).

    Volume is baked low at generation time, so playback stays quiet. A single
    toggle mutes everything. Looping sounds (purr) keep playing until another
    sound starts or stop() is called.
    """

    def __init__(self, enabled=True):
        self.enabled = enabled and _HAS_SOUND
        self._sounds = {}
        if _HAS_SOUND:
            for name in ('meow', 'purr', 'hiss', 'eat', 'chirp'):
                path = os.path.join(_SOUND_DIR, f'{name}.wav')
                if os.path.exists(path):
                    self._sounds[name] = path

    def play(self, name, loop=False):
        if not self.enabled:
            return
        path = self._sounds.get(name)
        if not path:
            return
        flags = winsound.SND_FILENAME | winsound.SND_ASYNC
        if loop:
            flags |= winsound.SND_LOOP
        try:
            winsound.PlaySound(path, flags)
        except Exception:
            pass

    def stop(self):
        if not _HAS_SOUND:
            return
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass

    def toggle(self):
        self.enabled = not self.enabled and _HAS_SOUND
        if not self.enabled:
            self.stop()
        return self.enabled
