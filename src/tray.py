import os
import threading

try:
    import pystray
    from PIL import Image as _PILImage
    _HAS_TRAY = True
except ImportError:
    _HAS_TRAY = False

_ICON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'assets', 'icons', 'tray_icon.png'
)


class TrayIcon:
    def __init__(self, window):
        self._win     = window
        self._icon    = None
        self._visible = True

    # All Tk work must happen on the main thread → schedule via root.after.
    def _run(self, fn, *args):
        self._win.root.after(0, lambda: fn(*args))

    def _build_menu(self):
        from src.window import TEST_ANIMATIONS

        anim_items = [
            pystray.MenuItem(label, (lambda s: lambda _i, _it: self._run(
                self._win.test_animation, s))(state))
            for label, state in TEST_ANIMATIONS
        ]
        anim_items.append(pystray.MenuItem(
            "Zoomies! 🏃", lambda _i, _it: self._run(self._win.test_zoomies)))
        anim_items.append(pystray.MenuItem(
            "Tes Pengingat 🔔", lambda _i, _it: self._run(self._win.test_reminder)))

        return pystray.Menu(
            pystray.MenuItem('Pengaturan AI ⚙️',
                             lambda _i, _it: self._run(self._win.open_settings)),
            pystray.MenuItem('Tanya Mochi 💬',
                             lambda _i, _it: self._run(self._win._ask_dialog_open)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Test Animasi 🎬', pystray.Menu(*anim_items)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Suara',
                             lambda _i, _it: self._run(self._win.toggle_sound),
                             checked=lambda _it: self._win.sound.enabled),
            pystray.MenuItem('Pengingat',
                             lambda _i, _it: self._run(self._win.toggle_reminders),
                             checked=lambda _it: self._win.reminders.enabled),
            pystray.MenuItem('Kesehatan 💪',
                             lambda _i, _it: self._run(self._win.toggle_health),
                             checked=lambda _it: self._win.health.enabled),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Show / Hide', self._toggle, default=True),
            pystray.MenuItem('Quit', self._quit),
        )

    def start(self):
        if not _HAS_TRAY or not os.path.exists(_ICON_PATH):
            return
        img = _PILImage.open(_ICON_PATH).resize((64, 64))
        self._icon = pystray.Icon('Mochi', img, 'Mochi', self._build_menu())
        threading.Thread(target=self._icon.run, daemon=True).start()

    def stop(self):
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass

    def _toggle(self, *_):
        if self._visible:
            self._win.root.after(0, self._win.hide)
        else:
            self._win.root.after(0, self._win.show)
        self._visible = not self._visible

    def _quit(self, *_):
        self._win.root.after(0, self._win.quit)
