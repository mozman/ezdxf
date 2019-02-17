import pytest

from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.entities.dxfentity import DXFTagStorage


@pytest.fixture
def entity():
    return DXFTagStorage.from_text(THE_KNOWN_UNKNOWN)


def test_default_attribs(entity):
    assert entity.dxftype() == 'MTEXT'
    assert entity.dxf.handle == '278'
    assert entity.dxf.owner == '1F'
    assert entity.base_class[0] == (0, 'MTEXT')
    assert entity.base_class[1] == (5, '278')


def test_dxf_export(entity):
    control_tags = basic_tags_from_text(THE_KNOWN_UNKNOWN)
    collector = TagCollector()
    entity.export_dxf(collector)
    result = collector.tags
    assert result == control_tags


THE_KNOWN_UNKNOWN = r"""0
MTEXT
5
278
330
1F
100
AcDbEntity
8
0
100
AcDbMText
10
2762.147
20
2327.073
30
0.0
40
2.5
41
18.851
46
0.0
71
1
72
5
1
{\fArial|b0|i0|c162|p34;CHANGE;\P\P\PTEXT}
73
1
44
1.0
101
Embedded Object
70
1
10
1.0
20
0.0
30
0.0
11
2762.147
21
2327.073
31
0.0
40
18.851
41
0.0
42
15.428
43
15.042
71
2
72
1
44
18.851
45
12.5
73
0
74
0
46
0.0
"""

if __name__ == '__main__':
    pytest.main([__file__])

