# Purpose: test basic graphic entities
# Created: 25.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import pytest
import ezdxf


@pytest.fixture(scope='module')
def dxf_ac1015():
    return ezdxf.new('AC1015')


@pytest.fixture(scope='module')
def dxf_ac1018():
    return ezdxf.new('AC1018')


@pytest.fixture(scope='module')
def dxf_ac1021():
    return ezdxf.new('AC1021')


def test_ac1015_default_settings(dxf_ac1015):
    msp = dxf_ac1015.modelspace()
    line = msp.add_line((0, 0), (1, 1))
    assert line.dxf.layer == '0'
    assert line.dxf.color == 256
    assert line.dxf.linetype == 'BYLAYER'
    assert line.dxf.ltscale == 1.0
    assert line.dxf.invisible == 0
    assert line.dxf.extrusion == (0.0, 0.0, 1.0)
    with pytest.raises(ezdxf.DXFValueError):  # requires AC1018
        value = line.dxf.true_color
    with pytest.raises(ezdxf.DXFValueError):  # requires AC1018
        value = line.dxf.color_name
    with pytest.raises(ezdxf.DXFValueError):  # requires AC1018
        value = line.dxf.transparency
    with pytest.raises(ezdxf.DXFValueError):  # requires AC1021
        value = line.dxf.shadow_mode
    with pytest.raises(ezdxf.DXFValueError):  # not defined value
        value = line.dxf.lineweight

    line.dxf.lineweight = 17  # set line weight
    assert line.dxf.lineweight == 17  # get line weight


@pytest.fixture
def line_ac1018(dxf_ac1018):
    msp = dxf_ac1018.modelspace()
    return msp.add_line((0, 0), (1, 1))


def test_ac1018_default_settings(line_ac1018):
    line = line_ac1018
    assert line.dxf_attrib_exists('true_color') is False  # no default true color
    assert line.dxf_attrib_exists('color_name') is False  # no default color name
    assert line.dxf_attrib_exists('transparency') is False  # no default transparency
    with pytest.raises(ezdxf.DXFValueError):  # requires AC1021
        value = line.dxf.shadow_mode


def test_ac1018_true_color(line_ac1018):
    line = line_ac1018
    line.dxf.true_color = 0x0F0F0F
    assert 0x0F0F0F == line.dxf.true_color
    assert (0x0F, 0x0F, 0x0F) == line.rgb  # shortcut for modern graphic entities
    line.rgb = (255, 255, 255)  # shortcut for modern graphic entities
    assert 0xFFFFFF == line.dxf.true_color


def test_ac1018_color_name(line_ac1018):
    line = line_ac1018
    line.dxf.color_name = "Rot"
    assert "Rot" == line.dxf.color_name


def test_ac1018_transparency(line_ac1018):
    line = line_ac1018
    line.dxf.transparency = 0x020000FF  # 0xFF = opaque; 0x00 = 100% transparent
    assert 0x020000FF == line.dxf.transparency
    # recommend usage: helper property ModernGraphicEntity.transparency
    assert 0. == line.transparency  # 0. =  opaque; 1. = 100% transparent
    line.transparency = 1.0
    assert 0x02000000 == line.dxf.transparency


def test_ac1021_default_settings(dxf_ac1021):
    line = dxf_ac1021.modelspace().add_line((0, 0), (1, 1))
    assert line.dxf_attrib_exists('shadow_mode') is False  # no default shadow_mode


@pytest.fixture(scope='module')
def layout(dxf_ac1018):
    return dxf_ac1018.modelspace()


def test_iter_layout(layout):
    entity_count = len(list(layout))
    layout.add_line((0, 0), (1, 1))
    layout.add_line((0, 0), (1, 1))
    assert entity_count+2 == len(list(layout))


def test_create_line(layout):
    line = layout.add_line((0, 0), (1, 1))
    assert (0., 0.) == line.dxf.start
    assert (1., 1.) == line.dxf.end


def test_create_circle(layout):
    circle = layout.add_circle((3, 3), 5)
    assert (3., 3.) == circle.dxf.center
    assert 5. == circle.dxf.radius


def test_create_arc(layout):
    arc = layout.add_arc((3, 3), 5, 30, 60)
    assert (3., 3.) == arc.dxf.center
    assert 5. == arc.dxf.radius
    assert 30. == arc.dxf.start_angle
    assert 60. == arc.dxf.end_angle


def test_create_trace(layout):
    trace = layout.add_trace([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert (0, 0) == trace[0]
    assert (1, 0) == trace.dxf.vtx1
    assert (1, 1) == trace[2]
    assert (0, 1) == trace.dxf.vtx3


def test_create_solid(layout):
    trace = layout.add_solid([(0, 0), (1, 0), (1, 1)])
    assert (0, 0) == trace.dxf.vtx0
    assert (1, 0) == trace[1]
    assert (1, 1) == trace.dxf.vtx2
    assert (1, 1) == trace[3]


def test_create_3dface(layout):
    trace = layout.add_3dface([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)])
    assert (0, 0, 0) == trace.dxf.vtx0
    assert (1, 0, 0) == trace[1]
    assert (1, 1, 0) == trace.dxf.vtx2
    assert (0, 1, 0) == trace[3]


def test_create_text(layout):
    text = layout.add_text('text')
    assert 'text' == text.dxf.text


def test_text_set_alignment(layout):
    text = layout.add_text('text')
    text.set_pos((2, 2), align="TOP_CENTER")
    assert 1 == text.dxf.halign
    assert 3 == text.dxf.valign
    assert (2, 2) == text.dxf.align_point


def test_text_set_fit_alignment(layout):
    text = layout.add_text('text')
    text.set_pos((2, 2), (4, 2), align="FIT")
    assert 5 == text.dxf.halign
    assert 0 == text.dxf.valign
    assert (2, 2) == text.dxf.insert
    assert (4, 2) == text.dxf.align_point


def test_text_get_alignment(layout):
    text = layout.add_text('text')
    text.dxf.halign = 1
    text.dxf.valign = 3
    assert 'TOP_CENTER' == text.get_align()


def test_text_get_pos_TOP_CENTER(layout):
    text = layout.add_text('text')
    text.set_pos((2, 2), align="TOP_CENTER")
    align, p1, p2 = text.get_pos()
    assert "TOP_CENTER" == align
    assert p1 == (2, 2)
    assert p2 is None


def test_text_get_pos_LEFT(layout):
    text = layout.add_text('text')
    text.set_pos((2, 2))
    align, p1, p2 = text.get_pos()
    assert "LEFT" == align
    assert p1 == (2, 2)
    assert p2 is None


def test_create_shape(layout):
    shape = layout.add_shape("TestShape", (1, 2), 3.0)
    assert "TestShape" == shape.dxf.name
    assert (1.0, 2.0) == shape.dxf.insert
    assert 3.0 == shape.dxf.size
    assert 0.0 == shape.dxf.rotation
    assert 1.0 == shape.dxf.xscale
    assert 0.0 == shape.dxf.oblique


def test_create_ray(layout):
    ray = layout.add_ray((1, 2, 0), (1, 0, 0))
    assert (1, 2, 0) == ray.dxf.start
    assert (1, 0, 0) == ray.dxf.unit_vector


def test_create_ray(layout):
    xline = layout.add_xline((1, 2, 0), (1, 0, 0))
    assert (1, 2, 0) == xline.dxf.start
    assert (1, 0, 0) == xline.dxf.unit_vector
