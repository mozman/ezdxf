#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import sys
from PyQt5 import QtWidgets as qw
from PyQt5.QtCore import QModelIndex
from .loader import load_section_dict
from .model import DXFStructureModel
__all__ = ["DXFStructureBrowser"]

APP_NAME = "DXF Structure Browser"


class DXFStructureBrowser(qw.QMainWindow):
    def __init__(self, filename: str = ""):
        super().__init__()
        self._filename = filename
        self._title = APP_NAME
        self._tree_view = qw.QTreeView()
        if filename:
            try:
                self.open(self._filename)
            except IOError:
                print("invalid file or file not found!")
                sys.exit(1)
            self._title += " - " + str(self._filename)

        self.setWindowTitle(self._title)
        self.setCentralWidget(self._tree_view)
        self.resize(800, 600)

    def open(self, filename: str):
        section_dict = load_section_dict(filename)
        model = DXFStructureModel(filename, section_dict)
        self._tree_view.setModel(model)
        model.index(0, 0, QModelIndex())
        self._tree_view.expand(model.index(0, 0, QModelIndex()))
        self._tree_view.setHeaderHidden(True)
