#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import io
import ezdxf
from ezdxf.math import Vec3
from ezdxf import bbox


def test_load_poly_face_mesh():
    doc = ezdxf.read(io.StringIO(POLYMESH))
    msp = doc.modelspace()
    poly_face_mesh = msp[0]
    assert poly_face_mesh.is_poly_face_mesh

    virtual_entities = list(poly_face_mesh.virtual_entities())
    face3d = virtual_entities[0]
    vertices = face3d.wcs_vertices()
    assert len(vertices) == 4
    assert vertices[2] == vertices[3]
    box = bbox.extents([face3d])
    assert box.extmin > Vec3(1, 1, 0)


if __name__ == '__main__':
    pytest.main([__file__])

# DXF R12, only ENTITIES section
POLYMESH = """0
SECTION
2
ENTITIES
0
POLYLINE
8
0
66
1
10
0.0
20
0.0
30
0.0
70
64
71
3
72
1
0
VERTEX
8
0
10
59416.31455091119
20
21790.91531877725
30
0.0
70
192
0
VERTEX
8
0
10
59361.25307228302
20
21813.84830555742
30
0.0
70
192
0
VERTEX
8
0
10
59380.16605928067
20
21806.95449032696
30
0.0
70
192
0
VERTEX
8
0
10
0.0
20
0.0
30
0.0
70
128
71
1
72
2
73
3
0
SEQEND
8
0
0
ENDSEC
0
EOF
"""