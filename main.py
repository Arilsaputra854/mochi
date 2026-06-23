import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.window import PetWindow


def main():
    app = PetWindow()
    app.run()


if __name__ == '__main__':
    main()
