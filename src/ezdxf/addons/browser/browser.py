#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from PyQt5 import QtWidgets as qw

__all__ = ["DXFBrowser"]

APP_NAME = "DXFBrowser"


class DXFBrowser(qw.QMainWindow):
    def __init__(self, filename: str = ""):
        super().__init__()
        self._filename = filename
        self._title = APP_NAME
        self._label = qw.QLabel(" is coming soon ....")
        self.setCentralWidget(self._label)
        if filename:
            self.open(self._filename)
            self._title += " - " + str(self._filename)
        self.setWindowTitle(self._title)

    def open(self, filename: str):
        print(f"loading: {filename}")
