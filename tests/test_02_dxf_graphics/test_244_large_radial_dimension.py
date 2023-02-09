# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

import pytest

import ezdxf
from ezdxf.entities.dimension import RadialDimensionLarge
from ezdxf.lldxf.const import DXF2010
from ezdxf.lldxf.tagwriter import TagCollector

ezdxf.options.preserve_proxy_graphics()


@pytest.fixture()
def dim():
    return RadialDimensionLarge.from_text(LARGE_RADIAL_DIM)


def test_load_dimension(dim):
    assert dim.dxf.defpoint == (46, 54, 0)
    assert dim.dxf.chord_point == (46, 54, 0)
    assert dim.dxf.override_center == (47, 53, 0)
    assert dim.dxf.jog_point == (49, 52, 0)
    assert dim.dxf.unknown2 == 0.0


def test_export_dimension(dim):
    tagwriter = TagCollector(dxfversion=DXF2010)
    dim.export_dxf(tagwriter)
    assert (10, 46) in tagwriter.tags
    assert (13, 46) in tagwriter.tags
    assert (14, 47) in tagwriter.tags
    assert (15, 49) in tagwriter.tags
    assert (40, 0.0) in tagwriter.tags


LARGE_RADIAL_DIM = """  0
LARGE_RADIAL_DIMENSION
5
37C
102
{ACAD_REACTORS
330
393
102
}
330
1F
100
AcDbEntity
8
0
100
AcDbDimension
280
0
2
*D15
10
46.0
20
54.0
30
0.0
11
48.0
21
53.0
31
0.0
70
169
71
5
42
3.089400503595107
73
0
74
0
75
0
3
Standard
100
AcDbRadialDimensionLarge
13
46.0
23
54.0
33
0.0
14
47.0
24
53.0
34
0.0
15
49.0
25
52.0
35
0.0
40
0.0
"""

if __name__ == "__main__":
    pytest.main([__file__])
