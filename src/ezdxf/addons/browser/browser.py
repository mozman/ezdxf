#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import sys
from PyQt5.QtWidgets import QMainWindow
from .loader import load_section_dict
from .model import DXFStructureModel
from .views import StructureTree

__all__ = ["DXFStructureBrowser"]

APP_NAME = "DXF Structure Browser"


def load_model(filename: str):
    section_dict = load_section_dict(filename)
    return DXFStructureModel(filename, section_dict)


class DXFStructureBrowser(QMainWindow):
    def __init__(self, filename: str = ""):
        super().__init__()
        self._filename = filename
        self._title = APP_NAME
        self._structure_tree = StructureTree()
        if filename:
            try:
                self.open(self._filename)
            except IOError:
                print("invalid file or file not found!")
                sys.exit(1)
            self._title += " - " + str(self._filename)

        self.setWindowTitle(self._title)
        self.setCentralWidget(self._structure_tree)
        self.resize(800, 600)

    def open(self, filename: str):
        model = load_model(filename)
        self._structure_tree.set_document(model)
