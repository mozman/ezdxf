#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import io
import ezdxf
from ezdxf.math import Vec3
from ezdxf import bbox


@pytest.fixture(scope="module")
def triangle_mesh():
    doc = ezdxf.read(io.StringIO(POLYMESH))
    msp = doc.modelspace()
    return msp[0]


@pytest.fixture
def virtual_3dface(triangle_mesh):
    virtual_entities = list(triangle_mesh.virtual_entities())
    return virtual_entities[0]


def test_is_poly_face_mesh(triangle_mesh):
    assert triangle_mesh.is_poly_face_mesh


def test_virtual_3dface_has_only_3_vertices(virtual_3dface):
    vertices = virtual_3dface.wcs_vertices()
    assert len(vertices) == 3


def test_virtual_3dface_does_not_include_NULLVEC(virtual_3dface):
    box = bbox.extents([virtual_3dface])
    assert box.extmin > Vec3(1, 1, 0)


if __name__ == "__main__":
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
