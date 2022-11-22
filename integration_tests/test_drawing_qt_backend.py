# Copyright (c) 2020-2022, Matthew Broadway
# License: MIT License
import pytest
import os

pytest.importorskip("PySide6")
from ezdxf.addons.xqt import QtWidgets as qw
from ezdxf.addons.drawing.pyqt import PyQtBackend


@pytest.fixture
def backend():
    scene = qw.QGraphicsScene()
    return PyQtBackend(scene)


@pytest.mark.skipif(
    "PYCHARM_HOSTED" in os.environ,
    reason="Qt backend test doesn't work inside PyCharm",
)
def test_get_text_width(backend):
    assert backend.get_text_line_width(
        "   abc", 100
    ) > backend.get_text_line_width("abc", 100)
    assert backend.get_text_line_width(
        "  abc ", 100
    ) == backend.get_text_line_width("  abc", 100)
    assert backend.get_text_line_width("   ", 100) == 0
    assert backend.get_text_line_width("  ", 100) == 0
