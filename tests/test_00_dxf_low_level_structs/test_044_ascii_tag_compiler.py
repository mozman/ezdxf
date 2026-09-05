# Copyright (c) 2026, Manfred Moitzi
# License: MIT License
"""ascii_tag_compiler() is the fused equivalent of the two-stage pipeline
tag_compiler(ascii_tags_loader(stream)) and has to stay that way - these tests
compare both implementations tag by tag, including the raised exceptions and
the line numbers reported in their messages.
"""
import pytest
from io import StringIO
from pathlib import Path

from ezdxf.lldxf.tagger import (
    ascii_tag_compiler,
    ascii_tags_loader,
    tag_compiler,
)
from ezdxf.lldxf.const import DXFStructureError
from ezdxf.lldxf.types import DXFTag, DXFVertex, DXFBinaryTag

EXAMPLES = Path(__file__).parent.parent.parent / "examples_dxf"


def collect(tags):
    """Returns all tags of a tag loader and the DXFStructureError it ends with."""
    result = []
    try:
        result.extend(tags)
    except DXFStructureError as e:
        return result, str(e)
    return result, None


def assert_same_tags(text: str, skip_comments: bool = True):
    """Asserts that both implementations return the same result for `text`."""
    expected_tags, expected_error = collect(
        tag_compiler(ascii_tags_loader(StringIO(text), skip_comments=skip_comments))
    )
    tags, error = collect(
        ascii_tag_compiler(StringIO(text), skip_comments=skip_comments)
    )

    assert error == expected_error
    assert len(tags) == len(expected_tags)
    for index, (tag, expected) in enumerate(zip(tags, expected_tags)):
        assert type(tag) is type(expected), f"different type of tag #{index}"
        assert tag.code == expected.code, f"different group code of tag #{index}"
        assert tag.value == expected.value, f"different value of tag #{index}"
    return tags


SIMPLE = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1018
  0
ENDSEC
  0
EOF
"""

COMMENTS = """999
comment 0
  0
SECTION
  2
HEADER
999
comment 1
  0
ENDSEC
  0
EOF
"""

POINTS_3D = """ 10
1.0
 20
2.0
 30
3.0
1011
100
1021
200
1031
300
  0
EOF
"""

POINTS_2D = """ 10
1.0
 20
2.0
 11
3.0
 21
4.0
  8
LAYER
  0
EOF
"""

POINT_2D_AT_EOF = """  8
LAYER
 10
1.0
 20
2.0
"""

# comment tags are removed by the loader stage, even inside a point
COMMENT_INSIDE_POINT = """ 10
1.0
999
comment
 20
2.0
999
comment
 30
3.0
  0
EOF
"""

MISSING_Y_COORDINATE = """  9
$EXTMIN
 20
100
 10
100
 40
1.0
"""

TRUNCATED_POINT = """  9
$EXTMIN
 10
100
 20
"""

INVALID_FLOAT = """ 10
1.0
 20
not-a-float
 30
3.0
  0
EOF
"""

INVALID_GROUP_CODE = """  8
LAYER
not-a-group-code
value
"""

FLOAT_FOR_INT = """ 71
1.0
  0
EOF
"""

INVALID_INT = """ 71
not-a-number
  0
EOF
"""

BINARY_DATA = """310
414243
  0
EOF
"""

INVALID_BINARY_DATA = """310
4142XY
  0
EOF
"""

DATA_BEYOND_EOF = """  0
EOF
  8
LAYER
"""

STRUCTURE_TAG_WITH_WHITESPACE = """  0
  SECTION
  0
EOF
"""

NO_LINE_BREAK_AT_EOF = """  8
LAYER
  0
EOF"""

ODD_LINE_COUNT = """  8
LAYER
  9
