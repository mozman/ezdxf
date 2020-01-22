# Purpose: created dimensions for the radius dimension tutorial
# Created: 21.01.2020
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.math import Vector


# ========================================
# Setup your preferred output directory
# ========================================
OUTDIR = pathlib.Path('~/Desktop/Outbox').expanduser()
if not OUTDIR.exists():
    OUTDIR = pathlib.Path()

# ========================================
# Default text attributes
# ========================================
TEXT_ATTRIBS = {
    'height': .25,
    'style': ezdxf.options.default_dimension_text_style,
}
DIM_TEXT_STYLE = ezdxf.options.default_dimension_text_style


def set_main_view(doc, center=(0, 0), height=10, icon=3):
    vport = doc.viewports.get('*Active')[0]
    vport.dxf.center = center
    vport.dxf.height = height
    vport.dxf.ucs_icon = icon  # switch off WCS icon


RADIUS = 2.5
DELTA = 6


def radius_default_outside(dxfversion='R2000'):
    def add_dim(x, y, dimtad):
        msp.add_circle((x, y), radius=RADIUS)
        dim = msp.add_radius_dim(center=(x, y), radius=RADIUS, angle=45, dimstyle='EZ_RADIUS',
                                 override={'dimtad': dimtad})
        dim.render()

    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    add_dim(0, 0, dimtad=1)
    add_dim(DELTA, 0, dimtad=0)
    add_dim(DELTA*2, 0, dimtad=4)
    set_main_view(doc, center=(DELTA, 0), height=10, icon=0)
    doc.saveas(OUTDIR / f'tut_dim_radius_default_outside.dxf')


def radius_default_outside_horizontal(dxfversion='R2000'):
    def add_dim(x, y, dimtad):
        msp.add_circle((x, y), radius=RADIUS)
        dim = msp.add_radius_dim(center=(x, y), radius=RADIUS, angle=45, dimstyle='EZ_RADIUS',
                                 override={
                                     'dimtoh': 1,  # force text outside horizontal
                                     'dimtad': dimtad,
                                 })
        dim.render()

    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    add_dim(0, 0, dimtad=1)
    add_dim(DELTA, 0, dimtad=0)
    add_dim(DELTA*2, 0, dimtad=4)
    set_main_view(doc, center=(DELTA, 0), height=10, icon=0)
    doc.saveas(OUTDIR / f'tut_dim_radius_default_outside_horizontal.dxf')


def radius_default_inside(dxfversion='R2000', dimtmove=0):
    def add_dim(x, y, dimtad):
        msp.add_circle((x, y), radius=RADIUS)
        dim = msp.add_radius_dim(center=(x, y), radius=RADIUS, angle=45, dimstyle='EZ_RADIUS_INSIDE',
                                 override={
                                     'dimtad': dimtad,
                                 })
        dim.render()

    doc = ezdxf.new(dxfversion, setup=True)
    style = doc.dimstyles.get('EZ_RADIUS_INSIDE')
    style.dxf.dimtmove = dimtmove
    msp = doc.modelspace()
    add_dim(0, 0, dimtad=1)  # above
    add_dim(DELTA, 0, dimtad=0)  # center
    add_dim(DELTA*2, 0, dimtad=4)  # below

    set_main_view(doc, center=(DELTA, 0), height=10, icon=0)
    doc.saveas(OUTDIR / f'tut_dim_radius_default_inside_dimtmove_{dimtmove}.dxf')


def radius_default_inside_horizontal(dxfversion='R2000', delta=10, dimtmove=0):
    doc = ezdxf.new(dxfversion, setup=True)
    style = doc.dimstyles.get('EZ_RADIUS_INSIDE')
    style.dxf.dimtmove = dimtmove

    msp = doc.modelspace()
    x, y = 0, 0
    angle = Vector(x, y).angle_deg
    msp.add_circle((x, y), radius=3)
    dim = msp.add_radius_dim(center=(x, y), radius=3, angle=angle, dimstyle='EZ_RADIUS_INSIDE',
                             override={
                                 'dimtih': 1,  # force text inside horizontal
                             })
    dim.render()
    doc.set_modelspace_vport(height=3 * delta)
    doc.saveas(OUTDIR / f'tur_dim_radius_default_inside_horizontal_dimtmove_{dimtmove}.dxf')


