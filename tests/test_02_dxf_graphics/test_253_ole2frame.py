#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest

from ezdxf.entities import OLE2Frame
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from binascii import unhexlify


@pytest.fixture
def ole2frame():
    return OLE2Frame.from_text(BITMAP)


def test_sublass_is_loaded(ole2frame):
    assert ole2frame.acdb_ole2frame is not None


def test_dxf_type(ole2frame):
    assert ole2frame.dxftype() == "OLE2FRAME"


def test_bounding_box(ole2frame):
    bbox = ole2frame.bbox()
    assert bbox.extmin.isclose((58, 296))
    assert bbox.extmax.isclose((104, 304))


def test_export_exact_original_data(ole2frame):
    expected = basic_tags_from_text(BITMAP)
    collector = TagCollector(dxfversion="AC1015", optional=True)
    ole2frame.export_dxf(collector)
    assert collector.tags == expected, "expected exact same DXF tags"


def test_binary_data(ole2frame):
    expected = unhexlify(
        "8055A6788D2B542F4D401E9880AF920E73400000000000000000078BDDB41A3E"
        "5A401E9880AF920E73400000000000000000078BDDB41A3E5A40938EBE02EC84"
        "72400000000000000000A6788D2B542F4D40938EBE02EC847240000000000000"
    )
    assert ole2frame.binary_data() == expected


BITMAP = """  0
OLE2FRAME
  5
9A
330
1F
100
AcDbEntity
  8
0
100
AcDbOle2Frame
 70
2
  3
Picture (Device Independent Bitmap)
 10
58
 20
304
 30
0.0
 11
104
 21
296
 31
0.0
 71
3
 72
0
 73
0
 90
0
310
8055A6788D2B542F4D401E9880AF920E73400000000000000000078BDDB41A3E
310
5A401E9880AF920E73400000000000000000078BDDB41A3E5A40938EBE02EC84
310
72400000000000000000A6788D2B542F4D40938EBE02EC847240000000000000
  1
OLE
1001
ACAD
1000
OLEBEGIN
1070
70
1070
1
1070
71
1070
1
1070
40
1040
0.0
1070
41
1040
46.600623867295
1070
42
1040
8.603192098578
1070
72
1070
0
1070
3
1000

1070
90
1071
12
1070
43
1040
4.23333
1070
4
1000

1070
91
1071
12
1070
44
1040
4.23333
1000
OLEEND
"""
if __name__ == "__main__":
    pytest.main([__file__])
