# Purpose: using arc DIMENSION
# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
from typing import Optional
import pathlib
import math
import ezdxf
from ezdxf.math import Vec3, UCS, ConstructionArc
import logging

# ========================================
# Setup logging
# ========================================
logging.basicConfig(level="WARNING")

# ========================================
# Setup your preferred output directory
# ========================================
OUTDIR = pathlib.Path("~/Desktop/Outbox").expanduser()
if not OUTDIR.exists():
    OUTDIR = pathlib.Path()

# ========================================
# Default text attributes
# ========================================
TEXT_ATTRIBS = {
    "height": 0.25,
    "style": ezdxf.options.default_dimension_text_style,
}
DIM_TEXT_STYLE = ezdxf.options.default_dimension_text_style

# =======================================================
# Discarding dimension rendering is possible
# for BricsCAD, but is incompatible to AutoCAD -> error
# =======================================================
BRICSCAD = False

DXFVERSION = "R2013"


def add_lines(
    msp, center: Vec3, radius: float, start_angle: float, end_angle: float
):
    attribs = {"color": 7}
    start_point = center + Vec3.from_deg_angle(start_angle) * radius
    end_point = center + Vec3.from_deg_angle(end_angle) * radius
    msp.add_line(center, start_point, dxfattribs=attribs)
    msp.add_line(center, end_point, dxfattribs=attribs)


def add_arc(
    msp, center: Vec3, radius: float, start_angle: float, end_angle: float
):
    attribs = {"color": 7}
    msp.add_arc(center, radius, start_angle, end_angle, dxfattribs=attribs)


def arc_cra_default(
    distance: float,
    filename: str,
    show_angle=True,
    override: dict = None,
):
    doc = ezdxf.new(DXFVERSION, setup=True)
    msp = doc.modelspace()
    radius = 5
    data = [
        [Vec3(0, 0), 60, 120],
        [Vec3(10, 0), 300, 240],
        [Vec3(20, 0), 240, 300],
        [Vec3(30, 0), 300, 30],
    ]
    if override is None:
        override = dict()
    for dimtad, offset in [(1, (0, 20)), (0, (0, 0)), (4, (0, -20))]:
        for center, start_angle, end_angle in data:
            center += Vec3(offset)
            override["dimtad"] = dimtad

            if show_angle:
                add_lines(msp, center, radius, start_angle, end_angle)
                add_arc(msp, center, radius, start_angle, end_angle)
            # Default DimStyle EZ_CURVED:
            # - angle units = degree
            # - scale 1: 100
            # - closed filled arrow, size = 0.25
            # - text location above dimension line
            #
            # center:
            #   center of angle
            # radius:
            #   distance from center to the start of the extension lines
            # distance:
            #   distance from start of the extension lines to the dimension line
            # start_angle:
            #   start angle in degrees
            # end_angle:
            #   end angle in degrees
            dim = msp.add_arc_dim_cra(
                center=center,
                radius=radius,
                start_angle=start_angle,
                end_angle=end_angle,
                distance=distance,
                override=override,
            )
            # Necessary second step, to create the BLOCK entity with the DIMENSION
            # geometry. Ezdxf supports DXF R2000 attributes for DXF R12 rendering,
            # but they have to be applied by the DIMSTYLE override feature, this
            # additional attributes are not stored in the XDATA section of the
            # DIMENSION entity, they are just used to render the DIMENSION entity.
            # The return value `dim` is not a DIMENSION entity, instead a
            # DimStyleOverride object is returned, the DIMENSION entity is stored
            # as dim.dimension, see also ezdxf.override.DimStyleOverride class.
            dim.render(discard=BRICSCAD)

    doc.set_modelspace_vport(height=70)
    doc.saveas(OUTDIR / f"{filename}_{DXFVERSION}.dxf")


def arc_cra_default_outside():
    """Outside means: the dimension line is farther away from the center than
    the extension line start points.
    """
    arc_cra_default(
        distance=2.0,
        filename="dim_arc_cra_outside",
        show_angle=True,
    )


def arc_cra_default_outside_fixed_extension_length():
    """Outside means: the dimension line is farther away from the center than
    the extension line start points.
    """
    arc_cra_default(
        distance=2.0,
        filename="dim_arc_cra_outside_fxl",
        show_angle=True,
        override={
            "dimfxlon": 1,  # use fixed length extension lines
            "dimexe": 0.5,  # length "above" the dimension line
            "dimfxl": 1.0,  # length "below" the dimension line
        },
    )


def arc_cra_default_inside():
    """Inside means: the dimension line is closer to the center than
    the extension line start points.
    """
    arc_cra_default(
        distance=-2.0,
        filename="dim_arc_cra_inside",
        show_angle=False,
    )


