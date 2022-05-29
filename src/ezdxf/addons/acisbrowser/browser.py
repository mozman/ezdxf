#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Iterator, Iterable, Optional
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
SELECTOR_WIDTH_FACTOR = 0.20
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
        self.doc: Optional[Drawing] = None
        self.acis_entities: List[AcisData] = []
        self.entities_viewer = QtWidgets.QListWidget()
        self.acis_content_viewer = QtWidgets.QPlainTextEdit()
        self.acis_content_viewer.setReadOnly(True)
        self.acis_content_viewer.setLineWrapMode(
            QtWidgets.QPlainTextEdit.NoWrap
        )
        self.acis_content_viewer.setFont(make_font())
        self.current_acis_entity = AcisData()
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
        container.addWidget(self.entities_viewer)
        container.addWidget(self.acis_content_viewer)
        selector_width = int(BROWSER_WIDTH * SELECTOR_WIDTH_FACTOR)
        entity_view_width = BROWSER_WIDTH - selector_width
        container.setSizes([selector_width, entity_view_width])
        container.setCollapsible(0, False)
        container.setCollapsible(1, False)
        return container

    def connect_slots(self):
        self.entities_viewer.clicked.connect(self.acis_entity_activated)
        self.entities_viewer.activated.connect(self.acis_entity_activated)

    # noinspection PyAttributeOutsideInit
    def setup_actions(self):
        self._open_action = self.make_action(
            "&Open DXF File...", self.open_dxf, shortcut="Ctrl+O"
        )
        self._reload_action = self.make_action(
            "Reload DXF File",
            self.reload_dxf,
            shortcut="Ctrl+R",
        )
        self._export_entity_action = self.make_action(
            "&Export Current Entity View...",
            self.export_entity,
            shortcut="Ctrl+E",
        )
        self._export_raw_data_action = self.make_action(
            "&Export Raw SAT/SAB Data...",
            self.export_raw_entity,
            shortcut="Ctrl+W",
        )
        self._quit_action = self.make_action(
            "&Quit", self.close, shortcut="Ctrl+Q"
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
        file_menu.addAction(self._export_raw_data_action)
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
            doc = ezdxf.readfile(path)
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
            self.doc = doc
            self.set_acis_entities(doc)
            self.update_title(path)

    def set_acis_entities(self, doc: Drawing):
        self.acis_entities = list(get_acis_entities(doc))
        if self.acis_entities:
            self.set_current_acis_entity(self.acis_entities[0])
            self.update_entities_viewer(self.acis_entities)

    def reload_dxf(self):
        try:
            index = self.acis_entities.index(self.current_acis_entity)
        except IndexError:
            index = -1
        self.load_dxf(self.filename)
        if index > 0:
            self.set_current_acis_entity(self.acis_entities[index])

    def export_entity(self):
        dxf_entity = self.get_current_dxf_entity()
        if dxf_entity is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,  # type: ignore
            caption="Export Current Entity View",
            dir=f"{dxf_entity.dxftype()}-{dxf_entity.dxf.handle}.txt",
            filter="Text Files (*.txt *.TXT)",
        )
        if path:
            write_data(self.current_acis_entity, path)

    def export_raw_entity(self):
        dxf_entity = self.get_current_dxf_entity()
        if dxf_entity is None:
            return
        filename = f"{dxf_entity.dxftype()}-{dxf_entity.dxf.handle}"
        sab = dxf_entity.has_binary_data
        if sab:
            filter_ = "Standard ACIS Binary Files (*.sab *.SAB)"
            filename += ".sab"
        else:
            filter_ = "Standard ACIS Text Files (*.sat *.SAT)"
            filename += ".sat"

        path, _ = QFileDialog.getSaveFileName(
            self,  # type: ignore
            caption="Export ACIS Raw Data",
            dir=filename,
            filter=filter_,
        )
        if path:
            if sab:
                with open(path, "wb") as fp:
                    fp.write(dxf_entity.sab)
            else:
                with open(path, "wt") as fp:
                    fp.write("\n".join(dxf_entity.sat))

    def get_current_dxf_entity(self) -> Optional[Body]:
        current = self.current_acis_entity
        if not current.handle or self.doc is None:
            return None
        return self.doc.entitydb.get(current.handle)  # type: ignore

    def update_title(self, path: str):
        self.setWindowTitle(f"{APP_NAME} - {path}")

    def acis_entity_activated(self, index: QModelIndex):
        if len(self.acis_entities) == 0:
            return
        try:
            self.set_current_acis_entity(self.acis_entities[index.row()])
        except IndexError:
            self.set_current_acis_entity(self.acis_entities[0])

    def set_current_acis_entity(self, entity: AcisData):
        if entity:
            self.current_acis_entity = entity
            self.update_acis_content_viewer(entity)

    def update_acis_content_viewer(self, entity: AcisData):
        viewer = self.acis_content_viewer
        viewer.clear()
        viewer.setPlainText("\n".join(entity.lines))

    def update_entities_viewer(self, entities: Iterable[AcisData]):
        viewer = self.entities_viewer
        viewer.clear()
        viewer.addItems([e.name for e in entities])

    def goto_handle(self, handle: str) -> bool:
        for entity in self.acis_entities:
            if entity.handle == handle:
                self.set_current_acis_entity(entity)
                return True
        return False


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
