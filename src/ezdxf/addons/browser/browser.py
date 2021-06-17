#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
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
from ezdxf.lldxf.types import DXFTag, is_pointer_code
from ezdxf.lldxf.tags import Tags
from .model import (
    DXFStructureModel,
    DXFTagsModel,
    DXFTagsRole,
)
from .data import DXFDocument, get_row_from_line_number, dxfstr, EntityHistory
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
        self._current_entity: Optional[Tags] = None
        self.history = EntityHistory()
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
                print(f"Invalid line number: {line}")
            else:
                self.goto_line(line)
        if handle is not None:
            try:
                int(handle, 16)
            except ValueError:
                print(f"Given handle is not a hex value: {handle}")
            else:
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
        self._dxf_tags_table.activated.connect(self.tag_activated)

    def setup_actions(self):
        self._open_action = QAction("&Open DXF File...", self)
        self._open_action.setShortcut("Ctrl+O")
        self._open_action.triggered.connect(self.open_dxf)

        self._export_entity_action = QAction("&Export DXF Entity...", self)
        self._export_entity_action.setShortcut("Ctrl+E")
        self._export_entity_action.triggered.connect(self.export_entity)

        self._copy_entity_action = QAction(
            "&Copy DXF Entity to Clipboard", self
        )
        self._copy_entity_action.setShortcut("Ctrl+C")
        self._copy_entity_action.triggered.connect(self.copy_entity)

        self._quit_action = QAction("&Quit", self)
        self._quit_action.setShortcut("Ctrl+Q")
        self._quit_action.triggered.connect(qApp.quit)

        self._goto_handle_action = QAction("&Go to Handle...", self)
        self._goto_handle_action.setShortcut("Ctrl+G")
        self._goto_handle_action.triggered.connect(self.ask_for_handle)

        self._goto_line_action = QAction("Go to &Line...", self)
        self._goto_line_action.setShortcut("Ctrl+L")
        self._goto_line_action.triggered.connect(self.ask_for_line_number)

        self._find_text_action = QAction("Find &Text...", self)
        self._find_text_action.setShortcut("Ctrl+F")
        self._find_text_action.triggered.connect(self.find_text)

        self._goto_predecessor_entity_action = QAction(
            "&Previous Entity", self
        )
        self._goto_predecessor_entity_action.setShortcut("Ctrl+Left")
        self._goto_predecessor_entity_action.triggered.connect(
            self.goto_predecessor_entity
        )

        self._goto_next_entity_action = QAction("&Next Entity", self)
        self._goto_next_entity_action.setShortcut("Ctrl+Right")
        self._goto_next_entity_action.triggered.connect(self.goto_next_entity)

        self._entity_history_back_action = QAction("Entity History &Back", self)
        self._entity_history_back_action.setShortcut("Alt+Left")
        self._entity_history_back_action.triggered.connect(
            self.go_back_entity_history
        )

        self._entity_history_forward_action = QAction(
            "Entity History &Forward", self
        )
        self._entity_history_forward_action.setShortcut("Alt+Right")
        self._entity_history_forward_action.triggered.connect(
            self.go_forward_entity_history
        )

    def setup_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(self._open_action)
        file_menu.addSeparator()
        file_menu.addAction(self._export_entity_action)
        file_menu.addAction(self._copy_entity_action)
        file_menu.addSeparator()
        file_menu.addAction(self._quit_action)
        navigate_menu = menu.addMenu("&Navigate")
        navigate_menu.addAction(self._goto_handle_action)
        navigate_menu.addAction(self._goto_line_action)
        navigate_menu.addAction(self._find_text_action)
        navigate_menu.addSeparator()
        navigate_menu.addAction(self._goto_next_entity_action)
        navigate_menu.addAction(self._goto_predecessor_entity_action)
        navigate_menu.addSeparator()
        navigate_menu.addAction(self._entity_history_back_action)
        navigate_menu.addAction(self._entity_history_forward_action)

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
            self.history.clear()
            self.update_title()

    def _load(self, filename: str):
        self.doc.load(filename)
        model = DXFStructureModel(self.doc.filepath.name, self.doc)
        self._structure_tree.set_structure(model)
        self.view_header_section()

    def export_entity(self):
        if self._dxf_tags_table is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            caption="Export DXF Entity",
            filter="Text Files (*.txt *.TXT)",
        )
        if path:
            model = self._dxf_tags_table.model()
            tags = model.compiled_tags()
            self.export_tags(path, tags)

    def copy_entity(self):
        if self._dxf_tags_table is None:
            return
        model = self._dxf_tags_table.model()
        tags = model.compiled_tags()
        copy_dxf_to_clipboard(tags)

    def view_header_section(self):
        header = self.doc.get_header_section()
        if header:
            self.set_current_entity(header[0])

    def update_title(self):
        self.setWindowTitle(f"{APP_NAME} - {self.doc.absolute_filepath()}")

    def get_current_entity_handle(self) -> Optional[str]:
        active_entity = self.get_current_entity()
        if active_entity:
            try:
                return active_entity.get_handle()
            except ValueError:
                pass
        return None

    def get_current_entity(self) -> Optional[Tags]:
        return self._current_entity

    def set_current_entity_by_handle(self, handle: str):
        entity = self.doc.get_entity(handle)
        if entity:
            self.set_current_entity(entity)

    def set_current_entity(self, entity: Tags, select_line_number: int = None):
        if entity:
            self._current_entity = entity
            start_line_number = self.doc.get_line_number(entity)
            model = DXFTagsModel(entity, start_line_number)
            self._dxf_tags_table.setModel(model)
            if select_line_number is not None:
                row = get_row_from_line_number(
                    model.compiled_tags(), start_line_number, select_line_number
                )
                self._dxf_tags_table.selectRow(row)
                index = self._dxf_tags_table.model().index(row, 0)
                self._dxf_tags_table.scrollTo(index)

    def set_current_entity_with_history(self, entity: Tags):
        current_entity = self.get_current_entity()
        if current_entity:
            self.history.append(current_entity)
        self.set_current_entity(entity)

    def entity_activated(self, index: QModelIndex):
        tags = index.data(role=DXFTagsRole)
        if isinstance(tags, Tags):
            self.set_current_entity_with_history(tags)

    def tag_activated(self, index: QModelIndex):
        tag = index.data(role=DXFTagsRole)
        if isinstance(tag, DXFTag) and is_pointer_code(tag.code):
            entity = self.doc.get_entity(tag.value)
            self.set_current_entity_with_history(entity)

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
            self.set_current_entity(entity, number)
            return True
        return False

    def find_text(self):
        pass

    def export_tags(self, filename: str, tags: Tags):
        try:
            with open(filename, "wt", encoding="utf8") as fp:
                fp.write(dxfstr(tags))
        except IOError as e:
            QMessageBox.critical(self, "IOError", str(e))

    def goto_next_entity(self):
        if self._dxf_tags_table:
            current_entity = self.get_current_entity()
            if current_entity is not None:
                next_entity = self.doc.next_entity(current_entity)
                if next_entity is not None:
                    self.set_current_entity_with_history(next_entity)

    def goto_predecessor_entity(self):
        if self._dxf_tags_table:
            current_entity = self.get_current_entity()
            if current_entity is not None:
                prev_entity = self.doc.previous_entity(current_entity)
                if prev_entity is not None:
                    self.set_current_entity_with_history(prev_entity)

    def go_back_entity_history(self):
        entity = self.history.back()
        if entity:
            self.set_current_entity(entity)  # do not change history

    def go_forward_entity_history(self):
        entity = self.history.forward()
        if entity:
            self.set_current_entity(entity)  # do not change history


def copy_dxf_to_clipboard(tags: Tags):
    clipboard = QApplication.clipboard()
    clipboard.setText(dxfstr(tags), mode=clipboard.Clipboard)
