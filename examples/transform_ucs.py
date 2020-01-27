# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
import pathlib
import math
import ezdxf
from ezdxf.math import UCS

OUTDIR = pathlib.Path('~/Desktop/Outbox').expanduser()

X_COUNT = 7
Y_COUNT = 7
DX = 2
DY = 2


def add_circle(msp, ucs):
    circle = msp.add_circle(center=(0, 0), radius=0.5, dxfattribs={
        'color': 6,
    })
    circle.transform_to_wcs(ucs)


def add_ocs_circle(msp, ucs):
    circle = msp.add_circle(center=(0, 0, .5), radius=0.25, dxfattribs={
        'color': 6,
        'extrusion': (1, 0, 0),
    })
    circle.transform_to_wcs(ucs)


def add_ellipse(msp, ucs):
    ellipse = msp.add_ellipse(
        center=(0, 0),
        major_axis=(.5, 0, 0),
        ratio=.5,
        start_param=0,
        end_param=math.pi,
        dxfattribs={
            'color': 1,
        })
    ellipse.transform_to_wcs(ucs)


def add_ocs_arc(msp, ucs):
    arc = msp.add_arc(center=(0, 0, 0.5), radius=0.25, start_angle=0, end_angle=90, dxfattribs={
        'color': 4,
        'extrusion': (-1, 0, 0),
    })
    arc.transform_to_wcs(ucs)


def add_solid(msp, ucs):
    solid = msp.add_solid([(-0.25, -0.15), (0.25, -0.15), (0, -0.5)], dxfattribs={'color': 2})
    solid.transform_to_wcs(ucs)


def add_trace(msp, ucs):
    solid = msp.add_solid([(-0.25, 0.15), (0.25, 0.15), (0, 0.5)], dxfattribs={'color': 7})
    solid.transform_to_wcs(ucs)


def add_3dface(msp, ucs):
    solid = msp.add_3dface([(0, 0, 0), (0.5, 0.5, 0), (0.5, 0.5, 0.5), (0, 0, 0.5)], dxfattribs={'color': 8})
    solid.transform_to_wcs(ucs)


def add_lwpolyline(msp, ucs):
    solid = msp.add_lwpolyline([(0, 0, 0), (0.3, 0, 1), (0.3, 0.3, 0), (0, 0.3, 0)], format='xyb',
                               dxfattribs={'color': 6})
    solid.transform_to_wcs(ucs)


def add_text(msp, ucs):
    text = msp.add_text('TEXT', dxfattribs={
        'color': 4,
        'style': 'OpenSansCondensed-Light',
        'height': .2,
    }).set_align('MIDDLE_CENTER')
    text.transform_to_wcs(ucs)


def add_mtext(msp, ucs):
    # It is always better to use text_direction instead of a rotation angle,
    # which works only for extrusion == (0, 0, 1)
    text = msp.add_mtext('MTEXT', dxfattribs={
        'color': 5,
        'style': 'OpenSansCondensed-Light',
        'char_height': .2,
        'insert': (0, 0),
        'rotation': 90,
        'attachment_point': 4,
    })
    text.transform_to_wcs(ucs)


def main(filename):
    doc = ezdxf.new('R2010', setup=True)
    msp = doc.modelspace()

    ucs = UCS()
    angle = math.pi / 12  # 15 degree

    for ix in range(X_COUNT):
        for iy in range(Y_COUNT):
            ucs.moveto((ix * DX, iy * DY, 0))
            ucs.render_axis(msp, length=1)
            add_circle(msp, ucs)
            # add_ocs_circle(msp, ucs)
            # add_ocs_arc(msp, ucs)
            # add_text(msp, ucs)
            add_mtext(msp, ucs)
            add_ellipse(msp, ucs)
            # add_solid(msp, ucs)
            # add_trace(msp, ucs)
            # add_3dface(msp, ucs)
            # add_lwpolyline(msp, ucs)
            ucs = ucs.rotate_local_z(angle)
        ucs = UCS().rotate_local_x(ix * angle)

    doc.set_modelspace_vport(Y_COUNT * (DY + 2), center=(X_COUNT * DX / 2, Y_COUNT * DY / 2))
    doc.saveas(filename)


if __name__ == '__main__':
    main(OUTDIR / "transform_ucs.dxf")
