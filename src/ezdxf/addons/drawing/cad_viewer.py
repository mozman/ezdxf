#!/usr/bin/env python3
# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import argparse
import signal
import sys
from functools import partial
from typing import Optional

from PyQt5 import QtWidgets as qw, QtCore as qc, QtGui as qg

import ezdxf
from ezdxf.addons.drawing.properties import get_layer_color, RenderContext
from ezdxf.addons.drawing.frontend import draw_layout
from ezdxf.addons.drawing.pyqt_backend import _get_x_scale, PyQtBackend, CorrespondingDXFEntity, \
    CorrespondingDXFEntityStack
from ezdxf.drawing import Drawing


class CADGraphicsView(qw.QGraphicsView):
    def __init__(self, view_buffer: float = 0.2):
        super().__init__()
        self._zoom = 1
        self._default_zoom = 1
        self._zoom_limits = (0.5, 100)
        self._view_buffer = view_buffer

        self.setTransformationAnchor(qw.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(qw.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.setDragMode(qw.QGraphicsView.ScrollHandDrag)
        self.setFrameShape(qw.QFrame.NoFrame)

        self.setRenderHints(qg.QPainter.Antialiasing | qg.QPainter.TextAntialiasing | qg.QPainter.SmoothPixmapTransform)

    def clear(self):
        pass

    def fit_to_scene(self):
        r = self.sceneRect()
        bx, by = r.width() * self._view_buffer / 2, r.height() * self._view_buffer / 2
        self.fitInView(self.sceneRect().adjusted(-bx, -by, bx, by), qc.Qt.KeepAspectRatio)
        self._default_zoom = _get_x_scale(self.transform())
        self._zoom = 1

    def _get_zoom_amount(self) -> float:
        return _get_x_scale(self.transform()) / self._default_zoom

    def wheelEvent(self, event: qg.QWheelEvent) -> None:
        # dividing by 120 gets number of notches on a typical scroll wheel. See QWheelEvent documentation
        delta_notches = event.angleDelta().y() / 120
        zoom_per_scroll_notch = 0.2
        factor = 1 + zoom_per_scroll_notch * delta_notches
        resulting_zoom = self._zoom * factor
        if resulting_zoom < self._zoom_limits[0]:
            factor = self._zoom_limits[0] / self._zoom
        elif resulting_zoom > self._zoom_limits[1]:
            factor = self._zoom_limits[1] / self._zoom
        self.scale(factor, factor)
        self._zoom *= factor


class CADGraphicsViewWithOverlay(CADGraphicsView):
    element_selected = qc.pyqtSignal(object, qc.QPointF)

    def __init__(self):
        super().__init__()
        self._current_item: Optional[qw.QGraphicsItem] = None

    def clear(self):
        super().clear()
        self._current_item = None

    def drawForeground(self, painter: qg.QPainter, rect: qc.QRectF) -> None:
        if self._current_item is not None:
            r = self._current_item.boundingRect()
            r = self._current_item.sceneTransform().mapRect(r)
            painter.fillRect(r, qg.QColor(0, 255, 0, 100))

    def mouseMoveEvent(self, event: qg.QMouseEvent) -> None:
        pos = self.mapToScene(event.pos())
        self._current_item = self.scene().itemAt(pos, qg.QTransform())
        self.element_selected.emit(self._current_item, pos)
        self.scene().invalidate(self.sceneRect(), qw.QGraphicsScene.ForegroundLayer)
        super().mouseMoveEvent(event)


class CadViewer(qw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.doc = None
        self._render_context = None
        self._visible_layers = None
        self._current_layout = None

        self.scene = qw.QGraphicsScene()

        self.view = CADGraphicsViewWithOverlay()
        self.view.setScene(self.scene)
        self.view.scale(1, -1)  # so that +y is up
        self.view.element_selected.connect(self._on_element_selected)

        self.renderer = PyQtBackend(self.scene)

        menu = self.menuBar()
        select_doc_action = qw.QAction('Select Document', self)
        select_doc_action.triggered.connect(self._select_doc)
        menu.addAction(select_doc_action)
        self.select_layout_menu = menu.addMenu('Select Layout')

        toggle_sidebar_action = qw.QAction('Toggle Sidebar', self)
        toggle_sidebar_action.triggered.connect(self._toggle_sidebar)
        menu.addAction(toggle_sidebar_action)

        toggle_join_polylines_action = qw.QAction('Toggle Join Polylines', self)
        toggle_join_polylines_action.triggered.connect(self._toggle_join_polylines)
        menu.addAction(toggle_join_polylines_action)

        self.sidebar = qw.QSplitter(qc.Qt.Vertical)
        self.layers = qw.QListWidget()
        self.layers.setStyleSheet('font-size: 12pt')
        self.layers.itemChanged.connect(self._layers_updated)
        self.sidebar.addWidget(self.layers)
        self.info = qw.QPlainTextEdit()
        self.info.setReadOnly(True)
        self.sidebar.addWidget(self.info)

        container = qw.QSplitter()
        self.setCentralWidget(container)
        container.addWidget(self.view)
        container.addWidget(self.sidebar)
        container.setCollapsible(0, False)
        container.setCollapsible(1, True)
        w = container.width()
        container.setSizes([int(3 * w / 4), int(w / 4)])

        self.setWindowTitle('CAD Viewer')
        self.resize(1600, 900)
        self.show()

    def _select_doc(self):
        path, _ = qw.QFileDialog.getOpenFileName(self, caption='Select CAD Document', filter='DXF Documents (*.dxf)')
        if path:
            self.set_document(ezdxf.readfile(path))

    def set_document(self, document: Drawing):
        self.doc = document
        self._render_context = RenderContext(document)
        self._visible_layers = None
        self._current_layout = None
        self._populate_layouts()
        self._populate_layer_list()
        self.draw_layout('Model')

    def _populate_layer_list(self):
        self.layers.blockSignals(True)
        self.layers.clear()
        for name, layer in self.doc.layers.entries.items():
            item = qw.QListWidgetItem(name)
            item.setCheckState(qc.Qt.Checked)
            item.setBackground(qg.QColor(get_layer_color(layer)))
            self.layers.addItem(item)
        self.layers.blockSignals(False)

    def _populate_layouts(self):
        self.select_layout_menu.clear()
        for layout_name in self.doc.layout_names_in_taborder():
            action = qw.QAction(layout_name, self)
            action.triggered.connect(partial(self.draw_layout, layout_name))
            self.select_layout_menu.addAction(action)

    def draw_layout(self, layout_name: str):
        print(f'drawing {layout_name}')
        self._current_layout = layout_name
        self.renderer.clear()
        self.view.clear()
        draw_layout(self.doc.layout(layout_name), self._render_context, self.renderer, self._visible_layers)
        self.view.fit_to_scene()

    def resizeEvent(self, event: qg.QResizeEvent) -> None:
        self.view.fit_to_scene()

    @qc.pyqtSlot(qw.QListWidgetItem)
    def _layers_updated(self, _item: qw.QListWidgetItem):
        self._visible_layers = set()
        for i in range(self.layers.count()):
            layer = self.layers.item(i)
            if layer.checkState() == qc.Qt.Checked:
                self._visible_layers.add(layer.text().lower())
        self.draw_layout(self._current_layout)

    @qc.pyqtSlot()
    def _toggle_sidebar(self):
        self.sidebar.setHidden(not self.sidebar.isHidden())

    @qc.pyqtSlot()
    def _toggle_join_polylines(self):
        self.renderer.draw_individual_polyline_elements = not self.renderer.draw_individual_polyline_elements
        self.draw_layout(self._current_layout)

    @qc.pyqtSlot(object, qc.QPointF)
    def _on_element_selected(self, element: Optional[qw.QGraphicsItem], mouse_pos: qc.QPointF):
        text = f'mouse position: {mouse_pos.x():.4f}, {mouse_pos.y():.4f}\n'
        if element is None:
            text += 'No element selected'
        else:
            dxf_entity = element.data(CorrespondingDXFEntity)
            if dxf_entity is None:
                text += 'No data'
            else:
                text += f'Current Entity: {dxf_entity}\nLayer: {dxf_entity.dxf.layer}\n\nDXF Attributes:\n'
                for key, value in dxf_entity.dxf.all_existing_dxf_attribs().items():
                    text += f'- {key}: {value}\n'

                dxf_entity_stack = element.data(CorrespondingDXFEntityStack)
                if dxf_entity_stack:
                    text += '\nParents:\n'
                    for entity in reversed(dxf_entity_stack):
                        text += f'- {entity}\n'

        self.info.setPlainText(text)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cad_file')
    parser.add_argument('--layout', default='Model')
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal.SIG_DFL)  # handle Ctrl+C properly
    app = qw.QApplication(sys.argv)

    v = CadViewer()
    if args.cad_file is not None:
        v.set_document(ezdxf.readfile(args.cad_file))
        try:
            v.draw_layout(args.layout)
        except KeyError:
            print(f'could not find layout "{args.layout}". Valid layouts: {[l.name for l in v.doc.layouts]}')
            sys.exit(1)
    sys.exit(app.exec_())


if __name__ == '__main__':
    _main()