def radius_user_defined_outside(dxfversion='R2000', delta=15):
    def add_dim(x, y, radius, dimtad):
        center = Vector(x, y)
        msp.add_circle((x, y), radius=3)
        dim_location = center + Vector.from_deg_angle(angle, radius)
        dim = msp.add_radius_dim(center=(x, y), radius=3, location=dim_location, dimstyle='EZ_RADIUS',
                                 override={
                                     'dimtad': dimtad,
                                 })
        dim.render()

    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    x, y = 0, 0
    add_dim(x, y, 5, dimtad=1)  # above
    add_dim(x + 3 * delta, y, 5, dimtad=0)  # center
    add_dim(x + 6 * delta, y, 5, dimtad=4)  # below
    doc.set_modelspace_vport(height=3 * delta, center=(4.5 * delta, 0))
    doc.saveas(OUTDIR / f'tut_dim_radius_user_defined_outside.dxf')


def radius_user_defined_outside_horizontal(dxfversion='R2000', delta=15):
    def add_dim(x, y, radius, dimtad):
        center = Vector(x, y)
        msp.add_circle((x, y), radius=3)
        dim_location = center + Vector.from_deg_angle(angle, radius)
        dim = msp.add_radius_dim(center=(x, y), radius=3, location=dim_location, dimstyle='EZ_RADIUS',
                                 override={
                                     'dimtad': dimtad,
                                     'dimtoh': 1,  # force text outside horizontal
                                 })
        dim.render()

    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    x, y = 0, 0
    angle = Vector(x, y).angle_deg
    add_dim(x, y, 5, dimtad=1)  # above
    add_dim(x + 3 * delta, y, 5, dimtad=0)  # center
    add_dim(x + 6 * delta, y, 5, dimtad=4)  # below

    doc.set_modelspace_vport(height=3 * delta, center=(4.5 * delta, 0))
    doc.saveas(OUTDIR / f'tut_dim_radius_user_defined_outside_horizontal.dxf')


def radius_user_defined_inside(dxfversion='R2000', delta=10, dimtmove=0):
    def add_dim(x, y, radius, dimtad):
        center = Vector(x, y)
        msp.add_circle((x, y), radius=3)
        dim_location = center + Vector.from_deg_angle(angle, radius)
        dim = msp.add_radius_dim(center=(x, y), radius=3, location=dim_location, dimstyle='EZ_RADIUS',
                                 override={
                                     'dimtad': dimtad,
                                 })
        dim.render()

    doc = ezdxf.new(dxfversion, setup=True)
    style = doc.dimstyles.get('EZ_RADIUS')
    style.dxf.dimtmove = dimtmove

    msp = doc.modelspace()
    x, y=0, 0

    angle = Vector(x, y).angle_deg
    add_dim(x, y, 1, dimtad=1)  # above
    add_dim(x + 3 * delta, y, 1, dimtad=0)  # center
    add_dim(x + 6 * delta, y, 1, dimtad=4)  # below

    doc.set_modelspace_vport(height=3 * delta, center=(4.5 * delta, 0))
    doc.saveas(OUTDIR / f'tut_dim_radius_user_defined_inside_dimtmove_{dimtmove}.dxf')


def radius_user_defined_inside_horizontal(dxfversion='R2000', delta=10):
    def add_dim(x, y, radius, dimtad):
        center = Vector(x, y)
        msp.add_circle((x, y), radius=3)
        dim_location = center + Vector.from_deg_angle(angle, radius)
        dim = msp.add_radius_dim(center=(x, y), radius=3, location=dim_location, dimstyle='EZ_RADIUS',
                                 override={
                                     'dimtad': dimtad,
                                     'dimtih': 1,  # force text inside horizontal
                                 })
        dim.render()

    doc = ezdxf.new(dxfversion, setup=True)
    msp = doc.modelspace()
    x, y = 0, 0
    angle = Vector(x, y).angle_deg
    add_dim(x, y, 1, dimtad=1)  # above
    add_dim(x + 3 * delta, y, 1, dimtad=0)  # center
    add_dim(x + 6 * delta, y, 1, dimtad=4)  # below

    doc.set_modelspace_vport(height=3 * delta, center=(4.5 * delta, 0))
    doc.saveas(OUTDIR / f'tut_dim_radius_user_defined_inside_horizontal.dxf')


if __name__ == '__main__':
    radius_default_outside()
    radius_default_outside_horizontal()
    # radius_default_inside(dimtmove=0)  # dimline from center
    # radius_default_inside(dimtmove=1)  # dimline from text
    # radius_default_inside_horizontal(dimtmove=0)  # dimline from center
    # radius_default_inside_horizontal(dimtmove=1)  # dimline from text
    # radius_user_defined_outside()
    # radius_user_defined_outside_horizontal()
    # radius_user_defined_inside(dimtmove=0)  # dimline from text, also for 1
    # radius_user_defined_inside(dimtmove=2)  # dimline from center
    # radius_user_defined_inside_horizontal()
