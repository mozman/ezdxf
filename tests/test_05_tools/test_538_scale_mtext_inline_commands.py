#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.tools.text import scale_mtext_inline_commands


@pytest.mark.parametrize(
    "text",
    [
        r"word \H100; word",
        r"word \H100 word",
        r"\H100; word",
        r"\H100 word",
        r"word \H100;",
        r"word \H100",
        r"\H100;",
        r"\H100",
        r"\H100.000",
    ],
)
def test_scale_absolute_height_commands(text):
    result = scale_mtext_inline_commands(text, 2.0)
    assert r"\H200" in result


@pytest.mark.parametrize(
    "text",
    [
        r"word \H100; word",
        r"word \H100 word",
        r"\H100; word",
        r"\H100 word",
        r"word \H100;",
        r"word \H100",
        r"\H100;",
        r"\H100",
    ],
)
def test_scaling_preserves_content_structure(text):
    expected = text.replace("1", "2")
    result = scale_mtext_inline_commands(text, 2.0)
    assert result == expected


@pytest.mark.parametrize(
    "text",
    [
        r"word \H100x; word",
        r"word \H100x word",
        r"\H100x; word",
        r"\H100x word",
        r"word \H100x;",
        r"word \H100x",
        r"\H100x;",
        r"\H100x",
        r"\H100.000x",
    ],
)
def test_does_not_scale_relative_height_commands(text):
    result = scale_mtext_inline_commands(text, 2.0)
    assert result == text


@pytest.mark.parametrize(
    "text",
    [
        r"word \H; word",
        r"word \H word",
        r"word \H0 word",
        r"word \H0; word",
        r"\H; word",
        r"\H word",
        r"\H0 word",
        r"\H0; word",
        r"word \H;",
        r"word \H",
        r"word \H0",
        r"word \H0;",
    ],
)
def test_invalid_constructs_are_preserved(text):
    # ... it is not the domain of this function to validate the MTEXT content string:
    # garbage in, garbage out
    assert scale_mtext_inline_commands(text, 2.0) == text


def test_negative_factor():
    assert scale_mtext_inline_commands(r"\H100; word", -2.0) == r"\H200; word"


def test_empty_content():
    assert scale_mtext_inline_commands("", 2.0) == ""


if __name__ == "__main__":
    pytest.main([__file__])
