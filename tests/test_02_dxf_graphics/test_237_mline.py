# Copyright (c) 2018-2020 Manfred Moitzi
# License: MIT License
from typing import cast
import pytest
import math
from unittest.mock import MagicMock

import ezdxf

from ezdxf.audit import Auditor
from ezdxf.lldxf import const
from ezdxf.lldxf.tagwriter import TagCollector
from ezdxf.lldxf.tags import Tags
from ezdxf.entities.mline import MLineVertex, MLine, MLineStyle
from ezdxf.math import Matrix44, Vec3
from ezdxf.protocols import SupportsVirtualEntities, query_virtual_entities


# noinspection PyUnresolvedReferences
class TestMLine:
    @pytest.fixture(scope="class")
    def msp(self):
        return ezdxf.new().modelspace()

    @pytest.fixture
    def mline_mock_update_geometry(self):
        mline = MLine()
        mline.update_geometry = MagicMock()
        return mline

    def test_unbounded_mline(self):
        mline = MLine()
        assert mline.dxf.style_handle is None
        assert mline.dxf.style_name == "Standard"
        assert mline.style is None

    def test_generic_mline(self, msp):
        mline = msp.add_mline()
        assert mline.dxftype() == "MLINE"
        assert mline.dxf.style_name == "Standard"
        assert mline.dxf.count == 0
        assert mline.dxf.start_location == (0, 0, 0)

    def test_set_justification(self, mline_mock_update_geometry):
        mline = mline_mock_update_geometry
        mline.set_justification(mline.BOTTOM)
        assert mline.dxf.justification == mline.BOTTOM
        mline.update_geometry.assert_called_once()

    def test_set_scale_factor(self, mline_mock_update_geometry):
        mline = mline_mock_update_geometry
        mline.set_scale_factor(17)
        assert mline.dxf.scale_factor == 17
        mline.update_geometry.assert_called_once()

    def test_close_state(self, mline_mock_update_geometry):
        mline = mline_mock_update_geometry
        assert mline.is_closed is False
        mline.close(True)
        assert mline.is_closed is True
        mline.update_geometry.assert_called_once()

    def test_point_count_management(self):
        mline = MLine()
        mline.load_vertices(Tags.from_text(VTX_2))
        assert len(mline.vertices) == 2
        assert len(mline) == 2
        assert mline.dxf.count == 2, "should be a callback to __len__()"

    def test_add_first_vertex(self):
        mline = MLine()
        mline.extend([(0, 0, 0)])
        assert mline.start_location() == (0, 0, 0)
        assert len(mline) == 1

    def test_add_two_vertices(self, msp):
        # MLineStyle is required
        mline = msp.add_mline([(0, 0), (10, 0)])
        assert mline.start_location() == (0, 0, 0)
        assert len(mline) == 2
        assert mline.vertices[0].line_direction.isclose((1, 0))
        assert mline.vertices[0].miter_direction.isclose((0, 1))
        assert mline.vertices[1].line_direction.isclose(
            (1, 0)
        ), "continue last line segment"
        assert mline.vertices[1].miter_direction.isclose((0, 1))

    def test_x_rotation(self, msp):
        mline = msp.add_mline([(0, 5), (10, 5)])
        m = Matrix44.x_rotate(math.pi / 2)
        mline.transform(m)
        assert mline.start_location().isclose((0, 0, 5))
        assert mline.dxf.extrusion.isclose((0, -1, 0))
        assert mline.dxf.scale_factor == 1

    def test_translate(self, msp):
        mline = msp.add_mline([(0, 5), (10, 5)])
        m = Matrix44.translate(1, 1, 1)
        mline.transform(m)
        assert mline.start_location().isclose((1, 6, 1))
        assert mline.dxf.scale_factor == 1

    def test_uniform_scale(self, msp):
        mline = msp.add_mline([(0, 5), (10, 5)])
        m = Matrix44.scale(2, 2, 2)
        mline.transform(m)
        assert mline.start_location().isclose((0, 10, 0))
        assert mline.dxf.scale_factor == 2

    def test_non_uniform_scale(self, msp):
        mline = msp.add_mline([(1, 2, 3), (3, 4, 3)])
        m = Matrix44.scale(2, 1, 3)
        mline.transform(m)
        assert mline.start_location().isclose((2, 2, 9))
        assert mline.dxf.scale_factor == 1, "ignore non-uniform scaling"

    def test_support_virtual_entities_protocol(self, msp):
        mline = msp.add_mline([(1, 2, 3), (3, 4, 3)])
        assert isinstance(mline, SupportsVirtualEntities)
        assert len(query_virtual_entities(mline)) > 0

    def test_virtual_sub_entities_source_tracking(self, msp):
        mline = msp.add_mline([(1, 2, 3), (3, 4, 3)])
        result = set(e.source_of_copy for e in mline.virtual_entities())
        assert len(result) == 1, "only one source of copy expected"
        assert mline in result, "mline should be the source of copy"


