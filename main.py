import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env if present (keeps API key out of code and git history)
_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(_env):
    with open(_env) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _k, _v = _line.split('=', 1)
                os.environ.setdefault(_k.strip(), _v.strip())

from src.window import PetWindow


def main():
    app = PetWindow()
    app.run()


if __name__ == '__main__':
    main()
