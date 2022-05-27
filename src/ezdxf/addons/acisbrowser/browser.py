#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Dict, Iterator, Tuple, Iterable

from ezdxf.addons.xqt import (
    QtWidgets,
    QAction,
    QMessageBox,
    QFileDialog,
    QInputDialog,
    Qt,
)

import ezdxf
from ezdxf.document import Drawing
from ezdxf.entities import Body

from ezdxf.lldxf.const import DXFStructureError
from .data import AcisData, BinaryAcisData, TextAcisData
from .views import AcisTree, AcisRawView

__all__ = ["AcisStructureBrowser"]

APP_NAME = "ACIS Structure Browser"


BROWSER_WIDTH = 1024
BROWSER_HEIGHT = 768
TREE_WIDTH_FACTOR = 0.33


class AcisStructureBrowser(QtWidgets.QMainWindow):
    def __init__(
        self,
        filename: str = "",
        handle: str = "",
    ):
        super().__init__()
        self.filename = filename
        self.acis_entities: Dict[str, AcisData] = dict()
        self._acis_tree = AcisTree()
        self._raw_acis_viewer = AcisRawView()
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
        container.addWidget(self._acis_tree)
        container.addWidget(self._raw_acis_viewer)
        tree_width = int(BROWSER_WIDTH * TREE_WIDTH_FACTOR)
        table_width = BROWSER_WIDTH - tree_width
        container.setSizes([tree_width, table_width])
        container.setCollapsible(0, False)
        container.setCollapsible(1, False)
        return container

    def connect_slots(self):
        self._acis_tree.activated.connect(self.acis_entity_activated)

    # noinspection PyAttributeOutsideInit
    def setup_actions(self):

        self._open_action = self.make_action(
            "&Open DXF File...", self.open_dxf, shortcut="Ctrl+O"
        )
        self._export_entity_action = self.make_action(
            "&Export ACIS Entity...", self.export_entity, shortcut="Ctrl+E"
        )
        self._copy_entity_action = self.make_action(
            "&Copy ACIS Entity to Clipboard",
            self.copy_entity,
            shortcut="Ctrl+C",
        )
        self._quit_action = self.make_action(
            "&Quit", self.close, shortcut="Ctrl+Q"
        )
        self.close()
        self._goto_handle_action = self.make_action(
            "&Go to Handle...",
            self.ask_for_handle,
            shortcut="Ctrl+G",
            tip="Go to Entity Handle",
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
        file_menu.addAction(self._copy_entity_action)
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
        self.acis_entities = dict(get_acis_entities(doc))
        if self.acis_entities:
            values = iter(self.acis_entities.values())
            self.set_current_acis_entity(next(values))
            self.update_acis_tree(self.acis_entities.values())

    def reload_dxf(self):
        self.load_dxf(self.filename)

    def export_entity(self):
        if self._dxf_tags_table is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            caption="Export ACIS Entity",
            filter="Text Files (*.txt *.TXT)",
        )
        if path:
            pass

    def copy_entity(self):
        pass

    def update_title(self, path: str):
        self.setWindowTitle(f"{APP_NAME} - {path}")

    def acis_entity_activated(self, event):
        pass

    def get_current_acis_entity(self) -> AcisData:
        return self._current_acis_entity

    def set_current_entity_by_handle(self, handle: str):
        entity = self.acis_entities.get(handle)
        if entity:
            self.set_current_acis_entity(entity)

    def set_current_acis_entity(self, entity: AcisData):
        if entity:
            self._current_acis_entity = entity
            self.update_acis_entity_viewer(entity)

    def update_acis_entity_viewer(self, entity: AcisData):
        viewer = self._raw_acis_viewer
        viewer.clear()
        viewer.addItems(entity.lines)

    def update_acis_tree(self, entities: Iterable[AcisData]):
        viewer = self._acis_tree
        viewer.clear()
        viewer.addItems([e.name for e in entities])

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
        entity = self.acis_entities.get(handle)
        if entity:
            self.set_current_acis_entity(entity)
            return True
        return False

    def show_error_handle_not_found(self, handle: str):
        QMessageBox.critical(self, "Error", f"Handle {handle} not found!")


def load_doc(filename: str) -> Drawing:
    return ezdxf.readfile(filename)


def get_acis_entities(doc: Drawing) -> Iterator[Tuple[str, AcisData]]:
    for e in doc.entitydb.values():
        if isinstance(e, Body):
            handle = e.dxf.handle
            name = str(e)
            if e.has_binary_data:
                yield handle, BinaryAcisData(e.sab, name)
            else:
                yield handle, TextAcisData(e.sat, name)
