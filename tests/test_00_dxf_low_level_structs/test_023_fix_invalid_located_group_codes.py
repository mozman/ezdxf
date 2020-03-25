from ezdxf.entities import LWPolyline
from ezdxf import options
import pytest




LWPOLYLINE = """  0
LWPOLYLINE
  5
20000
  8
Offline
 62
3 
100
AcDbEntity
100
AcDbPolyline
 70
0
 90
2
 10
1
 20
2
 10
1
 20
3
"""


def test_fix_invalid_located_acdb_entity_group_codes():
    options.fix_invalid_located_group_tags = True
    polyline = LWPolyline.from_text(LWPOLYLINE)

    print(str(polyline))
    print(f'Layer: {polyline.dxf.layer}')

    assert polyline.dxf.layer == 'Offline'
    assert polyline.dxf.color == 3


if __name__ == '__main__':
    pytest.main([__file__])

