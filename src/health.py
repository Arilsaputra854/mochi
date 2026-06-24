import time


class HealthMonitor:
    """Tracks continuous typing sessions and fires health reminders at configurable intervals."""

    # (config_key, category_id, default_minutes, message_template)
    _CHECKS = [
        ('health_eye_min',     'mata',    20,  "Udah {min} menit liat layar terus! "
                                               "Lihat titik jauh ~20 detik biar mata istirahat ya 👁️"),
        ('health_water_min',   'air',     45,  "Minum air dulu dong! "
                                               "Udah {min} menit duduk depan layar 💧"),
        ('health_move_min',    'gerak',   90,  "Berdiri dan stretch sebentar! "
                                               "Udah {min} menit duduk terus, bahaya buat pinggang 🧘"),
        ('health_posture_min', 'postur',  120, "Cek postur duduk kamu! "
                                               "Punggung tegak, bahu rileks, monitor sejajar mata 🪑"),
    ]

    def __init__(self, config=None, enabled=True):
        self.config          = config
        self.enabled         = enabled
        self._session_start  = None
        self._last_activity  = 0.0
        self._fired          = set()   # category IDs fired this session

    # ── Config helpers ────────────────────────────────────────────────────────

    def _conf(self, key, default):
        if self.config:
            v = self.config.get(key)
            return v if v is not None else default
        return default

    @property
    def _break_gap(self):
        return self._conf('health_break_gap_min', 5) * 60

    # ── Public API ────────────────────────────────────────────────────────────

    def notify_activity(self):
        """Call on every keypress or mouse click so session timing stays fresh."""
        if not self.enabled:
            return
        now = time.time()
        gap = now - self._last_activity
        if self._session_start is None or gap > self._break_gap:
            self._session_start = now
            self._fired         = set()
        self._last_activity = now

    def check(self):
        """Return (category, message) if a reminder is due, else None.
        Called each tick from the main loop."""
        if not self.enabled or self._session_start is None:
            return None
        elapsed = time.time() - self._session_start
        for key, category, default_min, template in self._CHECKS:
            threshold = self._conf(key, default_min) * 60
            if elapsed >= threshold and category not in self._fired:
                self._fired.add(category)
                minutes = int(threshold // 60)
                return (category, template.format(min=minutes))
        return None

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled

    def reset_session(self):
        """Call when user takes a real break (e.g., app hidden or forced sleep)."""
        self._session_start = None
        self._fired         = set()
