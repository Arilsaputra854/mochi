import datetime


class Reminder:
    """A daily reminder that fires once per day at a fixed local time."""

    def __init__(self, hour, minute, text):
        self.hour       = hour
        self.minute     = minute
        self.text       = text
        self.last_fired = None  # date it last fired

    def is_due(self, now):
        if self.last_fired == now.date():
            return False
        return now.hour == self.hour and now.minute == self.minute


# ── Default schedule (WIB / Indonesia). Edit freely. ───────────────────────────
# Meals + solat. Times staggered so two bubbles never collide on the same minute.
DEFAULT_REMINDERS = [
    Reminder(4, 40,  "Subuh sudah masuk, yuk solat dulu 🕌"),
    Reminder(7, 0,   "Pagi! Jangan lupa sarapan ya 🍳"),
    Reminder(12, 0,  "Waktunya makan siang! 🍚"),
    Reminder(12, 15, "Sudah Dzuhur, yuk solat 🕌"),
    Reminder(15, 15, "Sudah Ashar, jangan lupa solat 🕌"),
    Reminder(18, 0,  "Maghrib tiba, yuk solat 🕌"),
    Reminder(19, 0,  "Waktunya makan malam 🍽️"),
    Reminder(19, 15, "Isya, yuk solat dulu 🕌"),
]


class ReminderManager:
    def __init__(self, reminders=None, enabled=True):
        self.reminders = reminders if reminders is not None else DEFAULT_REMINDERS
        self.enabled   = enabled

    def check(self):
        """Return the text of a due reminder (and mark it fired), else None."""
        if not self.enabled:
            return None
        now = datetime.datetime.now()
        for r in self.reminders:
            if r.is_due(now):
                r.last_fired = now.date()
                return r.text
        return None

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled
