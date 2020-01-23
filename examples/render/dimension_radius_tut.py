# Purpose: created dimensions for the radius dimension tutorial
# Created: 21.01.2020
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.math import Vector

OUTDIR = pathlib.Path('~/Desktop/Outbox').expanduser()
if not OUTDIR.exists():
    OUTDIR = pathlib.Path()

TEXT_ATTRIBS = {
    'height': .25,
    'style': ezdxf.options.default_dimension_text_style,
}
DIM_TEXT_STYLE = ezdxf.options.default_dimension_text_style
DXFVERSION = 'R2000'
RADIUS = 2.5
DELTA = 6


def set_main_view(doc, center=(0, 0), height=10, icon=3):
    vport = doc.viewports.get('*Active')[0]
    vport.dxf.center = center
    vport.dxf.height = height
    vport.dxf.ucs_icon = icon


def add_dim(msp, x, y, override, dimstyle='EZ_RADIUS'):
    center = Vector(x, y)
    msp.add_circle(center, radius=RADIUS)
    dim = msp.add_radius_dim(
        center=center,
        radius=RADIUS,
        angle=45,
        dimstyle=dimstyle,
        override=override)
    dim.render()


def add_dim_user(msp, x, y, distance, override):
    center = Vector(x, y)
    msp.add_circle(center, radius=RADIUS)
    location = center + Vector.from_deg_angle(45, distance)
    add_mark(msp, location)
    dim = msp.add_radius_dim(
        center=center,
        radius=RADIUS,
        location=location,
        dimstyle='EZ_RADIUS',
        override=override)
    dim.render()


def add_mark(msp, location, size=.15, color=5):
    attribs = {'color': color}
    offset_1 = Vector(size / 2, 0)
    offset_2 = Vector(0, size / 2)
    msp.add_line(start=location - offset_1, end=location + offset_1, dxfattribs=attribs)
    msp.add_line(start=location - offset_2, end=location + offset_2, dxfattribs=attribs)
    msp.add_circle(location, radius=size * .35, dxfattribs=attribs)


def add_3x_dim(msp, x_locations, dimstyle='EZ_RADIUS'):
    for x, dimtad in zip(x_locations, (1, 0, 4)):
        add_dim(msp, x, 0, override={'dimtad': dimtad}, dimstyle=dimstyle)


def add_3x_dim_user(msp, x_locations, distance):
    for x, dimtad in zip(x_locations, (1, 0, 4)):
        add_dim_user(msp, x, 0, distance, override={'dimtad': dimtad})


def radius_default_outside():
    doc = ezdxf.new(DXFVERSION, setup=True)
    add_3x_dim(doc.modelspace(), [0, DELTA, 2 * DELTA])
    set_main_view(doc, center=(DELTA, 0), height=10, icon=0)
    doc.saveas(OUTDIR / f'tut_dim_radius_default_outside.dxf')


def radius_default_outside_horizontal():
    doc = ezdxf.new(DXFVERSION, setup=True)
    style = doc.dimstyles.get('EZ_RADIUS')
    style.dxf.dimtoh = 1
    add_3x_dim(doc.modelspace(), [0, DELTA, 2 * DELTA])
    set_main_view(doc, center=(DELTA, 0), height=10, icon=0)
    doc.saveas(OUTDIR / f'tut_dim_radius_default_outside_horizontal.dxf')


def radius_default_inside(dimtmove=0):
    doc = ezdxf.new(DXFVERSION, setup=True)
    style = doc.dimstyles.get('EZ_RADIUS_INSIDE')
    style.dxf.dimtmove = dimtmove
    add_3x_dim(doc.modelspace(), [0, DELTA, 2 * DELTA], dimstyle='EZ_RADIUS_INSIDE')
    set_main_view(doc, center=(DELTA, 0), height=10, icon=0)
    doc.saveas(OUTDIR / f'tut_dim_radius_default_inside_dimtmove_{dimtmove}.dxf')


def radius_default_inside_horizontal(dimtmove=0):
    doc = ezdxf.new(DXFVERSION, setup=True)
    style = doc.dimstyles.get('EZ_RADIUS_INSIDE')
    style.dxf.dimtmove = dimtmove
    style.dxf.dimtih = 1
    add_3x_dim(doc.modelspace(), [0, DELTA, 2 * DELTA], dimstyle='EZ_RADIUS_INSIDE')
    set_main_view(doc, center=(DELTA, 0), height=10, icon=0)
    doc.saveas(OUTDIR / f'tur_dim_radius_default_inside_horizontal_dimtmove_{dimtmove}.dxf')


def radius_user_defined_outside(delta=DELTA):
    doc = ezdxf.new(DXFVERSION, setup=True)
    add_3x_dim_user(doc.modelspace(), [0, delta, 2 * delta], distance=RADIUS + 1.5)
    set_main_view(doc, center=(delta, 0), height=10, icon=0)
    doc.saveas(OUTDIR / f'tut_dim_radius_user_defined_outside.dxf')


def radius_user_defined_outside_horizontal(delta=DELTA):
    doc = ezdxf.new(DXFVERSION, setup=True)
    style = doc.dimstyles.get('EZ_RADIUS')
    style.dxf.dimtoh = 1
    add_3x_dim_user(doc.modelspace(), [0, delta, 2 * delta], distance=RADIUS + 1.5)
    set_main_view(doc, center=(delta, 0), height=10, icon=0)
    doc.saveas(OUTDIR / f'tut_dim_radius_user_defined_outside_horizontal.dxf')


def radius_user_defined_inside(delta=DELTA, dimtmove=0):
    doc = ezdxf.new(DXFVERSION, setup=True)
    style = doc.dimstyles.get('EZ_RADIUS')
    style.dxf.dimtmove = dimtmove
    add_3x_dim_user(doc.modelspace(), [0, delta, 2 * delta], distance=RADIUS - 1.5)
    set_main_view(doc, center=(delta, 0), height=10, icon=0)
    doc.saveas(OUTDIR / f'tut_dim_radius_user_defined_inside_dimtmove_{dimtmove}.dxf')


def radius_user_defined_inside_horizontal(delta=DELTA):
    doc = ezdxf.new(DXFVERSION, setup=True)
    style = doc.dimstyles.get('EZ_RADIUS')
    style.dxf.dimtih = 1
    add_3x_dim_user(doc.modelspace(), [0, delta, 2 * delta], distance=RADIUS - 1.5)
    set_main_view(doc, center=(delta, 0), height=10, icon=0)
    doc.saveas(OUTDIR / f'tut_dim_radius_user_defined_inside_horizontal.dxf')


if __name__ == '__main__':
    radius_default_outside()
    radius_default_outside_horizontal()
    radius_default_inside(dimtmove=0)  # dimline from center
    radius_default_inside(dimtmove=1)  # dimline from text
    radius_default_inside_horizontal(dimtmove=0)  # dimline from center
    radius_default_inside_horizontal(dimtmove=1)  # dimline from text
    radius_user_defined_outside()
    radius_user_defined_outside_horizontal()
    radius_user_defined_inside(dimtmove=0)  # dimline from text, also for 1
    radius_user_defined_inside(dimtmove=2)  # dimline from center
    radius_user_defined_inside_horizontal()
