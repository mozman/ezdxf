# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import pytest

qc = pytest.importorskip('PyQt5.QtCore')
from PyQt5 import QtWidgets as qw
from ezdxf.addons.drawing.pyqt_backend import PyQtBackend, _buffer_rect

_app = None


@pytest.fixture()
def backend():
    global _app
    _app = qw.QApplication([])
    scene = qw.QGraphicsScene()
    return PyQtBackend(scene)


def test_get_text_width(backend):
    assert backend.get_text_line_width('   abc', 100) > backend.get_text_line_width('abc', 100)


def test_qrect_buffer():
    assert _buffer_rect(qc.QRectF(0, 0, 10, 10), 10).size() == qc.QSizeF(20, 20)
    assert _buffer_rect(qc.QRectF(0, 0, 10, 10), 10).topLeft() == qc.QPointF(-5, -5)
    assert _buffer_rect(qc.QRectF(0, 0, 10, 10), 10).bottomRight() == qc.QPointF(15, 15)

    assert _buffer_rect(qc.QRect(0, 0, 10, 10), 10).size() == qc.QSize(20, 20)
    assert _buffer_rect(qc.QRect(0, 0, 10, 10), 10).topLeft() == qc.QPoint(-5, -5)
    # integer rect behaviour different to QRectF
    assert _buffer_rect(qc.QRect(0, 0, 10, 10), 10).bottomRight() == qc.QPoint(14, 14)
