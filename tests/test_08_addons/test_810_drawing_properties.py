# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

import pytest
import ezdxf
from ezdxf.addons.drawing.properties import PropertyContext, Properties


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new()


def test_load_default_ctb(doc):
    msp = doc.modelspace()
    ctx = PropertyContext(msp, 'color.ctb')
    assert bool(ctx.plot_style_table) is True
    assert ctx.plot_style_table[1].color == (255, 0, 0)


def test_new_ctb(doc):
    msp = doc.modelspace()
    ctx = PropertyContext(msp, 'does_not_exist.ctb')
    assert bool(ctx.plot_style_table) is True
    assert ctx.plot_style_table[1].color == (255, 0, 0)


if __name__ == '__main__':
    pytest.main([__file__])