class TestMLineStyle:
    @pytest.fixture(scope="class")
    def doc(self):
        return ezdxf.new()

    def test_standard_mline_style(self, doc):
        mline_style = cast("MLineStyle", doc.mline_styles.get("Standard"))
        assert mline_style.dxftype() == "MLINESTYLE"

        elements = mline_style.elements
        assert len(elements) == 2
        assert elements[0].offset == 0.5
        assert elements[0].color == 256
        assert elements[0].linetype == "BYLAYER"
        assert elements[1].offset == -0.5
        assert elements[1].color == 256
        assert elements[1].linetype == "BYLAYER"

    def test_set_defined_style(self, doc):
        style = doc.mline_styles.new("DefinedStyle")
        mline = doc.modelspace().add_mline()
        mline.set_style("DefinedStyle")
        assert mline.dxf.style_name == "DefinedStyle"
        assert mline.dxf.style_handle == style.dxf.handle

    def test_set_undefined_style(self, doc):
        mline = doc.modelspace().add_mline()
        with pytest.raises(const.DXFValueError):
            mline.set_style("UndefinedStyle")

    def test_ordered_indices(self):
        style = MLineStyle()
        style.elements.append(5)  # top order
        style.elements.append(-5)  # bottom border
        style.elements.append(0)
        style.elements.append(1)
        assert style.ordered_indices() == [1, 2, 3, 0]

    def test_invalid_element_count(self, doc):
        style = doc.mline_styles.new("InvalidMLineStyle")
        assert len(style.elements) == 0
        auditor = Auditor(doc)
        style.audit(auditor)
        assert auditor.has_errors is True, "invalid element count"


class TestMLineVertex:
    def test_load_tags(self):
        tags = Tags.from_text(VTX_1)
        vtx = MLineVertex.load(tags)
        assert isinstance(vtx.location, Vec3)
        assert vtx.location == (0, 0, 0)
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
            (1, 1),
            (1, 0),
            (0, 1),
            [(0.5, 0), (0, 0)],
            [tuple(), tuple()],
        )
        assert vtx.location == (1, 1, 0)
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
        assert tags[0] == (11, vtx.location[0])
        assert tags[1] == (21, vtx.location[1])
        assert tags[2] == (31, vtx.location[2])

        assert tags[3] == (12, vtx.line_direction[0])
        assert tags[4] == (22, vtx.line_direction[1])
        assert tags[5] == (32, vtx.line_direction[2])

        assert tags[6] == (13, vtx.miter_direction[0])
        assert tags[7] == (23, vtx.miter_direction[1])
        assert tags[8] == (33, vtx.miter_direction[2])

        # line- and fill parameters
        assert tags[9:] == t[3:]


class TestMLineAudit:
    @pytest.fixture(scope="class")
    def doc(self):
        d = ezdxf.new()
        new_style = d.mline_styles.new("NewStyle1")
        new_style.elements.append(0.5)
        new_style.elements.append(0)
        return d

    @pytest.fixture(scope="class")
    def msp(self, doc):
        return doc.modelspace()

    @pytest.fixture
    def auditor(self, doc):
        return Auditor(doc)

    @pytest.fixture
    def mline1(self, msp):
        return msp.add_mline([(0, 0), (1, 1)])

    def test_valid_mline(self, mline1, auditor):
        mline1.audit(auditor)
        assert auditor.has_errors is False
        assert auditor.has_fixes is False

    def test_fix_invalid_style_name(self, mline1, auditor):
        mline1.dxf.style_name = "test"
        mline1.audit(auditor)
        assert mline1.dxf.style_name == "Standard"
        assert auditor.has_fixes is False, "silent fix"

    def test_fix_invalid_style_handle(self, mline1, auditor):
        mline1.dxf.style_name = "test"
        mline1.dxf.style_handle = "0"
        mline1.audit(auditor)
        assert mline1.dxf.style_name == "Standard"
        assert (
            mline1.dxf.style_handle
            == auditor.doc.mline_styles["Standard"].dxf.handle
        )
        assert auditor.has_fixes is True

    def test_fix_invalid_style_handle_by_name(self, mline1, doc, auditor):
        new_style = doc.mline_styles.get("NewStyle1")
        mline1.dxf.style_name = "NewStyle1"
        mline1.dxf.style_handle = "0"
        mline1.audit(auditor)
        assert mline1.dxf.style_name == new_style.dxf.name
        assert mline1.dxf.style_handle == new_style.dxf.handle
        assert auditor.has_fixes is True

    def test_fix_invalid_line_direction(self, mline1, auditor):
        mline1.vertices[0].line_direction = (0, 0, 0)
        mline1.audit(auditor)
        assert auditor.has_fixes is True

    def test_fix_invalid_miter_direction(self, mline1, auditor):
        mline1.vertices[0].miter_direction = (0, 0, 0)
        mline1.audit(auditor)
        assert auditor.has_fixes is True

    def test_fix_invalid_line_parameters(self, mline1, auditor):
        mline1.vertices[0].line_params = []
        mline1.audit(auditor)
        assert auditor.has_fixes is True


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

VTX_2 = """11
0.0
21
0.0
31
0.0
11
10.0
21
0.0
31
0.0
"""
