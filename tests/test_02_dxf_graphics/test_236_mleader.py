# Copyright (c) 2018-2020 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.layouts import VirtualLayout
from ezdxf import colors
from ezdxf.lldxf import const
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.math import Matrix44

# noinspection PyProtectedMember
from ezdxf.entities.mleader import (
    LeaderLine,
    Leader,
    compile_context_tags,
    MultiLeaderContext,
    MultiLeader,
    BlockData,
)
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text


@pytest.fixture
def msp():
    return VirtualLayout()


# todo: real MLEADER tests
def test_generic_mleader(msp):
    mleader = msp.new_entity("MLEADER", {})
    assert mleader.dxftype() == "MLEADER"
    assert mleader.dxf.style_handle is None


def test_synonym_multileader(msp):
    mleader = msp.new_entity("MULTILEADER", {})
    assert mleader.dxftype() == "MULTILEADER"
    assert mleader.dxf.style_handle is None


# todo: real MLEADERSTYLE tests
def test_standard_mleader_style():
    doc = ezdxf.new("R2007")
    mleader_style = doc.mleader_styles.get("Standard")
    assert mleader_style.dxftype() == "MLEADERSTYLE"
    assert mleader_style.dxf.content_type == 2


class TestLeaderLine:
    @pytest.fixture(scope="class")
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


class TestLeader:
    @pytest.fixture(scope="class")
    def tags(self):
        return Tags.from_text(LEADER_1)

    def test_parse(self, tags):
        ctx = compile_context_tags(tags, 303)
        leader = Leader.load(ctx)
        assert len(leader.lines) == 1
        assert leader.has_last_leader_line == 1
        assert leader.has_dogleg_vector == 1
        assert leader.last_leader_point == (213.9, 199.1, 0)
        assert leader.dogleg_vector == (1, 0, 0)
        assert len(leader.breaks) == 2
        assert leader.dogleg_length == 8.0
        assert leader.index == 0

    def test_export_dxf(self, tags):
        expected = basic_tags_from_text(LEADER_1)
        ctx = compile_context_tags(tags, 303)
        leader = Leader.load(ctx)
        collector = TagCollector()
        leader.export_dxf(collector)
        assert collector.tags == expected


LEADER_1 = """302
LEADER{
290
1
291
1
10
213.9
20
199.1
30
0.0
11
1.0
21
0.0
31
0.0
12
215.2
22
199.1
32
0.0
13
219.0
23
199.1
33
0.0
90
0
40
8.0
304
LEADER_LINE{
10
195.8
20
176.1
30
0.0
91
0
92
-1056964608
305
}
271
0
303
}
"""


class MLeaderTesting:
    @pytest.fixture(scope="class")
    def tags(self, text):
        tags = Tags.from_text(text)
        return MultiLeader.extract_context_data(tags)

    @pytest.fixture(scope="class")
    def ctx(self, tags):
        return MultiLeaderContext.load(compile_context_tags(tags, 301))

    @pytest.fixture(scope="class")
    def mleader(self, text):
        return MultiLeader.load(ExtendedTags.from_text(text))

    def test_context_attribs_definition(self, ctx):
        for name in ctx.ATTRIBS.values():
            assert hasattr(ctx, name) is True

    def test_mleader_export_dxf(self, text, mleader):
        expected = basic_tags_from_text(text)
        collector = TagCollector(dxfversion=const.DXF2010)
        mleader.export_dxf(collector)
        assert collector.tags == expected