"""


SAMPLES = {
    "empty": "",
    "simple": SIMPLE,
    "comments": COMMENTS,
    "points_3d": POINTS_3D,
    "points_2d": POINTS_2D,
    "point_2d_at_eof": POINT_2D_AT_EOF,
    "comment_inside_point": COMMENT_INSIDE_POINT,
    "missing_y_coordinate": MISSING_Y_COORDINATE,
    "truncated_point": TRUNCATED_POINT,
    "invalid_float": INVALID_FLOAT,
    "invalid_group_code": INVALID_GROUP_CODE,
    "float_for_int": FLOAT_FOR_INT,
    "invalid_int": INVALID_INT,
    "binary_data": BINARY_DATA,
    "invalid_binary_data": INVALID_BINARY_DATA,
    "data_beyond_eof": DATA_BEYOND_EOF,
    "structure_tag_with_whitespace": STRUCTURE_TAG_WITH_WHITESPACE,
    "no_line_break_at_eof": NO_LINE_BREAK_AT_EOF,
    "odd_line_count": ODD_LINE_COUNT,
}


@pytest.mark.parametrize("text", SAMPLES.values(), ids=SAMPLES.keys())
@pytest.mark.parametrize("skip_comments", [True, False])
def test_same_result_as_two_stage_pipeline(text, skip_comments):
    assert_same_tags(text, skip_comments=skip_comments)


@pytest.mark.parametrize(
    "name",
    [path.name for path in sorted(EXAMPLES.glob("*.dxf"))],
)
def test_same_result_for_example_files(name):
    tags = assert_same_tags(
        (EXAMPLES / name).read_text(encoding="utf-8", errors="ignore")
    )
    assert len(tags) > 0


def test_skip_comments():
    tags = ascii_tag_compiler(StringIO("999\ncomment\n  0\nEOF\n"))
    assert list(tags) == [(0, "EOF")]


def test_do_not_skip_comments():
    tags = ascii_tag_compiler(StringIO("999\ncomment\n  0\nEOF\n"), skip_comments=False)
    assert list(tags) == [(999, "comment"), (0, "EOF")]


def test_compile_3d_point():
    tags = list(ascii_tag_compiler(StringIO(" 10\n1\n 20\n2\n 30\n3\n")))
    assert tags == [DXFVertex(10, (1, 2, 3))]


def test_compile_2d_point():
    tags = list(ascii_tag_compiler(StringIO(" 10\n1\n 20\n2\n  8\nLAYER\n")))
    assert tags == [DXFVertex(10, (1, 2)), DXFTag(8, "LAYER")]


def test_compile_xdata_point():
    tags = list(ascii_tag_compiler(StringIO("1011\n1\n1021\n2\n1031\n3\n")))
    assert tags == [DXFVertex(1011, (1, 2, 3))]


def test_compile_int_and_float_values():
    tags = list(ascii_tag_compiler(StringIO(" 90\n7\n 40\n1.5\n290\n1\n")))
    assert tags == [DXFTag(90, 7), DXFTag(40, 1.5), DXFTag(290, 1)]
    assert isinstance(tags[0].value, int)
    assert isinstance(tags[1].value, float)


def test_compile_binary_data():
    tags = list(ascii_tag_compiler(StringIO("310\n414243\n")))
    assert tags == [DXFBinaryTag(310, b"ABC")]


def test_accept_float_for_int_values():
    # ProE stores int values as floats
    tags = list(ascii_tag_compiler(StringIO(" 71\n1.0\n")))
    assert tags == [DXFTag(71, 1)]


def test_ignore_tags_beyond_eof():
    tags = list(ascii_tag_compiler(StringIO("  0\nEOF\n  8\nLAYER\n")))
    assert tags == [DXFTag(0, "EOF")]


def test_discard_point_truncated_by_end_of_stream():
    # same behavior as tag_compiler(ascii_tags_loader(...))
    tags = list(ascii_tag_compiler(StringIO("  9\n$EXTMIN\n 10\n100\n 20\n")))
    assert tags == [DXFTag(9, "$EXTMIN")]


def test_invalid_group_code_raises_exception():
    with pytest.raises(DXFStructureError):
        list(ascii_tag_compiler(StringIO("not-a-group-code\nvalue\n")))


def test_unexpected_coordinate_order_raises_exception():
    with pytest.raises(DXFStructureError):
        list(ascii_tag_compiler(StringIO(" 20\n100\n 10\n100\n 40\n1.0\n")))


def test_invalid_coordinate_value_raises_exception():
    with pytest.raises(DXFStructureError):
        list(ascii_tag_compiler(StringIO(" 10\n1\n 20\nx\n 30\n3\n")))


if __name__ == "__main__":
    pytest.main([__file__])
