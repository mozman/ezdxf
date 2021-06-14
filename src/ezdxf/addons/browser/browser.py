#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import sys
from PyQt5.QtWidgets import QMainWindow, QSplitter
from PyQt5.QtCore import Qt

from .typehints import EntityIndex, SectionDict
from .loader import load_section_dict
from .model import DXFStructureModel, DXFTagsModel, build_entity_index
from .views import StructureTree, DXFTagsTable

__all__ = ["DXFStructureBrowser"]

APP_NAME = "DXF Structure Browser"


class DXFStructureBrowser(QMainWindow):
    def __init__(self, filename: str = ""):
        super().__init__()
        self._filename: str = filename
        self._title: str = APP_NAME
        self._sections: SectionDict = dict()
        self._entity_index: EntityIndex = dict()
        self._structure_tree = StructureTree()
        self._dxf_tags_table = DXFTagsTable()

        if filename:
            try:
                self.open(self._filename)
            except IOError:
                print("invalid file or file not found!")
                sys.exit(1)
            self._title += " - " + str(self._filename)

        self.setWindowTitle(self._title)
        self.setCentralWidget(self.build_central_widget())
        self.resize(800, 600)

    def build_central_widget(self):
        container = QSplitter(Qt.Horizontal)
        container.addWidget(self._structure_tree)
        container.addWidget(self._dxf_tags_table)
        container.setCollapsible(0, False)
        container.setCollapsible(1, False)
        return container

    def open(self, filename: str):
        self._sections = load_section_dict(filename)
        model = DXFStructureModel(filename, self._sections)
        self._structure_tree.set_structure(model)
        index = build_entity_index(self._sections)
        self.update_entity_index(index)
        header = self._sections.get("HEADER")
        if header:
            self.set_current_entity(header[0])

    def set_current_entity_by_handle(self, handle: str):
        entity = self._entity_index.get(handle)
        if entity is not None:
            model = DXFTagsModel(entity)
            self._dxf_tags_table.setModel(model)

    def set_current_entity(self, entity):
        if entity is not None:
            model = DXFTagsModel(entity)
            self._dxf_tags_table.setModel(model)

    def update_entity_index(self, index: EntityIndex):
        self._entity_index = index
        self._dxf_tags_table.set_index(index)
