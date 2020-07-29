# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.layouts import VirtualLayout


@pytest.fixture
def msp():
    return VirtualLayout()


def test_default_settings(msp):
    line = msp.add_line((0, 0), (1, 1))
    assert line.dxf.layer == '0'
    assert line.dxf.color == 256
    assert line.dxf.linetype == 'BYLAYER'
    assert line.dxf.ltscale == 1.0
    assert line.dxf.invisible == 0
    assert line.dxf.extrusion == (0, 0, 1)
    line.dxf.lineweight = 18  # set line weight
    assert line.dxf.lineweight == 18  # get line weight


@pytest.fixture
def line(msp):
    return msp.add_line((0, 0), (1, 1))


def test_ac1018_default_settings(line):
    line = line
    assert line.has_dxf_attrib('true_color') is False  # no default true color
    assert line.has_dxf_attrib('color_name') is False  # no default color name
    assert line.has_dxf_attrib('transparency') is False  # no default transparency


def test_ac1018_true_color(line):
    line.dxf.true_color = 0x0F0F0F
    assert 0x0F0F0F == line.dxf.true_color
    assert (0x0F, 0x0F, 0x0F) == line.rgb  # shortcut for modern graphic entities
    line.rgb = (255, 255, 255)  # shortcut for modern graphic entities
    assert 0xFFFFFF == line.dxf.true_color


def test_ac1018_color_name(line):
    line.dxf.color_name = "Rot"
    assert "Rot" == line.dxf.color_name


def test_ac1018_transparency(line):
    line.dxf.transparency = 0x020000FF  # 0xFF = opaque; 0x00 = 100% transparent
    assert 0x020000FF == line.dxf.transparency
    # recommend usage: helper property ModernGraphicEntity.transparency
    assert 0. == line.transparency  # 0. =  opaque; 1. = 100% transparent
    line.transparency = 1.0
    assert 0x02000000 == line.dxf.transparency


def test_ac1021_default_settings(line):
    assert line.has_dxf_attrib('shadow_mode') is False  # no default shadow_mode


@pytest.fixture(scope='module')
def layout():
    # Do not test VirtualLayout() here
    import ezdxf
    doc = ezdxf.new()
    return doc.modelspace()


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


def test_xline_ray(layout):
    xline = layout.add_xline((1, 2, 0), (1, 0, 0))
    assert (1, 2, 0) == xline.dxf.start
    assert (1, 0, 0) == xline.dxf.unit_vector
