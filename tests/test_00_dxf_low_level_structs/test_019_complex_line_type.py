# Copyright (C) 2018-2019, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.tools.complex_ltype import (
    lin_tokenizer,
    lin_parser,
    lin_compiler,
    ComplexLineTypePart,
)


def test_line_type_tokenizer_just_numbers():
    ltype = "A,.25,-.125,.25,-.125,0,-.125"
    result = list(lin_tokenizer(ltype))
    assert result == ["A", ".25", "-.125", ".25", "-.125", "0", "-.125"]


def test_line_type_tokenizer_strings():
    ltype = 'A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25'
    result = list(lin_tokenizer(ltype))
    assert result == [
        "A",
        ".5",
        "-.2",
        '["GAS"',
        "STANDARD",
        "S=.1",
        "U=0.0",
        "X=-0.1",
        "Y=-.05]",
        "-.25",
    ]


def test_line_type_tokenizer_string_with_comma():
    ltype = 'A, "TEXT, TEXT", 0'
    result = list(lin_tokenizer(ltype))
    assert result == ["A", '"TEXT, TEXT"', "0"]


def test_line_type_tokenizer_shapes():
    # A,.25,-.1,[BOX,ltypeshp.shx,x=-.1,s=.1],-.1,1 replacing BOX by shape index 132
    ltype = "A,.25,-.1,[132,ltypeshp.shx,x=-.1,s=.1],-.1,1"
    result = list(lin_tokenizer(ltype))
    assert result == [
        "A",
        ".25",
        "-.1",
        "[132",
        "ltypeshp.shx",
        "x=-.1",
        "s=.1]",
        "-.1",
        "1",
    ]


def test_line_type_parser_just_numbers():
    ltype = "A,.25,-.125,.25,-.125,0,-.125"
    result = lin_parser(ltype)
    assert result == ["A", 0.25, -0.125, 0.25, -0.125, 0, -0.125]


def test_line_type_parser_strings():
    ltype = 'A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25'
    result = lin_parser(ltype)
    assert result == [
        "A",
        0.5,
        -0.2,
        ["TEXT", "GAS", "STANDARD", "s", 0.1, "u", 0.0, "x", -0.1, "y", -0.05],
        -0.25,
    ]


def test_line_type_parser_shape():
    # A,.25,-.1,[BOX,ltypeshp.shx,x=-.1,s=.1],-.1,1 replacing BOX by shape index 132
    ltype = "A,.25,-.1,[132,ltypeshp.shx,x=-.1,s=.1],-.1,1"
    result = lin_parser(ltype)
    assert result == [
        "A",
        0.25,
        -0.1,
        ["SHAPE", 132, "ltypeshp.shx", "x", -0.1, "s", 0.1],
        -0.1,
        1,
    ]


def test_lin_compiler_floats():
    ltype = "A,.25,-.125,.25,-.125,0,-.125"
    result = lin_compiler(ltype)
    assert result == [
        (49, 0.25),
        (49, -0.125),
        (49, 0.25),
        (49, -0.125),
        (49, 0),
        (49, -0.125),
    ]


def test_lin_compiler_strings():
    ltype = 'A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25'
    result = lin_compiler(ltype)
    assert result[0] == (49, 0.5)
    assert result[1] == (49, -0.2)
    text = result[2]
    assert text.type == "TEXT"
    assert text.value == "GAS"
    assert text.font == "STANDARD"
    assert text.tags[0] == (46, 0.1)
    assert text.tags[1] == (50, 0)
    assert text.tags[2] == (44, -0.1)
    assert text.tags[3] == (45, -0.05)
    assert result[3] == (49, -0.25)


def test_lin_compiler_shape():
    # A,.25,-.1,[BOX,ltypeshp.shx,x=-.1,s=.1],-.1,1 replacing BOX by shape index 132
    ltype = "A,.25,-.1,[132,ltypeshp.shx,x=-.1,s=.1],-.1,1"
    result = lin_compiler(ltype)
    assert result[0] == (49, 0.25)
    assert result[1] == (49, -0.1)
    text = result[2]
    assert text.type == "SHAPE"
    assert text.value == 132
    assert text.font == "ltypeshp.shx"
    assert text.tags[0] == (46, 0.1)
    assert text.tags[1] == (50, 0.0)
    assert text.tags[2] == (44, -0.1)
    assert text.tags[3] == (45, 0.0)
    assert result[3] == (49, -0.1)
    assert result[4] == (49, 1)


def test_tags_from_complex_text():
    ltype = 'A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25'
    result = lin_compiler(ltype)
    cx_part = result[2]
    assert isinstance(cx_part, ComplexLineTypePart)
    assert cx_part.type == "TEXT"
    tags = cx_part.complex_ltype_tags(None)
    assert tags[0] == (74, 2)
    assert tags[1] == (75, 0)
    assert tags[2] == (340, "0")  # default handle without a DXF document
    assert tags[3] == (46, 0.1)  # s
    assert tags[4] == (50, 0)  # r
    assert tags[5] == (44, -0.1)  # x
    assert tags[6] == (45, -0.05)  # y
    assert tags[7] == (9, "GAS")


def test_tags_from_complex_shape():
    ltype = "A,.25,-.1,[132,ltypeshp.shx,x=-.1,s=.1],-.1,1"
    result = lin_compiler(ltype)
    cx_part = result[2]
    assert isinstance(cx_part, ComplexLineTypePart)
    assert cx_part.type == "SHAPE"
    tags = cx_part.complex_ltype_tags(None)
    assert tags[0] == (74, 4)
    assert tags[1] == (75, 132)  # shape index
    assert tags[2] == (340, "0")  # default handle with a DXF document
    assert tags[3] == (46, 0.1)  # s
    assert tags[4] == (50, 0.0)  # r
    assert tags[5] == (44, -0.1)  # x
    assert tags[6] == (45, 0.0)  # y


def test_new_table_entry_has_text_style_handle():
    import ezdxf

    doc = ezdxf.new("R2013")
    ltype = doc.linetypes.new(
        "GASLEITUNG2",
        dxfattribs={
            "description": "Gasleitung2 ----GAS----GAS----GAS----GAS----GAS----GAS--",
            "length": 1,
            "pattern": 'A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25',
        },
    )
    style_handle = ltype.pattern_tags.get_style_handle()
    assert style_handle == doc.styles.get("Standard").dxf.handle


if __name__ == "__main__":
    pytest.main([__file__])
