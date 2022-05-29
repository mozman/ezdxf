#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Iterator, Iterable
import ezdxf
from ezdxf.addons.xqt import (
    QtWidgets,
    QtGui,
    QAction,
    QMessageBox,
    QFileDialog,
    Qt,
    QModelIndex,
)
from ezdxf.document import Drawing
from ezdxf.entities import Body
from ezdxf.lldxf.const import DXFStructureError
from .data import AcisData, BinaryAcisData, TextAcisData


APP_NAME = "ACIS Structure Browser"
BROWSER_WIDTH = 1024
BROWSER_HEIGHT = 768
TREE_WIDTH_FACTOR = 0.33
FONT_FAMILY = "monospaced"


def make_font():
    font = QtGui.QFont(FONT_FAMILY)
    font.setStyleHint(QtGui.QFont.Monospace)
    return font


class AcisStructureBrowser(QtWidgets.QMainWindow):
    def __init__(
        self,
        filename: str = "",
        handle: str = "",
    ):
        super().__init__()
        self.filename = filename
        self.acis_entities: List[AcisData] = []
        self._entities_viewer = QtWidgets.QListWidget()
        self._acis_content_viewer = QtWidgets.QPlainTextEdit()
        self._acis_content_viewer.setReadOnly(True)
        self._acis_content_viewer.setLineWrapMode(
            QtWidgets.QPlainTextEdit.NoWrap
        )
        self._acis_content_viewer.setFont(make_font())
        self._current_acis_entity = AcisData()
        self.setup_actions()
        self.setup_menu()

        if filename:
            self.load_dxf(filename)
        else:
            self.setWindowTitle(APP_NAME)

        self.setCentralWidget(self.build_central_widget())
        self.resize(BROWSER_WIDTH, BROWSER_HEIGHT)
        self.connect_slots()
        if handle:
            try:
                int(handle, 16)
            except ValueError:
                print(f"Given handle is not a hex value: {handle}")
            else:
                if not self.goto_handle(handle):
                    print(f"Handle {handle} not found.")

    def build_central_widget(self):
        container = QtWidgets.QSplitter(Qt.Horizontal)
        container.addWidget(self._entities_viewer)
        container.addWidget(self._acis_content_viewer)
        tree_width = int(BROWSER_WIDTH * TREE_WIDTH_FACTOR)
        table_width = BROWSER_WIDTH - tree_width
        container.setSizes([tree_width, table_width])
        container.setCollapsible(0, False)
        container.setCollapsible(1, False)
        return container

    def connect_slots(self):
        self._entities_viewer.clicked.connect(self.acis_entity_activated)
        self._entities_viewer.activated.connect(self.acis_entity_activated)

    # noinspection PyAttributeOutsideInit
    def setup_actions(self):
        self._open_action = self.make_action(
            "&Open DXF File...", self.open_dxf, shortcut="Ctrl+O"
        )
        self._export_entity_action = self.make_action(
            "&Export ACIS Entity...", self.export_entity, shortcut="Ctrl+E"
        )
        self._quit_action = self.make_action(
            "&Quit", self.close, shortcut="Ctrl+Q"
        )
        self._reload_action = self.make_action(
            "Reload DXF File",
            self.reload_dxf,
            shortcut="Ctrl+R",
        )

    def make_action(
        self,
        name,
        slot,
        *,
        shortcut: str = "",
        tip: str = "",
    ) -> QAction:
        action = QAction(name, self)
        if shortcut:
            action.setShortcut(shortcut)
        if tip:
            action.setToolTip(tip)
        action.triggered.connect(slot)  # type: ignore
        return action

    def setup_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(self._open_action)
        file_menu.addAction(self._reload_action)
        file_menu.addSeparator()
        file_menu.addAction(self._export_entity_action)
        file_menu.addSeparator()
        file_menu.addAction(self._quit_action)

    def open_dxf(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            caption="Select DXF file",
            filter="DXF Documents (*.dxf *.DXF)",
        )
        if path:
            self.load_dxf(path)

    def load_dxf(self, path: str):
        try:
            doc = load_doc(path)
        except IOError as e:
            QMessageBox.critical(self, "Loading Error", str(e))
        except DXFStructureError as e:
            QMessageBox.critical(
                self,
                "DXF Structure Error",
                f'Invalid DXF file "{path}": {str(e)}',
            )
        else:
            self.filename = path
            self.set_acis_entities(doc)
            self.update_title(path)

    def set_acis_entities(self, doc: Drawing):
        self.acis_entities = list(get_acis_entities(doc))
        if self.acis_entities:
            self.set_current_acis_entity(self.acis_entities[0])
            self.update_acis_tree_viewer(self.acis_entities)

    def reload_dxf(self):
        try:
            index = self.acis_entities.index(self._current_acis_entity)
        except IndexError:
            index = -1
        self.load_dxf(self.filename)
        if index > 0:
            self.set_current_acis_entity(self.acis_entities[index])

    def export_entity(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            caption="Export ACIS Entity",
            filter="Text Files (*.txt *.TXT)",
        )
        if path:
            write_data(self._current_acis_entity, path)

    def update_title(self, path: str):
        self.setWindowTitle(f"{APP_NAME} - {path}")

    def acis_entity_activated(self, index: QModelIndex):
        if len(self.acis_entities) == 0:
            return
        try:
            self.set_current_acis_entity(self.acis_entities[index.row()])
        except IndexError:
            self.set_current_acis_entity(self.acis_entities[0])

    def get_current_acis_entity(self) -> AcisData:
        return self._current_acis_entity

    def set_current_acis_entity(self, entity: AcisData):
        if entity:
            self._current_acis_entity = entity
            self.update_acis_entity_viewer(entity)

    def update_acis_entity_viewer(self, entity: AcisData):
        viewer = self._acis_content_viewer
        viewer.clear()
        viewer.setPlainText("\n".join(entity.lines))

    def update_acis_tree_viewer(self, entities: Iterable[AcisData]):
        viewer = self._entities_viewer
        viewer.clear()
        viewer.addItems([e.name for e in entities])

    def goto_handle(self, handle: str) -> bool:
        for entity in self.acis_entities:
            if entity.handle == handle:
                self.set_current_acis_entity(entity)
                return True
        return False

    def show_error_handle_not_found(self, handle: str):
        QMessageBox.critical(self, "Error", f"Handle {handle} not found!")


def load_doc(filename: str) -> Drawing:
    return ezdxf.readfile(filename)


def get_acis_entities(doc: Drawing) -> Iterator[AcisData]:
    for e in doc.entitydb.values():
        if isinstance(e, Body):
            handle = e.dxf.handle
            name = str(e)
            if e.has_binary_data:
                yield BinaryAcisData(e.sab, name, handle)
            else:
                yield TextAcisData(e.sat, name, handle)


def write_data(entity: AcisData, path: str):
    try:
        with open(path, "wt") as fp:
            fp.write("\n".join(entity.lines))
    except IOError:
        pass
