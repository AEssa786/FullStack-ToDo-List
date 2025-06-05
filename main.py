import PySide6
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
import sys
import display as display

app = QApplication(sys.argv)

import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


css_path = resource_path("ToDo/styles.css")
with open(css_path, "r") as f:
    css = f.read()
app.setStyleSheet(css)

window = display.Display()

window.show()

sys.exit(app.exec())

