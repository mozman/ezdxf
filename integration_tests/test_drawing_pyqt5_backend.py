# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import pytest

qc = pytest.importorskip('PyQt5.QtCore')
from PyQt5 import QtWidgets as qw
from ezdxf.addons.drawing.pyqt import PyQtBackend

_app = None


@pytest.fixture()
def backend():
    global _app
    _app = qw.QApplication([])
    scene = qw.QGraphicsScene()
    return PyQtBackend(scene)


def test_get_text_width(backend):
    assert backend.get_text_line_width('   abc', 100) > backend.get_text_line_width('abc', 100)
