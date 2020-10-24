# Copyright (c) 2018-2020 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.layouts import VirtualLayout
from ezdxf.lldxf.tags import Tags
from ezdxf.entities.mline import MLineVertex
from ezdxf.lldxf.tagwriter import TagCollector

@pytest.fixture
def msp():
    return VirtualLayout()


# todo: real MLINE tests
def test_generic_mline(msp):
    mline = msp.new_entity('MLINE', {})
    assert mline.dxftype() == 'MLINE'


# todo: real MLINESTYLE tests
def test_standard_mline_style():
    doc = ezdxf.new()
    mline_style = doc.mline_styles.get('Standard')
    assert mline_style.dxftype() == 'MLINESTYLE'

    elements = mline_style.elements
    assert len(elements) == 2
    assert elements[0].offset == 0.5
    assert elements[0].color == 256
    assert elements[0].linetype == 'BYLAYER'
    assert elements[1].offset == -0.5
    assert elements[1].color == 256
    assert elements[1].linetype == 'BYLAYER'


VTX_1 = """11
0.0
21
0.0
31
0.0
12
1.0
22
0.0
32
0.0
13
0.0
23
1.0
33
0.0
74
2
41
0.5
41
0.0
75
0
74
2
41
0.0
41
0.0
75
0
74
2
41
-0.5
41
0.0
75
0
"""


class TestMlineVertex:
    def test_load_tags(self):
        tags = Tags.from_text(VTX_1)
        vtx = MLineVertex.load(tags)
        assert vtx.start == (0, 0, 0)
        assert vtx.line_direction == (1, 0, 0)
        assert vtx.miter_direction == (0, 1, 0)
        assert len(vtx.line_params) == 3
        p1, p2, p3 = vtx.line_params
        assert p1 == (0.5, 0.0)
        assert p2 == (0.0, 0.0)
        assert p3 == (-0.5, 0.0)
        assert len(vtx.fill_params) == 3
        assert sum(len(p) for p in vtx.fill_params) == 0

    def test_new(self):
        vtx = MLineVertex.new(
            (1, 1), (1, 0), (0, 1),
            [(0.5, 0), (0, 0)],
            [tuple(), tuple()],
        )
        assert vtx.start == (1, 1, 0)
        assert vtx.line_direction == (1, 0, 0)
        assert vtx.miter_direction == (0, 1, 0)
        assert len(vtx.line_params) == 2
        p1, p2 = vtx.line_params
        assert p1 == (0.5, 0)
        assert p2 == (0, 0)
        assert len(vtx.fill_params) == 2
        assert sum(len(p) for p in vtx.fill_params) == 0

    def test_export_dxf(self):
        t = Tags.from_text(VTX_1)
        vtx = MLineVertex.load(t)
        collector = TagCollector()
        vtx.export_dxf(collector)

        tags = Tags(collector.tags)
        assert tags[0] == (11, vtx.start[0])
        assert tags[1] == (21, vtx.start[1])
        assert tags[2] == (31, vtx.start[2])

        assert tags[3] == (12, vtx.line_direction[0])
        assert tags[4] == (22, vtx.line_direction[1])
        assert tags[5] == (32, vtx.line_direction[2])

        assert tags[6] == (13, vtx.miter_direction[0])
        assert tags[7] == (23, vtx.miter_direction[1])
        assert tags[8] == (33, vtx.miter_direction[2])

        # line- and fill parameters
        assert tags[9:] == t[3:]