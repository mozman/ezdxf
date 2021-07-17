# Copyright 2018-2021, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf

DXF_PATH = ezdxf.options.test_files_path / "DXF_with_ACIS_data"
SURFACES = DXF_PATH / "All_Surfaces_R2010.dxf"
DELIMITER = '\n' + '=' * 80 + '\n'


@pytest.mark.skipif(not SURFACES.exists(),
                    reason=f'File {SURFACES} not found')
def test_get_acis_data_from_surfaces():
    dwg = ezdxf.readfile(SURFACES)
    msp = dwg.modelspace()

    with open(DXF_PATH / "All_Surfaces_R2010.sat", 'wt') as f:
        for surface in msp.query(
                'SURFACE SWEPTSURFACE REVOLVEDSURFACE LOFTEDSURFACE EXTRUDEDSURFACE'):
            f.write(DELIMITER)
            f.write(str(surface) + ':')
            f.write(DELIMITER)
            f.write('\n'.join(surface.acis_data))
