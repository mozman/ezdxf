#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import sys
import pathlib
from PyQt5.QtWidgets import (
    QMainWindow,
    QSplitter,
    QAction,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from ezdxf.lldxf.const import DXFStructureError
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
        self._sections: SectionDict = dict()
        self._entity_index: EntityIndex = dict()
        self._structure_tree = StructureTree()
        self._dxf_tags_table = DXFTagsTable()
        self.setup_actions()
        self.setup_menu()

        if filename:
            self.load_dxf(filename)
            self.update_title()
        else:
            self.setWindowTitle(APP_NAME)

        self.setCentralWidget(self.build_central_widget())
        self.resize(800, 600)

    def build_central_widget(self):
        container = QSplitter(Qt.Horizontal)
        container.addWidget(self._structure_tree)
        container.addWidget(self._dxf_tags_table)
        container.setCollapsible(0, False)
        container.setCollapsible(1, False)
        return container

    def setup_actions(self):
        self._open_action = QAction("&Open DXF file...", self)
        self._open_action.triggered.connect(self.open_dxf)

    def setup_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(self._open_action)

    def open_dxf(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            caption="Select DXF file",
            filter="DXF Documents (*.dxf *.DXF)",
        )
        if path:
            self.load_dxf(path)

    def load_dxf(self, path: str):
        try:
            self._load(path)
        except IOError as e:
            QMessageBox.critical(self, "Loading Error", str(e))
        except DXFStructureError as e:
            QMessageBox.critical(
                self,
                "DXF Structure Error",
                f'Invalid DXF file "{path}": {str(e)}',
            )
        self.update_title()

    def _load(self, filename: str):
        self._sections = load_section_dict(filename)
        self._filename = filename
        model = DXFStructureModel(pathlib.Path(filename).name, self._sections)
        self._structure_tree.set_structure(model)
        index = build_entity_index(self._sections)
        self.update_entity_index(index)
        header = self._sections.get("HEADER")
        if header:
            self.set_current_entity(header[0])

    def update_title(self):
        filepath = pathlib.Path(self._filename)
        self.setWindowTitle(f"{APP_NAME} - {filepath.absolute()}")

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