class TestMTextContext(MLeaderTesting):
    @pytest.fixture(scope="class")
    def text(self):
        return MTEXT_MLEADER_R2010

    def test_mtext_data_attribs_definition(self, ctx):
        mtext = ctx.mtext
        for name in mtext.ATTRIBS.values():
            assert hasattr(mtext, name) is True

    def test_load_mtext_context(self, ctx):
        # Leader() class is tested in TestLeader():
        assert len(ctx.leaders) == 2
        assert ctx.scale == 1
        assert ctx.base_point == (187.4, 185, 0)
        assert ctx.text_height == 5
        assert ctx.arrowhead_size == 3
        assert ctx.landing_gap_size == 2.5
        assert ctx.left_attachment == 1
        assert ctx.right_attachment == 1
        assert ctx.attachment_type == 0
        assert ctx.mtext is not None  # see test_mtext_data()
        assert ctx.block is None
        assert ctx.plane_origin == (1, 2, 3)
        assert ctx.plane_x_axis == (0, 1, 0)
        assert ctx.plane_y_axis == (1, 0, 0)
        assert ctx.plane_normal_reversed == 1
        assert ctx.top_attachment == 8
        assert ctx.bottom_attachment == 8

    def test_mtext_data(self, ctx):
        mtext = ctx.mtext
        assert mtext.default_content == "MTEXT-DATA-CONTENT"
        assert mtext.extrusion == (1, 0, 0)
        assert mtext.style_handle == "FEFE"  # handle of TextStyle() table entry
        assert mtext.insert == (236.6, 187.0, 0)
        assert mtext.text_direction == (0, 1, 0)
        assert mtext.rotation == 0.2  # in radians!
        assert mtext.rect_width == 104.6
        assert mtext.line_spacing_factor == 1.5
        assert mtext.line_spacing_style == 1
        assert mtext.color == colors.BY_BLOCK_RAW_VALUE
        assert mtext.alignment == 3
        assert mtext.flow_direction == 1
        assert mtext.bg_color == -939524096  # use window background color?
        assert mtext.bg_scale_factor == 2
        assert mtext.bg_transparency == 0
        assert mtext.has_bg_color == 0
        assert mtext.has_bg_fill == 0
        assert mtext.column_type == 0
        assert mtext.use_auto_height == 0
        assert mtext.column_width == 0.0
        assert mtext.column_gutter_width == 0.0
        assert mtext.column_flow_reversed == 0
        assert len(mtext.column_sizes) == 0
        assert mtext.use_word_break == 0


MTEXT_MLEADER_R2010 = """0
MULTILEADER
5
98
330
1F
100
AcDbEntity
8
0
100
AcDbMLeader
270
2
300
CONTEXT_DATA{
40
1.0
10
187.4
20
185.0
30
0.0
41
5.0
140
3.0
145
2.5
174
1
175
1
176
2
177
0
290
1
304
MTEXT-DATA-CONTENT
11
1.0
21
0.0
31
0.0
340
FEFE
12
236.6
22
187.0
32
0.0
13
0.0
23
1.0
33
0.0
42
0.2
43
104.6
44
0.0
45
1.5
170
1
90
-1056964608
171
3
172
1
91
-939524096
141
2.0
92
0
291
0
292
0
173
0
293
0
142
0.0
143
0.0
294
0
295
0
296
0
110
1.0
120
2.0
130
3.0
111
0.0
121
1.0
131
0.0
112
1.0
122
0.0
132
0.0
297
1
302
LEADER{
290
1
291
1
10
246.6
20
185.0
30
0.0
11
-1.0
21
0.0
31
0.0
90
0
40
8.0
304
LEADER_LINE{
10
287.3
20
220.5
30
0.0
91
0
92
-1056964608
305
}
271
0
303
}
302
LEADER{
290
1
291
1
10
179.4
20
185.0
30
0.0
11
1.0
21
0.0
31
0.0
90
1
40
8.0
304
LEADER_LINE{
10
146.5
20
149.0
30
0.0
91
1
92
-1056964608
305
}
271
0
303
}
272
8
273
8
301
}
340
6D
90
330752
170
1
91
-1056964608
341
14
171
-2
290
1
291
1
41
8.0
42
4.0
172
2
343
11
173
1
95
1
174
1
175
0
92
-1056964608
292
0
93
-1056964608
10
1.0
20
1.0
30
1.0
43
0.0
176
0
293
0
294
0
178
0
179
1
45
1.0
271
0
272
9
273
9
"""


