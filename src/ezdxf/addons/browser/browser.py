#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Optional, Set, List
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QAction,
    QFileDialog,
    QMessageBox,
    QInputDialog,
    qApp,
    QDialog,
)
from PyQt5.QtCore import Qt, QModelIndex, QSettings
from ezdxf.lldxf.const import DXFStructureError
from ezdxf.lldxf.types import DXFTag, is_pointer_code
from ezdxf.lldxf.tags import Tags
from ezdxf.pp.reflinks import get_reference_link

from .model import (
    DXFStructureModel,
    DXFTagsModel,
    DXFTagsRole,
)
from .data import (
    DXFDocument,
    get_row_from_line_number,
    dxfstr,
    EntityHistory,
    SearchIndex,
)
from .views import StructureTree, DXFTagsTable
from .find_dialog import Ui_FindDialog

__all__ = ["DXFStructureBrowser"]

APP_NAME = "DXF Structure Browser"
TEXT_EDITOR = os.environ.get(
    "EZDXF_TEXT_EDITOR", r"C:\Program Files\Notepad++\notepad++.exe"
)

SearchSections = Set[str]


def searchable_entities(
    doc: DXFDocument, search_sections: SearchSections
) -> List[Tags]:
    entities = []
    for name, section_entities in doc.sections.items():
        if name in search_sections:
            entities.extend(section_entities)
    return entities


