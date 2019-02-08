# Copyright (c) 2019 Manfred Moitzi
# License: MIT License

import ezdxf
import pytest

from ezdxf.render.dimension import LinearDimension, DimStyleOverride


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2007', setup=True)


def test_linear_dimension_with_one_tolerance(dwg):
    block = dwg.blocks.new_anonymous_block(type_char='D')
    msp = dwg.modelspace()
    dimline = msp.add_linear_dim(base=(0, 10), p1=(0, 0), p2=(100, 0))
    override = {
        'dimlfac': 1,
        'dimtol': 1,
        'dimtfac': .5,
        'dimtolj': 0,
        'dimtp': 0.01,
        'dimtm': 0.01,
    }
    style = DimStyleOverride(dimline.dimension, override)
    renderer = LinearDimension(dimline.dimension, block, override=style)
    assert renderer.text == '100'
    assert renderer.text_decimal_separator == '.'
    assert renderer.tol_decimal_places == 4  # default value
    assert renderer.tol_text == '±0.0100'
    assert renderer.tol_valign == 0
    assert renderer.compile_mtext() == r"\A0;100{\H0.50x;±0.0100}"


def test_linear_dimension_with_two_tolerances(dwg):
    block = dwg.blocks.new_anonymous_block(type_char='D')
    msp = dwg.modelspace()
    dimline = msp.add_linear_dim(base=(0, 10), p1=(0, 0), p2=(101, 0))
    override = {
        'dimlfac': 1,
        'dimtol': 1,
        'dimtfac': .5,
        'dimtolj': 1,
        'dimtp': 0.02,
        'dimtm': 0.03,
    }
    style = DimStyleOverride(dimline.dimension, override)
    renderer = LinearDimension(dimline.dimension, block, override=style)
    assert renderer.text == '101'
    assert renderer.text_decimal_separator == '.'
    assert renderer.tol_decimal_places == 4  # default value
    assert renderer.tol_text_upper == '+0.0200'
    assert renderer.tol_text_lower == '-0.0300'
    assert renderer.tol_valign == 1
    assert renderer.compile_mtext() == r"\A1;101{\H0.50x;\S+0.0200^-0.0300}"


