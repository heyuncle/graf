import sys
import main_window
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icons/graf.png'))
    window = main_window.MainWindow()
    app.exec_()