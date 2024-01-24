# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.lldxf.validator import (
    is_in_integer_range,
    is_valid_aci_color,
    is_valid_layer_name,
    is_valid_lineweight,
    is_not_null_vector,
    is_positive,
    fix_lineweight,
    is_integer_bool,
    is_valid_one_line_text,
    fix_one_line_text,
    is_not_zero,
    is_not_negative,
    is_one_of,
    is_in_float_range,
    fit_into_float_range,
    fix_integer_bool,
    fit_into_integer_range,
    is_valid_bitmask,
    fix_bitmask,
    is_greater_or_equal_zero,
    is_handle,
    is_transparency,
    is_valid_rgb,
)
from ezdxf.entities.layer import is_valid_layer_color_index, fix_layer_color


def test_invalid_layer_name():
    assert is_valid_layer_name("Layer Layer") is True
    assert is_valid_layer_name("Layer/") is False
    assert is_valid_layer_name("Layer=") is False
    assert is_valid_layer_name("Layer;") is False
    assert is_valid_layer_name("Layer:") is False
    assert is_valid_layer_name("Layer<") is False
    assert is_valid_layer_name("Layer>") is False
    assert is_valid_layer_name("Layer`") is False
    assert is_valid_layer_name("\\Layer`") is False
    assert is_valid_layer_name('"Layer"') is False

def test_the_asterisk_in_layer_names():
    """The `*` as first letter is used by AutoCAD for internal layer names, 
    which do not show up in the layers panel. Only the first letter can be a asterisk.
    """
    assert is_valid_layer_name("*Layer") is True
    assert is_valid_layer_name("*") is False
    assert is_valid_layer_name("L*ayer") is False
    assert is_valid_layer_name("Layer*") is False

def test_allow_dxf_unicode_encoding_in_layer_names():
    assert is_valid_layer_name(r"tschüss mit \U+00FC") is True


def test_allow_dxf_mplus_encoding_in_layer_names():
    # I don't know the real name of this encoding, so I call it "mplus" encoding
    assert is_valid_layer_name(r"\M+5D7DF\M+5CFDF\M+5BCDC") is True


def test_strange_but_valid_layer_name():
    assert is_valid_layer_name("Layer|Layer") is True


def test_is_adsk_special_layer():
    assert is_valid_layer_name("*adsk_xyz") is True
    assert is_valid_layer_name("*ADSK_xyz") is True
    assert is_valid_layer_name("ADSK_xyz*") is False


def test_is_valid_lineweight():
    assert is_valid_lineweight(0) is True
    assert is_valid_lineweight(50) is True
    assert is_valid_lineweight(211) is True
    assert is_valid_lineweight(-4) is False, "is too small"
    assert is_valid_lineweight(212) is False, "is too big"
    assert is_valid_lineweight(10) is False


def test_lineweight_fixer():
    assert fix_lineweight(-4) == -1, "too small, fix as BYLAYER"
    assert fix_lineweight(212) == 211, "too big, fix as biggest lineweight"
    assert fix_lineweight(10) == 13, "invalid, fix as next valid lineweight"


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
    assert validator(10) is False, "exclude end value"


def test_fit_into_integer_range():
    fixer = fit_into_integer_range(0, 6)
    assert fixer(-1) == 0
    assert fixer(0) == 0
    assert fixer(5) == 5
    assert fixer(6) == 5, "exclude end value"


def test_is_in_float_range():
    validator = is_in_float_range(1, 10)
    assert validator(0) is False
    assert validator(1) is True
    assert validator(9) is True
    assert validator(10) is True, "include end value"


def test_fit_into_float_range():
    fixer = fit_into_float_range(0.25, 4.00)
    assert fixer(0.24) == 0.25
    assert fixer(0.25) == 0.25
    assert fixer(0.50) == 0.50
    assert fixer(4.00) == 4.00, "include end value"
    assert fixer(4.01) == 4.00


def test_is_not_null_vector():
    assert is_not_null_vector((0, 0, 1)) is True
    assert is_not_null_vector((0, 1, 0)) is True
    assert is_not_null_vector((1, 0, 0)) is True
    assert is_not_null_vector((0, 0, 0)) is False


def test_is_positive_value():
    assert is_positive(1) is True
    assert is_positive(0.5) is True
    assert is_positive(0) is False
    assert is_positive(0.0) is False
    assert is_positive(-1) is False


def test_is_integer_bool():
    assert is_integer_bool(0) is True
    assert is_integer_bool(1) is True
    assert is_integer_bool(2) is False
    assert is_integer_bool(-1) is False


