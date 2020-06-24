# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

import pytest
import ezdxf
from ezdxf.addons.drawing.properties import PropertyContext, Properties, compile_pattern


@pytest.fixture(scope='module')
def doc():
    d = ezdxf.new(setup=True)
    d.layers.new('Test', dxfattribs={'color': 5})  # blues: 0000ff
    msp = d.modelspace()
    msp.add_line((0, 0), (1, 0), dxfattribs={'color': 256, 'layer': 'Test'})  # bylayer
    msp.add_line((0, 0), (1, 0), dxfattribs={'color': 1, 'layer': 'Test'})  # red: ff0000
    return d


def test_load_default_ctb(doc):
    msp = doc.modelspace()
    ctx = PropertyContext(msp, 'color.ctb')
    assert bool(ctx.plot_style_table) is True
    assert ctx.plot_style_table[1].color == (255, 0, 0)


def test_new_ctb(doc):
    msp = doc.modelspace()
    ctx = PropertyContext(msp)
    assert bool(ctx.plot_style_table) is True
    assert ctx.plot_style_table[1].color == (255, 0, 0)


def test_resolve_entity_color(doc):
    msp = doc.modelspace()
    ctx = PropertyContext(msp)
    lines = msp.query('LINE')
    line1 = Properties.resolve(lines[0], ctx)
    line2 = Properties.resolve(lines[1], ctx)
    assert line1.color == '#0000ff'
    assert line2.color == '#ff0000'


def test_compile_pattern():
    assert compile_pattern(0, [0.0]) == tuple()
    assert compile_pattern(2.0, [1.25, -0.25, 0.25, -0.25]) == (1.25, 0.25, 0.25, 0.25)
    assert compile_pattern(3.5, [2.5, -0.25, 0.5, -0.25]) == (2.5, 0.25, 0.5, 0.25)
    assert compile_pattern(1.4, [1.0, -0.2, 0.0, -0.2]) == (1.0, 0.2, 0.0, 0.2)
    assert compile_pattern(0.2, [0.0, -0.2]) == (0.0, 0.2)
    assert compile_pattern(2.6, [2.0, -0.2, 0.0, -0.2, 0.0, -0.2]) == (2.0, 0.2, 0.0, 0.2, 0.0, 0.2)


#  [0.8, 0.5, -0.1, 0.0, -0.1, 0.0, -0.1]),

if __name__ == '__main__':
    pytest.main([__file__])
