# Copyright 2018 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
import os
import ezdxf


def test_complex_line_type(tmpdir):
    dwg = ezdxf.new('R2018')  # DXF R13 or later is required
    dwg.linetypes.new('GASLEITUNG2', dxfattribs={
        'description': 'Gasleitung2 ----GAS----GAS----GAS----GAS----GAS----GAS--',
        'length': 1,  # required for complex line types
        # line type definition in acadlt.lin:
        'pattern': 'A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25',
    })

    # shapes only work if the ltypeshp.shx and the DXF file are in the same directory
    dwg.linetypes.new('GRENZE2', dxfattribs={
        'description': 'Grenze eckig ----[]-----[]----[]-----[]----[]--',
        'length': 1.45,  # required for complex line types
        # line type definition in acadlt.lin:
        # A,.25,-.1,[BOX,ltypeshp.shx,x=-.1,s=.1],-.1,1
        # replacing BOX by shape index 132 (got index from an AutoCAD file), ezdxf can't get shape index from ltypeshp.shx
        'pattern': 'A,.25,-.1,[132,ltypeshp.shx,x=-.1,s=.1],-.1,1',
    })

    msp = dwg.modelspace()
    msp.add_line((0, 0), (100, 0), dxfattribs={'linetype': 'GASLEITUNG2'})
    msp.add_line((0, 50), (100, 50), dxfattribs={'linetype': 'GRENZE2'})

    filename = str(tmpdir.join('complex_line_type_%s.dxf' % dwg.dxfversion))
    try:
        dwg.saveas(filename)
    except ezdxf.DXFError as e:
        pytest.fail("DXFError: {0} for DXF version {1}".format(str(e), dwg.dxfversion))
    assert os.path.exists(filename)
