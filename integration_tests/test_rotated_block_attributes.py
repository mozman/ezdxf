# Copyright 2018, Manfred Moitzi
# License: MIT License
import os
import pytest
import ezdxf
from ezdxf.lldxf.const import versions_supported_by_new


@pytest.fixture(params=versions_supported_by_new)
def drawing(request):
    return ezdxf.new(request.param)


def create_block(dwg):
    # first create a block
    flag = dwg.blocks.new(name='FLAG')

    # add dxf entities to the block (the flag)
    # use basepoint = (x, y) to define an other basepoint than (0, 0)
    flag_symbol = [(0, 0), (0, 5), (4, 3), (0, 3)]
    flag.add_polyline2d(flag_symbol)
    flag.add_circle((0, 0), .4, dxfattribs={'color': 2})

    # define some attributes
    flag.add_attdef('NAME', (0.5, -0.5), {'height': 0.5, 'color': 3})
    flag.add_attdef('XPOS', (0.5, -1.0), {'height': 0.25, 'color': 4})
    flag.add_attdef('YPOS', (0.5, -1.5), {'height': 0.25, 'color': 4})


def insert_block(layout):
    point = (10, 12)
    values = {
        'NAME': "REFNAME",
        'XPOS': "x = %.3f" % point[0],
        'YPOS': "y = %.3f" % point[1]
    }
    scale = 1.75
    layout.add_auto_blockref('FLAG', point, values, dxfattribs={
        'xscale': scale,
        'yscale': scale,
        'layer': 'FLAGS',
        'rotation': -15
    })


def test_rotated_block(drawing, tmpdir):
    create_block(drawing)
    insert_block(drawing.modelspace())

    filename = str(tmpdir.join('rotated_block_reference_%s.dxf' % drawing.dxfversion))
    try:
        drawing.saveas(filename)
    except ezdxf.DXFError as e:
        pytest.fail("DXFError: {0} for DXF version {1}".format(str(e), drawing.dxfversion))
    assert os.path.exists(filename)