class TestBlockContext(MLeaderTesting):
    @pytest.fixture(scope="class")
    def text(self):
        return BLOCK_MLEADER_R2010

    def test_block_data_attribs_definition(self, ctx):
        block = ctx.block
        for name in block.ATTRIBS.values():
            assert hasattr(block, name) is True

    def test_load_block_context(self, ctx):
        # Leader() class is tested in TestLeader():
        assert len(ctx.leaders) == 1
        assert ctx.scale == 1
        assert ctx.base_point == (8.42, 0.70, 0)
        assert ctx.text_height == 5
        assert ctx.arrowhead_size == 3
        assert ctx.landing_gap_size == 2.5
        assert ctx.left_attachment == 1
        assert ctx.right_attachment == 1
        assert ctx.attachment_type == 0
        assert ctx.mtext is None
        assert ctx.block is not None  # see test_block_data()
        assert ctx.plane_origin == (1, 2, 3)
        assert ctx.plane_x_axis == (0, 1, 0)
        assert ctx.plane_y_axis == (1, 0, 0)
        assert ctx.plane_normal_reversed == 1
        assert ctx.top_attachment == 8
        assert ctx.bottom_attachment == 8

    def test_block_data(self, ctx):
        block = ctx.block
        assert block.block_record_handle == "FEFE"
        assert block.normal_direction == (0, 0, 1)
        assert block.location == (18.42, 0.70, 0)
        assert block.scale == (1.0, 2.0, 3.0)
        assert block.rotation == 0.2
        assert block.color == colors.BY_BLOCK_RAW_VALUE

    def test_get_transformation_matrix(self, ctx):
        # The transformation matrix is stored in transposed order
        # of ezdxf.math.Matrix44()!
        assert ctx.block._matrix == [
            1,
            0,
            0,
            18.42,
            0,
            1,
            0,
            0.70,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            1,
        ]
        assert ctx.block.matrix44.get_row(3) == (18.42, 0.70, 0, 1)

    def test_set_transformation_matrix(self):
        m = Matrix44()
        m.set_row(3, (4, 3, 2, 1))
        block = BlockData()
        block.matrix44 = m
        # The transformation matrix is stored in transposed order
        # of ezdxf.math.Matrix44()!
        assert block._matrix == [
            1,
            0,
            0,
            4,
            0,
            1,
            0,
            3,
            0,
            0,
            1,
            2,
            0,
            0,
            0,
            1,
        ]


BLOCK_MLEADER_R2010 = """  0
MULTILEADER
5
B5
330
1F
100
AcDbEntity
8
0
100
AcDbMLeader
270
2
300
CONTEXT_DATA{
40
1.0
10
8.42
20
0.70
30
0.0
41
5.0
140
3.0
145
2.5
174
1
175
1
176
0
177
0
290
0
296
1
341
FEFE
14
0.0
24
0.0
34
1.0
15
18.42
25
0.70
35
0.0
16
1.0
26
2.0
36
3.0
46
0.2
93
-1056964608
47
1.0
47
0.0
47
0.0
47
18.42
47
0.0
47
1.0
47
0.0
47
0.70
47
0.0
47
0.0
47
1.0
47
0.0
47
0.0
47
0.0
47
0.0
47
1.0
110
1.0
120
2.0
130
3.0
111
0.0
121
1.0
131
0.0
112
1.0
122
0.0
132
0.0
297
1
302
LEADER{
290
1
291
1
10
9.42
20
0.70
30
0.0
11
1.0
21
0.0
31
0.0
90
0
40
8.0
304
LEADER_LINE{
10
1.15
20
-10.40
30
0.0
91
0
92
-1056964608
305
}
271
0
303
}
272
8
273
8
301
}
340
6D
90
6816768
170
1
91
-1056964608
341
14
171
-2
290
1
291
1
41
8.0
42
4.0
172
1
343
11
173
1
95
1
174
1
175
0
92
-1056964608
292
0
344
94
93
-1056964608
10
1.0
20
1.0
30
1.0
43
0.0
176
0
293
0
330
A3
177
1
44
0.0
302
B
294
0
178
0
179
1
45
1.0
271
0
272
9
273
9
"""
