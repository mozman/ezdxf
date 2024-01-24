#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import cast
import pytest
import ezdxf
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.entities import factory
from ezdxf.entities import ACADProxyEntity
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.math import Matrix44
from ezdxf.protocols import SupportsVirtualEntities, virtual_entities
from ezdxf.entities.copy import CopyNotSupported

@pytest.fixture(scope="module")
def proxy() -> ACADProxyEntity:
    xtags = ExtendedTags.from_text(AEC_DOOR)
    return cast(ACADProxyEntity, factory.load(xtags, ezdxf.new("R2018")))


def test_load_acad_proxy_entity(proxy):
    assert proxy.dxftype() == "ACAD_PROXY_ENTITY"
    assert proxy.proxy_graphic is not None, "expected proxy graphic data"


def test_export_exact_original_data(proxy):
    expected = basic_tags_from_text(AEC_DOOR)
    collector = TagCollector(dxfversion=ezdxf.const.DXF2013, optional=True)
    proxy.export_dxf(collector)
    assert collector.tags == expected, "expected exact same DXF tags"


EXPECTED_VIRTUAL_ENTITY_TYPES = [
    "POLYLINE",
    "POLYLINE",
    "ARC",
    "ARC",
    "POLYLINE",
    "POLYLINE",
]


def test_virtual_entities_support(proxy):
    types = [e.dxftype() for e in proxy.virtual_entities()]
    assert types == EXPECTED_VIRTUAL_ENTITY_TYPES


def test_virtual_sub_entities_source_tracking(proxy):
    result = set(e.source_of_copy for e in proxy.virtual_entities())
    assert len(result) == 1, "only one source of copy expected"
    assert proxy in result, "proxy should be the source of copy"


def test_virtual_entities_if_no_proxy_graphic_exists(proxy):
    data = proxy.proxy_graphic
    proxy.proxy_graphic = None
    assert len(list(proxy.virtual_entities())) == 0
    proxy.proxy_graphic = data


def test_supports_virtual_entities_protocol(proxy):
    assert isinstance(proxy, SupportsVirtualEntities)
    types = [e.dxftype() for e in virtual_entities(proxy)]
    assert types == EXPECTED_VIRTUAL_ENTITY_TYPES


def test_proxy_entity_is_not_transformable(proxy):
    # Transformation is only for the virtual entities possible!
    with pytest.raises(NotImplementedError):
        proxy.transform(Matrix44.translate(1, 1, 1))


def test_proxy_graphic_is_not_copyable(proxy):
    # Has to be copied as virtual entities!
    with pytest.raises(CopyNotSupported):
        proxy.copy()


AEC_DOOR = """  0
ACAD_PROXY_ENTITY
  5
59D
330
1F
100
AcDbEntity
  8
fire door - 60 mins
100
AcDbProxyEntity
 90
498
 91
518
 71
33
 97
155
 70
0
160
728
310
D80200000D0000000C00000010000000050000000C0000000E000000000100000C00000012000000FF7F0000100000002200000000000000000000000C00000010000000050000000C00000012000000000000000C0000000E000000010000006C00000007000000040000008705D40EB308C2404F852AD01EBFC340000000
310
0000000000188DCA03B308C240BF872AD01EA6C34000000000000000003988CA03B33AC240E19617BA1EA6C3400000000000000000A800D40EB33AC240719417BA1EBFC34000000000000000006C000000070000000400000043041686B408C2407A322AD01E11C7400000000000000000B27C1F91B408C2400A302AD01E2A
310
C7400000000000000000D3771F91B43AC2402C3F17BA1E2AC740000000000000000064FF1586B43AC2409C4117BA1E11C74000000000000000006400000004000000A800D40EB33AC240719417BA1EBFC34000000000000000000000000000908A4000000000000000000000000000000000010000000000F0BFD0A43C4F34
310
41DC3EADE1FCFFFFFFEF3F0000000000000000182D4454FB21F93F00000000640000000400000064FF1586B43AC2409C4117BA1E11C74000000000000000000000000000908A4000000000000000000000000000000000010000000000F03FD0A43C4F3441DCBEADE1FCFFFFFFEFBF0000000000000000182D4454FB21F93F
310
000000006C0000000700000004000000A800D40EB33AC240719417BA1EBFC3400000000000000000A36A8A18B33AC2404D9217BA1ED5C340000000000000000038418A18B3E3C340EE9276FE1DD5C34000000000000000003DD7D30EB3E3C340139576FE1DBFC34000000000000000006C000000070000000400000064FF15
310
86B43AC2409C4117BA1E11C740000000000000000069955F7CB43AC240C14317BA1EFBC6400000000000000000FE6B5F7CB4E3C340634476FE1DFBC6400000000000000000F9D51586B4E3C3403E4276FE1D11C7400000000000000000
162
626
311
9267B00330036003200330045003400450032002D0043003200360044002D0034004500300041002D0041004400370042002D003500340033004500420032003400360046003000450035007D00A80
161
1103
310
5430B80950542012A00C46E501D984612017F0E55A03D4D86811A148789E6883B87C56F0FE7FFFFFF79FC56F0FE7FFFFFF79F9A148789E6883B97D52A8000000000004138800000000000204FA000000000001810480A8000000000000092800000000000603920202A8696AA0A8205B88A82A0A82059E206A82A0A8400000
310
000002047A04A82A0A82A0
360
5A1
340
457
 94
0
1001
ACAD
1000
AcRTDxfName
1000
AEC_DOOR
1000
AcRTDxfName
1000
AEC_DOOR
1000
AcRTDxfName
1000
AEC_DOOR
"""

if __name__ == "__main__":
    pytest.main([__file__])
