#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from PyQt5.QtWidgets import (
    QMainWindow,
    QSplitter,
    QAction,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QModelIndex
from ezdxf.lldxf.const import DXFStructureError
from ezdxf.lldxf.tags import Tags
from .model import (
    DXFStructureModel,
    DXFTagsModel,
    DXFTagsRole,
)
from .data import DXFDocument
from .views import StructureTree, DXFTagsTable

__all__ = ["DXFStructureBrowser"]

APP_NAME = "DXF Structure Browser"


class DXFStructureBrowser(QMainWindow):
    def __init__(self, filename: str = ""):
        super().__init__()
        self.doc = DXFDocument()
        self._structure_tree = StructureTree()
        self._dxf_tags_table = DXFTagsTable()
        self.setup_actions()
        self.setup_menu()

        if filename:
            self.load_dxf(filename)
        else:
            self.setWindowTitle(APP_NAME)

        self.setCentralWidget(self.build_central_widget())
        self.resize(800, 600)
        self.connect_slots()

    def build_central_widget(self):
        container = QSplitter(Qt.Horizontal)
        container.addWidget(self._structure_tree)
        container.addWidget(self._dxf_tags_table)
        container.setCollapsible(0, False)
        container.setCollapsible(1, False)
        return container

    def connect_slots(self):
        self._structure_tree.activated.connect(self.entity_activated)

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
        else:
            self.update_title()

    def _load(self, filename: str):
        self.doc.load(filename)
        model = DXFStructureModel(self.doc.filepath.name, self.doc)
        self._structure_tree.set_structure(model)
        self.view_header_section()

    def view_header_section(self):
        header = self.doc.get_header_section()
        if header:
            self.set_current_entity(header[0])

    def update_title(self):
        self.setWindowTitle(f"{APP_NAME} - {self.doc.absolute_filepath()}")

    def set_current_entity_by_handle(self, handle: str):
        entity = self.doc.get_entity(handle)
        if entity:
            self.set_current_entity(entity)

    def set_current_entity(self, entity: Tags):
        if entity:
            line_number = self.doc.get_line_number(entity)
            model = DXFTagsModel(entity, line_number)
            self._dxf_tags_table.setModel(model)

    def entity_activated(self, index: QModelIndex):
        tags = index.data(role=DXFTagsRole)
        if isinstance(tags, Tags):
            self.set_current_entity(tags)
