# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import pytest

plt = pytest.importorskip("matplotlib.pyplot")

from ezdxf.addons.drawing.matplotlib import MatplotlibBackend


@pytest.fixture()
def backend():
    fig, ax = plt.subplots()
    return MatplotlibBackend(ax)


def test_get_text_width(backend):
    assert backend.get_text_line_width(
        "   abc", 100
    ) > backend.get_text_line_width("abc", 100)
    assert backend.get_text_line_width(
        "  abc ", 100
    ) == backend.get_text_line_width("  abc", 100)
    assert backend.get_text_line_width("   ", 100) == 0
    assert backend.get_text_line_width("  ", 100) == 0
