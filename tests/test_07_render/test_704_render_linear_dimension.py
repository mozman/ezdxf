# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License

import ezdxf
import pytest

from ezdxf.render.dimension import LinearDimension, DimStyleOverride
from ezdxf.render.dim_base import compile_mtext
from ezdxf.math import Vec3


@pytest.fixture(scope="module")
def dwg():
    return ezdxf.new("R2007", setup=True)


def test_linear_dimension_with_one_tolerance(dwg):
    msp = dwg.modelspace()
    dimline = msp.add_linear_dim(base=(0, 10), p1=(0, 0), p2=(100, 0))
    override = {
        "dimlfac": 1,
        "dimtol": 1,
        "dimtfac": 0.5,
        "dimtolj": 0,
        "dimtp": 0.01,
        "dimtm": 0.01,
    }
    style = DimStyleOverride(dimline.dimension, override)
    renderer = LinearDimension(dimline.dimension, override=style)
    assert renderer.measurement.text == "100"
    assert renderer.measurement.decimal_separator == "."
    assert renderer.tol.decimal_places == 2  # default value
    assert renderer.tol.text == "±0.01"
    assert renderer.tol.valign == 0
    assert compile_mtext(renderer.measurement, renderer.tol) == r"\A0;100{\H0.50x;±0.01}"


def test_linear_dimension_with_two_tolerances(dwg):
    msp = dwg.modelspace()
    dimline = msp.add_linear_dim(base=(0, 10), p1=(0, 0), p2=(101, 0))
    override = {
        "dimlfac": 1,
        "dimtol": 1,
        "dimtfac": 0.5,
        "dimtolj": 1,
        "dimtp": 0.02,
        "dimtm": 0.03,
    }
    style = DimStyleOverride(dimline.dimension, override)
    renderer = LinearDimension(dimline.dimension, override=style)
    assert renderer.measurement.text == "101"
    assert renderer.measurement.decimal_separator == "."
    assert renderer.tol.decimal_places == 2  # default value
    assert renderer.tol.text_upper == "+0.02"
    assert renderer.tol.text_lower == "-0.03"
    assert renderer.tol.valign == 1
    assert compile_mtext(renderer.measurement, renderer.tol) == r"\A1;101{\H0.50x;\S+0.02^ -0.03;}"


def test_linear_dimension_with_limits(dwg):
    msp = dwg.modelspace()
    dimline = msp.add_linear_dim(base=(0, 10), p1=(0, 0), p2=(101, 0))
    override = {
        "dimlfac": 1,
        "dimlim": 1,
        "dimtfac": 0.5,
        "dimtp": 0.02,
        "dimtm": 0.03,
    }
    style = DimStyleOverride(dimline.dimension, override)
    renderer = LinearDimension(dimline.dimension, override=style)
    assert renderer.measurement.text == "101"
    assert renderer.measurement.decimal_separator == "."
    assert renderer.tol.decimal_places == 2  # default value
    assert renderer.tol.text_upper == "101.02"
    assert renderer.tol.text_lower == "100.97"
    assert compile_mtext(renderer.measurement, renderer.tol) == r"{\H0.50x;\S101.02^ 100.97;}"


def test_dimension_insert_attribute_translates_the_block_content():
    doc = ezdxf.new()
    msp = doc.modelspace()
    dimline = msp.add_linear_dim(base=(0, 10), p1=(0, 0), p2=(100, 0))
    dimline.render()
    dim = dimline.dimension
    blk = dim.get_geometry_block()

    blk_points = blk.query("POINT")
    virtual_points = [
        e for e in dim.virtual_entities() if e.dxftype() == "POINT"
    ]

    # without the insert attribute, the virtual points should be located at the
    # original location:
    for vpoint, blk_point in zip(virtual_points, blk_points):
        assert vpoint.dxf.location.isclose(blk_point.dxf.location)

    # set an insertion point for this dimension ...
    INSERT = Vec3(10, 10, 0)
    dim.dxf.insert = Vec3(INSERT)
    virtual_points = [
        e for e in dim.virtual_entities() if e.dxftype() == "POINT"
    ]

    # ... and the virtual points should be translated by the insert vector
    for vpoint, blk_point in zip(virtual_points, blk_points):
        assert (vpoint.dxf.location - blk_point.dxf.location).isclose(INSERT)