def test_fix_integer_bool():
    assert fix_integer_bool(0) == 0
    assert fix_integer_bool(1) == 1
    assert fix_integer_bool(None) == 0
    assert fix_integer_bool("") == 0
    assert fix_integer_bool("A") == 1
    assert fix_integer_bool(2) == 1
    assert fix_integer_bool(-1) == 1


@pytest.mark.parametrize(
    "invalid_text",
    [
        "test\ntext\r",
        "test\r\ntext",
        "testtext^",
        "test\ntext^",
        "test\ntext^\r",
    ],
)
def test_is_valid_one_line_text(invalid_text):
    assert is_valid_one_line_text(invalid_text) is False


@pytest.mark.parametrize(
    "invalid_text",
    [
        "test\ntext\r",
        "test\r\ntext",
        "testtext^",
        "test\ntext^",
        "test\ntext^\r",
    ],
)
def test_fix_invalid_one_line_text(invalid_text):
    assert fix_one_line_text(invalid_text) == "testtext"


def test_is_not_negative():
    assert is_not_negative(-1) is False
    assert is_not_negative(-1e-9) is False
    assert is_not_negative(0) is True
    assert is_not_negative(1e-9) is True
    assert is_not_negative(1) is True


def test_is_not_zero():
    assert is_not_zero(-1) is True
    assert is_not_zero(-1e-9) is True
    assert is_not_zero(1e-9) is True
    assert is_not_zero(1) is True
    assert is_not_zero(0) is False
    assert is_not_zero(0.0) is False
    assert is_not_zero(1e-12) is False
    assert is_not_zero(-1e-12) is False


def test_is_one_of():
    _validator = is_one_of({1, 3, 5})
    assert _validator(0) is False
    assert _validator(2) is False
    assert _validator(4) is False
    assert _validator(1) is True
    assert _validator(3) is True
    assert _validator(5) is True


def test_is_greater_or_equal_zero():
    assert is_greater_or_equal_zero(-1) is False
    assert is_greater_or_equal_zero(0) is True
    assert is_greater_or_equal_zero(1) is True


def test_is_valid_bitmask():
    validator = is_valid_bitmask(3)
    assert validator(0) is True
    assert validator(1) is True
    assert validator(2) is True
    assert validator(3) is True
    assert validator(4) is False


def test_fix_bitmask():
    fixer = fix_bitmask(3)
    assert fixer(0) == 0
    assert fixer(1) == 1
    assert fixer(2) == 2
    assert fixer(3) == 3
    assert fixer(4) == 0
    assert fixer(5) == 1


@pytest.mark.parametrize("aci", [255, -7, -1, 1, 7, 255])
def test_is_valid_layer_color(aci):
    assert is_valid_layer_color_index(aci) is True
    assert fix_layer_color(aci) == aci


@pytest.mark.parametrize("aci", [256, 0, 256])
def test_is_not_valid_layer_color(aci):
    assert is_valid_layer_color_index(aci) is False
    assert fix_layer_color(aci) == 7


@pytest.mark.parametrize("handle", ["0", "100", "FEFE"])
def test_is_a_handle(handle):
    assert is_handle(handle) is True


@pytest.mark.parametrize("handle", [None, 0, 0x200000, "xyz"])
def test_is_not_a_handle(handle):
    assert is_handle(handle) is False


@pytest.mark.parametrize(
    "t",
    [
        0x02000000,  # 100% transparent
        0x0200007F,  # 50% transparent
        0x020000FF,  # opaque
        0x01000000,  # ByBlock
    ],
)
def test_is_transparency(t):
    assert is_transparency(t) is True


@pytest.mark.parametrize("t", [None, 0, 127, 255, 0x01000001])
def test_is_not_transparency(t):
    assert is_transparency(t) is False


@pytest.mark.parametrize("rgb", [
    (0, 0, 0),
    [0, 0, 0],
    (255, 255, 255),
    [255, 255, 255],
])
def test_is_valid_rgb(rgb):
    assert is_valid_rgb(rgb) is True


@pytest.mark.parametrize("rgb", [
    None,
    1,
    1.0,
    "1",
    (0,),
    (0, 0),
    (0, 0, 0, 0),
    (-1, 0, 0),
    (256, 0, 0),
    ("0", 0, 0),
    (0.0, 0, 0),  # no floats!
])
def test_is_not_valid_rgb(rgb):
    assert is_valid_rgb(rgb) is False


if __name__ == "__main__":
    pytest.main([__file__])
