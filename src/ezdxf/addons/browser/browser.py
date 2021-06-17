#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from PyQt5.QtWidgets import (
    QMainWindow,
    QSplitter,
    QAction,
    QFileDialog,
    QMessageBox,
    QInputDialog,
    qApp,
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
    def __init__(
        self, filename: str = "", line: int = None, handle: str = None
    ):
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
        self.resize(1024, 768)
        self.connect_slots()
        if line is not None:
            try:
                line = int(line)
            except ValueError:
                pass
            else:
                self.goto_line(line)
        if handle is not None:
            if not self.goto_handle(handle):
                print(f"Handle {handle} not found.")

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
        self._open_action = QAction("&Open DXF file ...", self)
        self._open_action.setShortcut("Ctrl+O")
        self._open_action.triggered.connect(self.open_dxf)

        self._quit_action = QAction("&Quit", self)
        self._quit_action.setShortcut("Ctrl+Q")
        self._quit_action.triggered.connect(qApp.quit)

        self._goto_handle_action = QAction("Go to &Handle ...", self)
        self._goto_handle_action.setShortcut("Ctrl+H")
        self._goto_handle_action.triggered.connect(self.ask_for_handle)

        self._goto_line_action = QAction("Go to &Line ...", self)
        self._goto_line_action.setShortcut("Ctrl+L")
        self._goto_line_action.triggered.connect(self.ask_for_line_number)

        self._find_text_action = QAction("&Find text ...", self)
        self._find_text_action.setShortcut("Ctrl+F")
        self._find_text_action.triggered.connect(self.find_text)

    def setup_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(self._open_action)
        file_menu.addAction(self._quit_action)
        navigate_menu = menu.addMenu("&Navigate")
        navigate_menu.addAction(self._goto_handle_action)
        navigate_menu.addAction(self._goto_line_action)
        navigate_menu.addAction(self._find_text_action)

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

    def ask_for_handle(self):
        handle, ok = QInputDialog.getText(
            self,
            "Go to",
            "Go to entity handle:",
        )
        if ok:
            if not self.goto_handle(handle):
                QMessageBox.information(
                    self, "Error", f"Handle {handle} not found!"
                )

    def goto_handle(self, handle: str) -> bool:
        entity = self.doc.get_entity(handle)
        if entity:
            self.set_current_entity(entity)
            return True
        return False

    def ask_for_line_number(self):
        max_line_number = self.doc.max_line_number
        number, ok = QInputDialog.getInt(
            self,
            "Go to",
            f"Go to line number: (max. {max_line_number})",
            value=1,
            min=1,
            max=max_line_number,
        )
        if ok:
            self.goto_line(number)

    def goto_line(self, number: int) -> bool:
        entity = self.doc.get_entity_at_line(int(number))
        if entity:
            self.set_current_entity(entity)
            return True
        return False

    def find_text(self):
        pass
