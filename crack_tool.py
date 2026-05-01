# -*- coding: utf-8 -*-
import sys
from PyQt6 import QtWidgets

from app.stylesheet import APP_STYLESHEET
from app.model import CrackModel
from app.view import MainView
from app.controller import CrackController

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)

    main_window = QtWidgets.QMainWindow()
    model = CrackModel()
    view = MainView()
    view.setupUi(main_window)
    controller = CrackController(view, model)

    main_window.show()
    sys.exit(app.exec())