def arc_cra_default_inside_fixed_extension_length():
    """Inside means: the dimension line is closer to the center than
    the extension line start points.
    """
    arc_cra_default(
        distance=-2.0,
        filename="dim_arc_cra_inside_fxl",
        show_angle=False,
        override={
            "dimfxlon": 1,  # use fixed length extension lines
            "dimexe": 0.5,  # length "above" the dimension line
            "dimfxl": 1.0,  # length "below" the dimension line
        },
    )


def arc_3p_default(distance: float = 2.0):
    doc = ezdxf.new(DXFVERSION, setup=True)
    msp = doc.modelspace()
    radius = 5
    data = [
        [Vec3(0, 0), 60, 120],
        [Vec3(10, 0), 300, 240],
        [Vec3(20, 0), 240, 300],
    ]
    for dimtad, offset in [(1, (0, 20)), (0, (0, 0)), (4, (0, -20))]:
        for center, start_angle, end_angle in data:
            center += Vec3(offset)
            dir1 = Vec3.from_deg_angle(start_angle)
            dir2 = Vec3.from_deg_angle(end_angle)

            # calculate defpoints from parameters of the "cra" example:
            p1 = center + dir1 * radius
            p2 = center + dir2 * radius
            base = center + dir1.lerp(dir2) * (radius + distance)

            add_lines(msp, center, radius, start_angle, end_angle)
            add_arc(msp, center, radius, start_angle, end_angle)
            msp.add_arc_dim_3p(
                base,
                center,
                p1,
                p2,
                override={
                    "dimtad": dimtad,
                    "dimtxt": 1,
                    "dimasz": 1,
                    "dimgap": 0.25,
                },
            ).render(discard=BRICSCAD)

    doc.set_modelspace_vport(height=70)
    doc.saveas(OUTDIR / f"dim_arc_3p_{DXFVERSION}.dxf")


def dim_arc_3d():
    doc = ezdxf.new(DXFVERSION, setup=True)
    msp = doc.modelspace()

    for center, radius, sa, ea, distance in [
        [Vec3(0, 0), 5, 60, 90, 2]
    ]:
        arc = ConstructionArc(center, radius, sa, ea)
        ucs = UCS(origin=center + (5, 5)).rotate_local_x(math.radians(45))
        msp.add_line(arc.center, arc.start_point).transform(ucs.matrix)
        msp.add_line(arc.center, arc.end_point).transform(ucs.matrix)

        dim = msp.add_arc_dim_arc(
            arc=arc,
            distance=distance, dimstyle="EZ_CURVED"
        )
        dim.render(discard=BRICSCAD, ucs=ucs)

    doc.set_modelspace_vport(height=30)
    doc.saveas(OUTDIR / f"dim_arc_3d_{DXFVERSION}.dxf")


def arc_units_tol_limits():
    doc = ezdxf.new(DXFVERSION, setup=True)
    msp = doc.modelspace()
    radius = 5
    distance = 2
    data = [
        [Vec3(0, 0), 60, 120, 0, 0],
        [Vec3(10, 0), 300, 240, 0, 0],
        [Vec3(20, 0), 240, 300, 1, 0],  # tolerance
        [Vec3(30, 0), 300, 30, 0, 1],  # limits
    ]
    for dimaunit, offset in [
        [0, Vec3(0, 0)],
        [1, Vec3(0, 20)],
        [2, Vec3(0, 40)],
        [3, Vec3(0, 60)],
    ]:
        for center, start_angle, end_angle, dimtol, dimlim in data:
            center += offset
            add_lines(msp, center, radius, start_angle, end_angle)
            dim = msp.add_arc_dim_cra(
                center,
                radius,
                start_angle,
                end_angle,
                distance,
                override={
                    "dimaunit": dimaunit,
                    "dimtol": dimtol,
                    "dimtp": 1.0,
                    "dimtm": 2.0,
                    "dimlim": dimlim,
                },
            )
            dim.render(discard=BRICSCAD)

    doc.set_modelspace_vport(height=70)
    doc.saveas(OUTDIR / f"dim_arc_units_tol_limits_{DXFVERSION}.dxf")


def add_arc_dim(
    msp,
    center: Vec3,
    angle: float,
    delta: float,
    radius: float,
    distance: float,
    text_rotation: Optional[float],
    override: dict,
):
    start_angle = angle - delta
    end_angle = angle + delta
    add_lines(msp, center, radius, start_angle, end_angle)
    dim = msp.add_angular_dim_cra(
        center,
        radius,
        start_angle,
        end_angle,
        distance,
        text_rotation=text_rotation,
        override=override,
    )
    return dim


