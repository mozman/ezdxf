# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
# mypy: ignore_errors=True
from __future__ import annotations
import os

from ezdxf.addons.xqt import QtWidgets, QtGui
from ezdxf.addons.drawing.qtviewer import CADGraphicsView
from ezdxf.addons.drawing.pyqt import PyQtPlaybackBackend
from ezdxf.addons import xplayer
from . import api

VIEWER_NAME = "HPGL/2 Viewer"


class HPGL2Widget(QtWidgets.QWidget):
    def __init__(self, view: CADGraphicsView) -> None:
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view)
        self.setLayout(layout)
        self._view = view
        self._view.closing.connect(self.close)
        self._recorder: api.Recorder | None = None
        self._reset_backend()

    def _reset_backend(self) -> None:
        self._backend = PyQtPlaybackBackend()

    @property
    def view(self) -> CADGraphicsView:
        return self._view

    def plot(self, data: bytes, reset_view: bool = True) -> None:
        self._reset_backend()
        self._recorder: api.Recorder = api.record_plotter_output(
            data, 0, 1.0, 1.0, api.MergeControl.AUTO
        )
        self._view.begin_loading()
        new_scene = QtWidgets.QGraphicsScene()
        self._backend.set_scene(new_scene)
        xplayer.hpgl2_to_drawing(self._recorder, self._backend)
        self._backend.finalize()
        self._view.end_loading(new_scene)
        self._view.buffer_scene_rect()
        if reset_view:
            self._view.fit_to_scene()


class HPGL2Viewer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._cad = HPGL2Widget(CADGraphicsView())
        self._view = self._cad.view
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        layout.addWidget(self._cad)
        sidebar = self.make_sidebar()
        layout.addWidget(sidebar)
        self.setWindowTitle(VIEWER_NAME)
        self.resize(1600, 900)
        self.show()

    def make_sidebar(self):
        sidebar = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        sidebar.setLayout(layout)

        policy = QtWidgets.QSizePolicy()
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Policy.Fixed)
        sidebar.setSizePolicy(policy)

        open_button = QtWidgets.QPushButton("Open HPGL/2 File")
        open_button.clicked.connect(self._select_plot_file)
        layout.addWidget(open_button)
        return sidebar

    def load_plot_file(self, path: str | os.PathLike) -> None:
        try:
            with open(path, "rb") as fp:
                data = fp.read()
            self.set_plot_data(data, path)
        except IOError as e:
            QtWidgets.QMessageBox.critical(self, "Loading Error", str(e))

    def _select_plot_file(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            caption="Select HPGL/2 Plot File",
            filter="Plot Files (*.plt)",
        )
        if path:
            self.load_plot_file(path)

    def set_plot_data(self, data: bytes, filename: str) -> None:
        self._cad.plot(data)
        self.setWindowTitle(f"{VIEWER_NAME} - " + str(filename))

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self._view.fit_to_scene()
