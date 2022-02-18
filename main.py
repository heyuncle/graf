import sys
import main_window
from PyQt5.QtWidgets import *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = main_window.MainWindow()
    app.exec_()