def measure_fixed_angle(angle: float):
    doc = ezdxf.new(DXFVERSION, setup=True)
    msp = doc.modelspace()
    x_dist = 15
    for dimtad, y_dist in [[0, 0], [1, 20], [4, 40]]:
        for count in range(8):
            dim = add_arc_dim(
                msp,
                center=Vec3(x_dist * count, y_dist),
                angle=45.0 * count,
                delta=angle / 2.0,
                radius=3.0,
                distance=1.0,
                text_rotation=None,
                override={"dimtad": dimtad},
            )
            dim.render(discard=BRICSCAD)
    doc.set_modelspace_vport(height=100, center=(x_dist * 4, 20))
    doc.saveas(OUTDIR / f"dim_arc_deg_{angle:.0f}_{DXFVERSION}.dxf")


def usr_location_absolute(angle: float, rotation: float = None):
    doc = ezdxf.new(DXFVERSION, setup=True)
    msp = doc.modelspace()
    x_dist = 15
    radius = 3.0
    distance = 1.0
    for dimtad, y_dist, leader in [
        [0, 0, False],
        [0, 20, True],
        [4, 40, True],
    ]:
        for count in range(8):
            center = Vec3(x_dist * count, y_dist)
            main_angle = 45.0 * count
            dim = add_arc_dim(
                msp,
                center=center,
                angle=main_angle,
                delta=angle / 2.0,
                radius=radius,
                distance=distance,
                text_rotation=rotation,
                override={"dimtad": dimtad},
            )
            # user location in WCS coordinates, absolut location:
            usr_location = center + Vec3.from_deg_angle(
                main_angle, radius + distance * 2.0
            )
            dim.set_location(usr_location, leader=leader)
            dim.render(discard=BRICSCAD)

    doc.set_modelspace_vport(height=100, center=(x_dist * 4, 40))
    rstr = ""
    if rotation is not None:
        rstr = f"rot_{rotation}_"
    doc.saveas(OUTDIR / f"dim_arc_usr_loc_absolute_{rstr}_{DXFVERSION}.dxf")


def usr_location_relative(angle: float, rotation: float = None):
    doc = ezdxf.new(DXFVERSION, setup=True)
    msp = doc.modelspace()
    x_dist = 10
    radius = 3.0
    distance = 1.0
    for dimtad, y_dist, leader in [
        [0, 0, False],
        [0, 10, True],
        [4, 20, True],
    ]:
        for count in range(8):
            center = Vec3(x_dist * count, y_dist)
            main_angle = 45.0 * count
            dim = add_arc_dim(
                msp,
                center=center,
                angle=main_angle,
                delta=angle / 2.0,
                radius=radius,
                distance=distance,
                text_rotation=rotation,
                override={"dimtad": dimtad},
            )
            # user location relative to center of dimension line:
            usr_location = Vec3.from_deg_angle(main_angle, 2.0)
            dim.set_location(usr_location, leader=leader, relative=True)
            dim.render(discard=BRICSCAD)

    doc.set_modelspace_vport(height=100, center=(x_dist * 4, 40))
    rstr = ""
    if rotation is not None:
        rstr = f"rot_{rotation}_"
    doc.saveas(OUTDIR / f"dim_arc_usr_loc_relative_{rstr}_{DXFVERSION}.dxf")


def show_all_arrow_heads():
    doc = ezdxf.new(DXFVERSION, setup=True)
    msp = doc.modelspace()
    x_dist = 4.0
    y_dist = 5.0
    for x, arrow_name in enumerate(sorted(ezdxf.ARROWS.__all_arrows__)):
        for y, angle in enumerate((3.0, 30.0)):
            center = Vec3(x * x_dist, y * y_dist)
            dim = add_arc_dim(
                msp,
                center=center,
                angle=90.0,
                delta=angle / 2.0,
                radius=3.0,
                distance=1.0,
                text_rotation=None,
                override={"dimblk": arrow_name},
            )
            dim.render(discard=BRICSCAD)

    doc.set_modelspace_vport(height=40, center=(50, 5))
    doc.saveas(OUTDIR / f"dim_arc_all_arrows_{DXFVERSION}.dxf")


if __name__ == "__main__":
    arc_cra_default_outside()
    arc_cra_default_outside_fixed_extension_length()
    arc_cra_default_inside()
    arc_cra_default_inside_fixed_extension_length()
    arc_3p_default()
    dim_arc_3d()
    arc_units_tol_limits()
    measure_fixed_angle(3.0)
    measure_fixed_angle(6.0)
    measure_fixed_angle(9.0)
    usr_location_absolute(6)
    usr_location_absolute(6, rotation=15)
    usr_location_relative(30)
    usr_location_relative(30, rotation=345)
    show_all_arrow_heads()
