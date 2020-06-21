from typing import Dict

import matplotlib.pyplot as plt
import pytest
from PyQt5 import QtCore as qc, QtWidgets as qw

from ezdxf.addons.drawing.backend_interface import DrawingBackend
from ezdxf.addons.drawing.matplotlib_backend import MatplotlibBackend
from ezdxf.addons.drawing.pyqt_backend import PyQtBackend, _buffer_rect

_app = None


@pytest.fixture()
def backends() -> Dict[str, DrawingBackend]:
    global _app
    _app = qw.QApplication([])
    scene = qw.QGraphicsScene()
    fig, ax = plt.subplots()
    return dict(
        pyqt_backend=PyQtBackend(scene),
        matplotlib_backend=MatplotlibBackend(ax)
    )


def test_get_text_width(backends):
    for name, backend in backends.items():
        assert backend.get_text_line_width('   abc', 100) > backend.get_text_line_width('abc', 100)


def test_qrect_buffer():
    assert _buffer_rect(qc.QRectF(0, 0, 10, 10), 10).size() == qc.QSizeF(20, 20)
    assert _buffer_rect(qc.QRectF(0, 0, 10, 10), 10).topLeft() == qc.QPointF(-5, -5)
    assert _buffer_rect(qc.QRectF(0, 0, 10, 10), 10).bottomRight() == qc.QPointF(15, 15)

    assert _buffer_rect(qc.QRect(0, 0, 10, 10), 10).size() == qc.QSize(20, 20)
    assert _buffer_rect(qc.QRect(0, 0, 10, 10), 10).topLeft() == qc.QPoint(-5, -5)
    # integer rect behaviour different to QRectF
    assert _buffer_rect(qc.QRect(0, 0, 10, 10), 10).bottomRight() == qc.QPoint(14, 14)
