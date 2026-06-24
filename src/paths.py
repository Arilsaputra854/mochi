import sys
import os


def get_base_dir() -> str:
    """Return project root, works both in normal Python and PyInstaller frozen exe."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
