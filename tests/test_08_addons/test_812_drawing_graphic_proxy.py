#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.addons.drawing.gfxproxy import DXFGraphicProxy
from ezdxf.entities import DXFObject, factory
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.protocols import SupportsVirtualEntities, query_virtual_entities


class TestDXFGraphicProxy:
    @pytest.fixture
    def proxy(self):
        obj = DXFObject()
        # does not support any graphical DXF attributes like layer, linetype ...
        obj.DXFTYPE = "FAKE_OBJECT"
        return DXFGraphicProxy(obj)

    def test_dxf_type(self, proxy):
        assert proxy.dxftype() == "FAKE_OBJECT"

    def test_get_dxfattribs(self, proxy):
        assert proxy.dxf.layer == "0", "expected default layer"

    def test_setting_dxfattribs_does_no_alter_wrapped_entity(self, proxy):
        proxy.dxf.layer = "TEST"
        assert proxy.dxf.layer == "TEST", "expected layer changed"
        assert (
            proxy.entity.dxf.hasattr("layer") is False
        ), "wrapped object does not support 'layer'"

    def test_copy_raises_type_error(self, proxy):
        with pytest.raises(TypeError):
            proxy.copy()

    def test_supports_virtual_entities_protocol(self, proxy):
        assert isinstance(proxy, SupportsVirtualEntities)
        assert len(query_virtual_entities(proxy)) == 0


def test_support_for_proxy_graphic_stored_in_acdb_entity():
    tag_storage = factory.load(ExtendedTags.from_text(DXF_STORAGE))
    assert tag_storage.dxftype() == "TAG_STORAGE"
    proxy = DXFGraphicProxy(tag_storage)
    # reusing data from test suite 252
    types = [e.dxftype() for e in query_virtual_entities(proxy)]
    assert types == [
        "POLYLINE",
        "POLYLINE",
        "ARC",
        "ARC",
        "POLYLINE",
        "POLYLINE",
    ]


DXF_STORAGE = """0
TAG_STORAGE
5
FEFE
100
AcDbEntity
8
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
100
AcDbTagStorage
"""

if __name__ == "__main__":
    pytest.main([__file__])
