# This Python file uses the following encoding: utf-8
import sys
from PyQt5 import QtWidgets, QtCore, uic

ui = os.path.join(os.path.dirname(__file__), 'UI/MainWindow.ui')
Ui_MainWindow, QtBaseClass = uic.loadUiType(ui)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # ...
    sys.exit(app.exec_())
