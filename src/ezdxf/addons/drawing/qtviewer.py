#!/usr/bin/env python3
# Copyright (c) 2020-2021, Matthew Broadway
# License: MIT License
import math
import os
import time
from typing import Iterable, Tuple, List, Dict

from PyQt5 import QtWidgets as qw, QtCore as qc, QtGui as qg

import ezdxf
from ezdxf import recover
from ezdxf.addons import odafc
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.backend import BackendScaler
from ezdxf.addons.drawing.config import Configuration

from ezdxf.addons.drawing.properties import is_dark_color
from ezdxf.addons.drawing.pyqt import (
    _get_x_scale,
    PyQtBackend,
    CorrespondingDXFEntity,
    CorrespondingDXFParentStack,
)
from ezdxf.audit import Auditor
from ezdxf.document import Drawing
from ezdxf.entities import DXFGraphic
from ezdxf.lldxf.const import DXFStructureError


class CADGraphicsView(qw.QGraphicsView):
    def __init__(
        self,
        *,
        view_buffer: float = 0.2,
        zoom_per_scroll_notch: float = 0.2,
        loading_overlay: bool = True,
    ):
        super().__init__()
        self._zoom = 1.0
        self._default_zoom = 1.0
        self._zoom_limits = (0.5, 100)
        self._zoom_per_scroll_notch = zoom_per_scroll_notch
        self._view_buffer = view_buffer
        self._loading_overlay = loading_overlay
        self._is_loading = False

        self.setTransformationAnchor(qw.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(qw.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.setDragMode(qw.QGraphicsView.ScrollHandDrag)
        self.setFrameShape(qw.QFrame.NoFrame)
        self.setRenderHints(
            qg.QPainter.Antialiasing  # type: ignore
            | qg.QPainter.TextAntialiasing
            | qg.QPainter.SmoothPixmapTransform
        )

    def clear(self):
        pass

    def begin_loading(self):
        self._is_loading = True
        self.scene().invalidate(qc.QRectF(), qw.QGraphicsScene.AllLayers)
        qw.QApplication.processEvents()

    def end_loading(self, new_scene: qw.QGraphicsScene):
        self.setScene(new_scene)
        self._is_loading = False
        self.buffer_scene_rect()
        self.scene().invalidate(qc.QRectF(), qw.QGraphicsScene.AllLayers)

    def buffer_scene_rect(self):
        scene = self.scene()
        r = scene.sceneRect()
        bx, by = (
            r.width() * self._view_buffer / 2,
            r.height() * self._view_buffer / 2,
        )
        scene.setSceneRect(r.adjusted(-bx, -by, bx, by))

    def fit_to_scene(self):
        self.fitInView(self.sceneRect(), qc.Qt.KeepAspectRatio)
        self._default_zoom = _get_x_scale(self.transform())
        self._zoom = 1

    def _get_zoom_amount(self) -> float:
        return _get_x_scale(self.transform()) / self._default_zoom

    def wheelEvent(self, event: qg.QWheelEvent) -> None:
        # dividing by 120 gets number of notches on a typical scroll wheel.
        # See QWheelEvent documentation
        delta_notches = event.angleDelta().y() / 120
        direction = math.copysign(1, delta_notches)
        factor = (1.0 + self._zoom_per_scroll_notch * direction) ** abs(
            delta_notches
        )
        resulting_zoom = self._zoom * factor
        if resulting_zoom < self._zoom_limits[0]:
            factor = self._zoom_limits[0] / self._zoom
        elif resulting_zoom > self._zoom_limits[1]:
            factor = self._zoom_limits[1] / self._zoom
        self.scale(factor, factor)
        self._zoom *= factor

    def drawForeground(self, painter: qg.QPainter, rect: qc.QRectF) -> None:
        if self._is_loading and self._loading_overlay:
            painter.save()
            painter.fillRect(rect, qg.QColor("#aa000000"))
            painter.setWorldMatrixEnabled(False)
            r = self.viewport().rect()
            painter.setBrush(qc.Qt.NoBrush)
            painter.setPen(qc.Qt.white)
            painter.drawText(r.center(), "Loading...")
            painter.restore()


class CADGraphicsViewWithOverlay(CADGraphicsView):
    mouse_moved = qc.pyqtSignal(qc.QPointF)
    element_selected = qc.pyqtSignal(object, int)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._selected_items: List[qw.QGraphicsItem] = []
        self._selected_index = None

    def clear(self):
        super().clear()
        self._selected_items = None
        self._selected_index = None

    def begin_loading(self):
        self.clear()
        super().begin_loading()

    def drawForeground(self, painter: qg.QPainter, rect: qc.QRectF) -> None:
        super().drawForeground(painter, rect)
        if self._selected_items:
            item = self._selected_items[self._selected_index]
            r = item.sceneTransform().mapRect(item.boundingRect())
            painter.fillRect(r, qg.QColor(0, 255, 0, 100))

    def mouseMoveEvent(self, event: qg.QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        pos = self.mapToScene(event.pos())
        self.mouse_moved.emit(pos)
        selected_items = self.scene().items(pos)
        if selected_items != self._selected_items:
            self._selected_items = selected_items
            self._selected_index = 0 if self._selected_items else None
            self._emit_selected()

    def mouseReleaseEvent(self, event: qg.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        if event.button() == qc.Qt.LeftButton and self._selected_items:
            self._selected_index = (self._selected_index + 1) % len(
                self._selected_items
            )
            self._emit_selected()

    def _emit_selected(self):
        self.element_selected.emit(self._selected_items, self._selected_index)
        self.scene().invalidate(
            self.sceneRect(), qw.QGraphicsScene.ForegroundLayer
        )


class CadViewer(qw.QMainWindow):
    def __init__(self, config: Configuration = Configuration.defaults()):
        super().__init__()
        self._config = config
        self.doc = None
        self._render_context = None
        self._visible_layers = None
        self._current_layout = None
        self._reset_backend()

        self.view = CADGraphicsViewWithOverlay()
        self.view.setScene(qw.QGraphicsScene())
        self.view.scale(1, -1)  # so that +y is up
        self.view.element_selected.connect(self._on_element_selected)
        self.view.mouse_moved.connect(self._on_mouse_moved)

        menu = self.menuBar()
        select_doc_action = qw.QAction("Select Document", self)
        select_doc_action.triggered.connect(self._select_doc)
        menu.addAction(select_doc_action)
        self.select_layout_menu = menu.addMenu("Select Layout")

        toggle_sidebar_action = qw.QAction("Toggle Sidebar", self)
        toggle_sidebar_action.triggered.connect(self._toggle_sidebar)
        menu.addAction(toggle_sidebar_action)

        self.sidebar = qw.QSplitter(qc.Qt.Vertical)
        self.layers = qw.QListWidget()
        self.layers.setStyleSheet(
            "QListWidget {font-size: 12pt;} "
            "QCheckBox {font-size: 12pt; padding-left: 5px;}"
        )
        self.sidebar.addWidget(self.layers)
        info_container = qw.QWidget()
        info_layout = qw.QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        self.selected_info = qw.QPlainTextEdit()
        self.selected_info.setReadOnly(True)
        info_layout.addWidget(self.selected_info)
        self.mouse_pos = qw.QLabel()
        info_layout.addWidget(self.mouse_pos)
        info_container.setLayout(info_layout)
        self.sidebar.addWidget(info_container)

        container = qw.QSplitter()
        self.setCentralWidget(container)
        container.addWidget(self.view)
        container.addWidget(self.sidebar)
        container.setCollapsible(0, False)
        container.setCollapsible(1, True)
        w = container.width()
        container.setSizes([int(3 * w / 4), int(w / 4)])

        self.setWindowTitle("CAD Viewer")
        self.resize(1600, 900)
        self.show()

    def _reset_backend(self, scale: float = 1.0):
        backend = PyQtBackend(use_text_cache=True)
        if scale != 1.0:
            backend = BackendScaler(backend, factor=scale)  # type: ignore
        # clear caches
        self._backend = backend

    def _select_doc(self):
        path, _ = qw.QFileDialog.getOpenFileName(
            self,
            caption="Select CAD Document",
            filter="CAD Documents (*.dxf *.DXF *.dwg *.DWG)",
        )
        if path:
            try:
                if os.path.splitext(path)[1].lower() == ".dwg":
                    doc = odafc.readfile(path)
                    auditor = doc.audit()
                else:
                    try:
                        doc = ezdxf.readfile(path)
                    except ezdxf.DXFError:
                        doc, auditor = recover.readfile(path)
                    else:
                        auditor = doc.audit()
                self.set_document(doc, auditor)
            except IOError as e:
                qw.QMessageBox.critical(self, "Loading Error", str(e))
            except DXFStructureError as e:
                qw.QMessageBox.critical(
                    self,
                    "DXF Structure Error",
                    f'Invalid DXF file "{path}": {str(e)}',
                )

    def set_document(
        self,
        document: Drawing,
        auditor: Auditor,
        *,
        layout: str = "Model",
        overall_scaling_factor: float = 1.0,
    ):
        error_count = len(auditor.errors)
        if error_count > 0:
            ret = qw.QMessageBox.question(
                self,
                "Found DXF Errors",
                f'Found {error_count} errors in file "{document.filename}"\n'
                f"Load file anyway? ",
            )
            if ret == qw.QMessageBox.No:
                auditor.print_error_report(auditor.errors)
                return
        self.doc = document
        self._render_context = RenderContext(document)
        self._reset_backend(scale=overall_scaling_factor)  # clear caches
        self._visible_layers = None
        self._current_layout = None
        self._populate_layouts()
        self._populate_layer_list()
        self.draw_layout(layout)
        self.setWindowTitle("CAD Viewer - " + str(document.filename))

    def _populate_layer_list(self):
        self.layers.blockSignals(True)
        self.layers.clear()
        for layer in self._render_context.layers.values():
            name = layer.layer
            item = qw.QListWidgetItem()
            self.layers.addItem(item)
            checkbox = qw.QCheckBox(name)
            checkbox.setCheckState(
                qc.Qt.Checked if layer.is_visible else qc.Qt.Unchecked
            )
            checkbox.stateChanged.connect(self._layers_updated)
            text_color = (
                "#FFFFFF" if is_dark_color(layer.color, 0.4) else "#000000"
            )
            checkbox.setStyleSheet(
                f"color: {text_color}; background-color: {layer.color}"
            )
            self.layers.setItemWidget(item, checkbox)
        self.layers.blockSignals(False)

    def _populate_layouts(self):
        self.select_layout_menu.clear()
        for layout_name in self.doc.layout_names_in_taborder():
            action = qw.QAction(layout_name, self)
            action.triggered.connect(
                lambda: self.draw_layout(layout_name, reset_view=True)
            )
            self.select_layout_menu.addAction(action)

    def draw_layout(
        self,
        layout_name: str,
        reset_view: bool = True,
    ):
        print(f"drawing {layout_name}")
        self._current_layout = layout_name
        self.view.begin_loading()
        new_scene = qw.QGraphicsScene()
        self._backend.set_scene(new_scene)
        layout = self.doc.layout(layout_name)  # type: ignore
        self._update_render_context(layout)
        try:
            start = time.perf_counter()
            self.create_frontend().draw_layout(layout)
            duration = time.perf_counter() - start
            print(f"took {duration:.4f} seconds")
        except DXFStructureError as e:
            qw.QMessageBox.critical(
                self,
                "DXF Structure Error",
                f'Abort rendering of layout "{layout_name}": {str(e)}',
            )
        finally:
            self._backend.finalize()
        self.view.end_loading(new_scene)
        self.view.buffer_scene_rect()
        if reset_view:
            self.view.fit_to_scene()

    def create_frontend(self):
        return Frontend(
            self._render_context,
            self._backend,
            self._config,
        )

    def _update_render_context(self, layout):
        assert self._render_context
        self._render_context.set_current_layout(layout)
        # Direct modification of RenderContext.layers would be more flexible,
        # but would also expose the internals.
        if self._visible_layers is not None:
            self._render_context.set_layers_state(
                self._visible_layers, state=True
            )

    def resizeEvent(self, event: qg.QResizeEvent) -> None:
        self.view.fit_to_scene()

    def _layer_checkboxes(self) -> Iterable[Tuple[int, qw.QCheckBox]]:
        for i in range(self.layers.count()):
            item = self.layers.itemWidget(self.layers.item(i))
            yield i, item  # type: ignore

    @qc.pyqtSlot(int)
    def _layers_updated(self, item_state: qc.Qt.CheckState):
        shift_held = qw.QApplication.keyboardModifiers() & qc.Qt.ShiftModifier  # type: ignore
        if shift_held:
            for i, item in self._layer_checkboxes():
                item.blockSignals(True)
                item.setCheckState(item_state)
                item.blockSignals(False)

        self._visible_layers = set()
        for i, layer in self._layer_checkboxes():
            if layer.checkState() == qc.Qt.Checked:
                self._visible_layers.add(layer.text())
        self.draw_layout(self._current_layout, reset_view=False)  # type: ignore

    @qc.pyqtSlot()
    def _toggle_sidebar(self):
        self.sidebar.setHidden(not self.sidebar.isHidden())

    @qc.pyqtSlot(qc.QPointF)
    def _on_mouse_moved(self, mouse_pos: qc.QPointF):
        self.mouse_pos.setText(
            f"mouse position: {mouse_pos.x():.4f}, {mouse_pos.y():.4f}\n"
        )

    @qc.pyqtSlot(object, int)
    def _on_element_selected(
        self, elements: List[qw.QGraphicsItem], index: int
    ):
        if not elements:
            text = "No element selected"
        else:
            text = (
                f"Selected: {index + 1} / {len(elements)}    (click to cycle)\n"
            )
            element = elements[index]
            dxf_entity = element.data(CorrespondingDXFEntity)
            if dxf_entity is None:
                text += "No data"
            else:
                text += (
                    f"Selected Entity: {dxf_entity}\n"
                    f"Layer: {dxf_entity.dxf.layer}\n\nDXF Attributes:\n"
                )
                text += _entity_attribs_string(dxf_entity)

                dxf_parent_stack = element.data(CorrespondingDXFParentStack)
                if dxf_parent_stack:
                    text += "\nParents:\n"
                    for entity in reversed(dxf_parent_stack):
                        text += f"- {entity}\n"
                        text += _entity_attribs_string(entity, indent="    ")

        self.selected_info.setPlainText(text)


def _entity_attribs_string(dxf_entity: DXFGraphic, indent: str = "") -> str:
    text = ""
    for key, value in dxf_entity.dxf.all_existing_dxf_attribs().items():
        text += f"{indent}- {key}: {value}\n"
    return text
