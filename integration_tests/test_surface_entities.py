# Copyright 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
import ezdxf
import os

DXFPATH = r"D:\Source\dxftest\DXF_with_ACIS_data"
FILE = os.path.join(DXFPATH, "All_Surfaces_R2010.dxf")
DELIMITER = '\n' + '='*80 + '\n'


@pytest.mark.skipif(not os.path.exists(FILE), reason='File {} not found'.format(FILE))
def test_get_acis_data_from_surfaces():
    dwg = ezdxf.readfile(FILE)
    msp = dwg.modelspace()

    with open(os.path.join(DXFPATH, "All_Surfaces_R2010.sat"), 'wt') as f:
        for surface in msp.query('SURFACE SWEPTSURFACE REVOLVEDSURFACE LOFTEDSURFACE EXTRUDEDSURFACE'):
            f.write(DELIMITER)
            f.write(str(surface)+':')
            f.write(DELIMITER)
            f.write('\n'.join(surface.get_acis_data()))
