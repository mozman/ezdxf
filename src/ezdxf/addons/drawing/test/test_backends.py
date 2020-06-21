import pytest
from PyQt5 import QtCore as qc, QtWidgets as qw
import matplotlib.pyplot as plt

from ezdxf.addons.drawing.backend_interface import DrawingBackend
from ezdxf.addons.drawing.matplotlib_backend import MatplotlibBackend
from ezdxf.addons.drawing.pyqt_backend import PyQtBackend, _buffer_rect


def matplotlib_backend() -> MatplotlibBackend:
    fig, ax = plt.subplots()
    return MatplotlibBackend(ax)


def pyqt_backend() -> PyQtBackend:
    scene = qw.QGraphicsScene()
    return PyQtBackend(scene)


@pytest.mark.parametrize('backend', [matplotlib_backend(), pyqt_backend()])
def test_get_text_width(backend: DrawingBackend):
    assert backend.get_text_line_width('   abc', 100) > backend.get_text_line_width('abc', 100)


def test_qrect_buffer():
    assert _buffer_rect(qc.QRectF(0, 0, 10, 10), 10).size() == qc.QSizeF(20, 20)
    assert _buffer_rect(qc.QRectF(0, 0, 10, 10), 10).topLeft() == qc.QPointF(-5, -5)
    assert _buffer_rect(qc.QRectF(0, 0, 10, 10), 10).bottomRight() == qc.QPointF(15, 15)

    assert _buffer_rect(qc.QRect(0, 0, 10, 10), 10).size() == qc.QSize(20, 20)
    assert _buffer_rect(qc.QRect(0, 0, 10, 10), 10).topLeft() == qc.QPoint(-5, -5)
    # integer rect behaviour different to QRectF
    assert _buffer_rect(qc.QRect(0, 0, 10, 10), 10).bottomRight() == qc.QPoint(14, 14)
