# Copyright 2018-2020, Manfred Moitzi
# License: MIT License
from pathlib import Path
import pytest
import ezdxf

DXF_PATH = Path(r"D:\Source\dxftest\DXF_with_ACIS_data")
SURFACES = DXF_PATH / "All_Surfaces_R2010.dxf"
DELIMITER = '\n' + '='*80 + '\n'


@pytest.mark.skipif(not SURFACES.exists(), reason='File {} not found'.format(SURFACES))
def test_get_acis_data_from_surfaces():
    dwg = ezdxf.readfile(SURFACES)
    msp = dwg.modelspace()

    with open(DXF_PATH / "All_Surfaces_R2010.sat", 'wt') as f:
        for surface in msp.query('SURFACE SWEPTSURFACE REVOLVEDSURFACE LOFTEDSURFACE EXTRUDEDSURFACE'):
            f.write(DELIMITER)
            f.write(str(surface)+':')
            f.write(DELIMITER)
            f.write('\n'.join(surface.get_acis_data()))
