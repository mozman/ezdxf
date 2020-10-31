# Copyright (c) 2018-2020 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.layouts import VirtualLayout
from ezdxf import colors
from ezdxf.lldxf.tags import Tags
from ezdxf.entities.mleader import LeaderLine
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

@pytest.fixture
def msp():
    return VirtualLayout()


# todo: real MLEADER tests
def test_generic_mleader(msp):
    mleader = msp.new_entity('MLEADER', {})
    assert mleader.dxftype() == 'MLEADER'
    assert mleader.dxf.style_handle is None


def test_synonym_multileader(msp):
    mleader = msp.new_entity('MULTILEADER', {})
    assert mleader.dxftype() == 'MULTILEADER'
    assert mleader.dxf.style_handle is None


# todo: real MLEADERSTYLE tests
def test_standard_mleader_style():
    doc = ezdxf.new('R2007')
    mleader_style = doc.mleader_styles.get('Standard')
    assert mleader_style.dxftype() == 'MLEADERSTYLE'
    assert mleader_style.dxf.content_type == 2


class TestLeaderLine:
    @pytest.fixture(scope='class')
    def tags(self):
        return Tags.from_text(LEADER_LINE_1)

    def test_parse(self, tags):
        line = LeaderLine.load(tags)
        assert len(line.vertices) == 1
        assert len(line.breaks) == 3
        assert line.index == 0
        assert line.color == colors.BY_BLOCK_RAW_VALUE

    def test_export_dxf(self, tags):
        expected = basic_tags_from_text(LEADER_LINE_1)
        line = LeaderLine.load(tags)
        collector = TagCollector()
        line.export_dxf(collector)
        assert collector.tags == expected


LEADER_LINE_1 = """304
LEADER_LINE{
 10
181.0
 20
176.0
 30
0.0
 90
0
 11
204.0
 21
159.0
 31
0.0
 12
206.0
 22
158.0
 32
0.0
 91
0
 92
-1056964608
305
}
"""