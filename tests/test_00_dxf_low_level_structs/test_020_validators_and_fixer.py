# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.lldxf.validator import (
    is_in_integer_range, is_valid_aci_color, is_valid_layer_name,
    is_valid_lineweight, is_not_null_vector, is_positive_value,
    fix_lineweight, is_integer_bool,
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


def test_lineweight_fixer():
    assert fix_lineweight(-4) == -1, 'too small, fix as BYLAYER'
    assert fix_lineweight(212) == 211, 'too big, fix as biggest lineweight'
    assert fix_lineweight(10) == 13, 'invalid, fix as next valid lineweight'


def test_is_valid_aci_color():
    assert is_valid_aci_color(-1) is False
    assert is_valid_aci_color(0) is True
    assert is_valid_aci_color(257) is True
    assert is_valid_aci_color(258) is False


def test_is_in_integer_range():
    validator = is_in_integer_range(1, 10)
    assert validator(0) is False
    assert validator(1) is True
    assert validator(9) is True
    assert validator(10) is False, 'exclude end value'


def test_is_not_null_vector():
    assert is_not_null_vector((0, 0, 1)) is True
    assert is_not_null_vector((0, 1, 0)) is True
    assert is_not_null_vector((1, 0, 0)) is True
    assert is_not_null_vector((0, 0, 0)) is False


def test_is_positive_value():
    assert is_positive_value(1) is True
    assert is_positive_value(0.5) is True
    assert is_positive_value(0) is False
    assert is_positive_value(0.0) is False
    assert is_positive_value(-1) is False


def test_is_integer_bool():
    assert is_integer_bool(0) is True
    assert is_integer_bool(1) is True
    assert is_integer_bool(2) is False
    assert is_integer_bool(-1) is False


if __name__ == '__main__':
    pytest.main([__file__])
