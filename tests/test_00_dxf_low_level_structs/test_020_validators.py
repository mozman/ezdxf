# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.lldxf.validator import (
    is_in_int_range, is_valid_aci_color, is_valid_layer_name,
    is_valid_lineweight,
)


def test_invalid_layer_name():
    assert is_valid_layer_name('Layer Layer') is True
    assert is_valid_layer_name('Layer/') is False
    assert is_valid_layer_name('Layer*') is False
    assert is_valid_layer_name('*Layer') is False
    assert is_valid_layer_name('Layer=') is False
    assert is_valid_layer_name('Layer;') is False
    assert is_valid_layer_name('Layer:') is False
    assert is_valid_layer_name('Layer<') is False
    assert is_valid_layer_name('Layer>') is False
    assert is_valid_layer_name('Layer`') is False
    assert is_valid_layer_name('\\Layer`') is False
    assert is_valid_layer_name('"Layer"') is False


def test_strange_but_valid_layer_name():
    assert is_valid_layer_name('Layer|Layer') is True


def test_is_adsk_special_layer():
    assert is_valid_layer_name('*adsk_xyz') is True
    assert is_valid_layer_name('*ADSK_xyz') is True
    assert is_valid_layer_name('ADSK_xyz*') is False


def test_is_valid_lineweight():
    assert is_valid_lineweight(0) is True
    assert is_valid_lineweight(50) is True
    assert is_valid_lineweight(211) is True
    assert is_valid_lineweight(-4) is False, 'is too small'
    assert is_valid_lineweight(212) is False, 'is too big'
    assert is_valid_lineweight(10) is False


def test_is_valis_aci_color():
    assert is_valid_aci_color(-1) is False
    assert is_valid_aci_color(0) is True
    assert is_valid_aci_color(257) is True
    assert is_valid_aci_color(258) is False


def test_is_in_int_range():
    validator = is_in_int_range(1, 10)
    assert validator(0) is False
    assert validator(1) is True
    assert validator(9) is True
    assert validator(10) is False, 'exclude end value , the standard Python ' \
                                   'behavior expected'


if __name__ == '__main__':
    pytest.main([__file__])
