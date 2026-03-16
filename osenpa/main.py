import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from ui.main_window import MainWindow

if __name__ == "__main__":
    app = MainWindow()
    app.run()
