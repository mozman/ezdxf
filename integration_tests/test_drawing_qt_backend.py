# Copyright (c) 2020-2021, Matthew Broadway
# License: MIT License
import pytest
import sys

pytest.importorskip("PySide6")
from ezdxf.addons.xqt import QtWidgets as qw
from ezdxf.addons.drawing.pyqt import PyQtBackend

WIN = sys.platform == "win32"
PY310 = sys.version_info[:2] == (3, 10)
_app = None


@pytest.fixture
def backend():
    global _app
    _app = qw.QApplication([])
    scene = qw.QGraphicsScene()
    return PyQtBackend(scene)


# Error Message:
# RuntimeError: Please destroy the QApplication singleton before creating a new
# QApplication instance.
#
# ezdxf "view" command works as expected!
# Works if launched in PyCharm, but not if launched by command line
# "pytest ..." ???

@pytest.mark.skipif(
    WIN and PY310,
    reason="Does not work for Win & CPython 3.10 & PySide6",
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
