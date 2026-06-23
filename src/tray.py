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

    def start(self):
        if not _HAS_TRAY or not os.path.exists(_ICON_PATH):
            return
        img  = _PILImage.open(_ICON_PATH).resize((64, 64))
        menu = pystray.Menu(
            pystray.MenuItem('Show / Hide', self._toggle, default=True),
            pystray.MenuItem('Quit', self._quit),
        )
        self._icon = pystray.Icon('MeowMate', img, 'MeowMate', menu)
        threading.Thread(target=self._icon.run, daemon=True).start()

    def stop(self):
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass

    def _toggle(self):
        if self._visible:
            self._win.root.after(0, self._win.hide)
        else:
            self._win.root.after(0, self._win.show)
        self._visible = not self._visible

    def _quit(self):
        self._win.root.after(0, self._win.quit)
