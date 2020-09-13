# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import pytest

plt = pytest.importorskip('matplotlib.pyplot')

from ezdxf.addons.drawing.matplotlib import MatplotlibBackend, _get_line_style_pattern
from ezdxf.addons.drawing.properties import Properties


@pytest.fixture()
def backend():
    fig, ax = plt.subplots()
    return MatplotlibBackend(ax)


def test_get_text_width(backend):
    assert backend.get_text_line_width('   abc',
                                       100) > backend.get_text_line_width('abc',
                                                                          100)
    assert backend.get_text_line_width('  abc ',
                                       100) == backend.get_text_line_width(
        '  abc', 100)
    assert backend.get_text_line_width('   ', 100) == 0
    assert backend.get_text_line_width('  ', 100) == 0


def test_get_line_style(backend):
    p = Properties()
    p.linetype_pattern = (1, 1)
    assert _get_line_style_pattern(p, 2) == (0, (6, 6))  # in points!
    assert _get_line_style_pattern(Properties(), 2) == 'solid'
