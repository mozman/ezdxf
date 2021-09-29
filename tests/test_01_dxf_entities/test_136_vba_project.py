# Copyright (c) 2018-2019 Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf.entities.dxfobj import VBAProject
from ezdxf.lldxf.tagwriter import TagCollector


def test_vba_project():
    doc = ezdxf.new("R2007")
    vba = doc.objects.new_entity("VBA_PROJECT", {})  # type: VBAProject
    assert vba.dxftype() == "VBA_PROJECT"
    assert len(vba.data) == 0

    data = (
        b"abcdefghij" * 100
    )  # 1000 bytes => 8 DXFBinaryTags() with <= 127 bytes
    assert len(data) == 1000

    vba.data = data
    collector = TagCollector()
    vba.export_data(collector)
    tags = collector.tags
    assert len(tags) == 8
    # 127 bytes encoded as 254 char string
    assert len(tags[-2].value) == 127
    assert len(tags[-1].value) == 1000 - (127 * 7)

    assert vba.data == data


VBA_PROJECT = """0
VBA_PROJECT
5
0
330
0
100
AcDbVbaProject
90
6
310
A0B0C0D0E0F0
"""


def test_load_vba_project():
    vba = VBAProject.from_text(VBA_PROJECT)
    assert len(vba.data) == 6
    assert vba.data == b"\xA0\xB0\xC0\xD0\xE0\xF0"
