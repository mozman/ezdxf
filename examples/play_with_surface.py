from pathlib import Path
import ezdxf

DXFPATH = Path(r"D:\Source\dxftest\DXF_with_ACIS_data")
DELIMITER = '\n' + '='*80 + '\n'

doc = ezdxf.readfile(DXFPATH / "All_Surfaces_R2010.dxf")
msp = doc.modelspace()


with open(DXFPATH / "All_Surfaces_R2010.sat", 'wt') as f:
    for surface in msp.query('SURFACE SWEPTSURFACE REVOLVEDSURFACE LOFTEDSURFACE EXTRUDEDSURFACE'):
        f.write(DELIMITER)
        f.write(str(surface)+':')
        f.write(DELIMITER)
        f.write('\n'.join(surface.get_acis_data()))