class DXFStructureBrowser(QMainWindow):
    def __init__(
        self, filename: str = "", line: int = None, handle: str = None
    ):
        super().__init__()
        self.doc = DXFDocument()
        self._structure_tree = StructureTree()
        self._dxf_tags_table = DXFTagsTable()
        self._current_entity: Optional[Tags] = None
        self._active_search: Optional[SearchIndex] = None
        self._search_sections = set()
        self._find_dialog: "FindDialog" = self.create_find_dialog()
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

    # noinspection PyAttributeOutsideInit
    def setup_actions(self):
        self._open_action = self.make_action(
            "&Open DXF File...", self.open_dxf, "Ctrl+O"
        )
        self._export_entity_action = self.make_action(
            "&Export DXF Entity...", self.export_entity, "Ctrl+E"
        )
        self._copy_entity_action = self.make_action(
            "&Copy DXF Entity to Clipboard", self.copy_entity, "Ctrl+C"
        )
        self._quit_action = self.make_action("&Quit", qApp.quit, "Ctrl+Q")
        self._goto_handle_action = self.make_action(
            "&Go to Handle...", self.ask_for_handle, "Ctrl+G"
        )
        self._goto_line_action = self.make_action(
            "Go to &Line...", self.ask_for_line_number, "Ctrl+L"
        )

        self._find_text_action = self.make_action(
            "Find &Text...", self.find_text, "Ctrl+F"
        )
        self._goto_predecessor_entity_action = self.make_action(
            "&Previous Entity", self.goto_previous_entity, "Ctrl+Left"
        )

        self._goto_next_entity_action = self.make_action(
            "&Next Entity", self.goto_next_entity, "Ctrl+Right"
        )
        self._entity_history_back_action = self.make_action(
            "Entity History &Back", self.go_back_entity_history, "Alt+Left"
        )
        self._entity_history_forward_action = self.make_action(
            "Entity History &Forward",
            self.go_forward_entity_history,
            "Alt+Right",
        )
        self._open_entity_in_text_editor_action = self.make_action(
            "&Open Entity in Notepad++",
            self.open_entity_in_text_editor,
            "Ctrl+N",
        )
        self._show_entity_in_tree_view_action = self.make_action(
            "Show Entity in &TreeView",
            self.show_current_entity_in_tree_view,
            "Ctrl+T",
        )

    def make_action(self, name, slot, shortcut=None) -> QAction:
        action = QAction(name, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(slot)
        return action

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
        navigate_menu.addSeparator()
        navigate_menu.addAction(self._open_entity_in_text_editor_action)
        navigate_menu.addAction(self._show_entity_in_tree_view_action)

    def create_find_dialog(self) -> "FindDialog":
        dialog = FindDialog(self)
        dialog.setModal(True)
        dialog.find_forward_button.clicked.connect(self.find_forward)
        dialog.find_backwards_button.clicked.connect(self.find_backwards)
        dialog.find_forward_button.setShortcut("F3")
        dialog.find_backwards_button.setShortcut("F4")
        return dialog

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
            self.view_header_section()
            self.update_title()

    def _load(self, filename: str):
        self.doc.load(filename)
        model = DXFStructureModel(self.doc.filepath.name, self.doc)
        self._structure_tree.set_structure(model)

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
            self.set_current_entity_with_history(header[0])

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
            model = DXFTagsModel(
                entity, start_line_number, self.doc.handle_index
            )
            self._dxf_tags_table.setModel(model)
            if select_line_number is not None:
                row = get_row_from_line_number(
                    model.compiled_tags(), start_line_number, select_line_number
                )
                self._dxf_tags_table.selectRow(row)
                index = self._dxf_tags_table.model().index(row, 0)
                self._dxf_tags_table.scrollTo(index)

    def set_current_entity_with_history(self, entity: Tags):
        self.set_current_entity(entity)
        self.history.append(entity)

    def set_current_entity_and_row_index(self, entity: Tags, index: int):
        line = self.doc.get_line_number(entity, index)
        self.set_current_entity(entity, select_line_number=line)
        self.history.append(entity)

    def entity_activated(self, index: QModelIndex):
        tags = index.data(role=DXFTagsRole)
        if isinstance(tags, Tags):
            self.set_current_entity_with_history(tags)

    def tag_activated(self, index: QModelIndex):
        tag = index.data(role=DXFTagsRole)
        if isinstance(tag, DXFTag):
            code, value = tag
            if is_pointer_code(code):
                if not self.goto_handle(value):
                    self.show_error_handle_not_found(value)
            elif code == 0:
                self.open_web_browser(get_reference_link(value))

    def ask_for_handle(self):
        handle, ok = QInputDialog.getText(
            self,
            "Go to",
            "Go to entity handle:",
        )
        if ok:
            if not self.goto_handle(handle):
                self.show_error_handle_not_found(handle)

    def goto_handle(self, handle: str) -> bool:
        entity = self.doc.get_entity(handle)
        if entity:
            self.set_current_entity_with_history(entity)
            return True
        return False

    def show_error_handle_not_found(self, handle: str):
        QMessageBox.critical(self, "Error", f"Handle {handle} not found!")

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
        self._active_search = None
        dialog = self._find_dialog
        dialog.restore_geometry()
        dialog.show_message("F3 searches forward, F4 searches backwards")
        dialog.find_text_edit.setFocus()
        dialog.show()

    def update_search(self):
        def setup_search():
            self._search_sections = dialog.search_sections()
            entities = searchable_entities(self.doc, self._search_sections)
            self._active_search = SearchIndex(entities)

        dialog = self._find_dialog
        if self._active_search is None:
            setup_search()
            # noinspection PyUnresolvedReferences
            self._active_search.set_current_entity(self._current_entity)
        else:
            search_sections = dialog.search_sections()
            if search_sections != self._search_sections:
                setup_search()
        dialog.update_options(self._active_search)

    def find_forward(self):
        self._find(backward=False)

    def find_backwards(self):
        self._find(backward=True)

    def _find(self, backward=False):
        if self._find_dialog.isVisible():
            self.update_search()
            search = self._active_search
            if search.is_end_of_index:
                search.reset_cursor(backward=backward)

            entity, index = (
                search.find_backwards() if backward else search.find_forward()
            )

            if entity:
                self.set_current_entity_and_row_index(entity, index)
                self.show_entity_found_message(entity, index)
            else:
                if search.is_end_of_index:
                    self.show_message("Not found and end of file!")
                else:
                    self.show_message("Not found!")

    def show_message(self, msg: str):
        self._find_dialog.show_message(msg)

    def show_entity_found_message(self, entity: Tags, index: int):
        dxftype = entity.dxftype()
        if dxftype == "SECTION":
            tail = " @ {0} Section".format(entity.get_first_value(2))
        else:
            try:
                handle = entity.get_handle()
                tail = f" @ {dxftype}(#{handle})"
            except ValueError:
                tail = ""
        line = self.doc.get_line_number(entity, index)
        self.show_message(f"Found in Line: {line}{tail}")

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

    def goto_previous_entity(self):
        if self._dxf_tags_table:
            current_entity = self.get_current_entity()
            if current_entity is not None:
                prev_entity = self.doc.previous_entity(current_entity)
                if prev_entity is not None:
                    self.set_current_entity_with_history(prev_entity)

    def go_back_entity_history(self):
        entity = self.history.back()
        if entity is not None:
            self.set_current_entity(entity)  # do not change history

    def go_forward_entity_history(self):
        entity = self.history.forward()
        if entity is not None:
            self.set_current_entity(entity)  # do not change history

    def open_entity_in_text_editor(self):
        current_entity = self.get_current_entity()
        line_number = self.doc.get_line_number(current_entity)
        if self._dxf_tags_table:
            indices = self._dxf_tags_table.selectedIndexes()
            if indices:
                model = self._dxf_tags_table.model()
                row = indices[0].row()
                line_number = model.line_number(row)
        args = [
            TEXT_EDITOR,
            str(self.doc.absolute_filepath()),
            "-n" + str(line_number),
        ]
        subprocess.Popen(args)

    def open_web_browser(self, url: str):
        import webbrowser

        webbrowser.open(url)

    def show_current_entity_in_tree_view(self):
        entity = self.get_current_entity()
        if entity:
            self._structure_tree.expand_to_entity(entity)


def copy_dxf_to_clipboard(tags: Tags):
    clipboard = QApplication.clipboard()
    clipboard.setText(dxfstr(tags), mode=clipboard.Clipboard)


class FindDialog(QDialog, Ui_FindDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.close_button.clicked.connect(lambda: self.close())
        self.settings = QSettings("ezdxf", "DXFBrowser")

    def restore_geometry(self):
        geometry = self.settings.value("find.dialog.geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)

    def search_sections(self) -> SearchSections:
        sections = set()
        if self.header_check_box.isChecked():
            sections.add("HEADER")
        if self.classes_check_box.isChecked():
            sections.add("CLASSES")
        if self.tables_check_box.isChecked():
            sections.add("TABLES")
        if self.blocks_check_box.isChecked():
            sections.add("BLOCKS")
        if self.entities_check_box.isChecked():
            sections.add("ENTITIES")
        if self.objects_check_box.isChecked():
            sections.add("OBJECTS")
        return sections

    def update_options(self, search: SearchIndex) -> None:
        search.reset_search_term(self.find_text_edit.text())
        search.case_insensitive = not self.match_case_check_box.isChecked()
        search.whole_words = self.whole_words_check_box.isChecked()
        search.numbers = self.number_tags_check_box.isChecked()

    def closeEvent(self, event):
        self.settings.setValue("find.dialog.geometry", self.saveGeometry())
        super().closeEvent(event)

    def show_message(self, msg: str):
        self.message.setText(msg)
