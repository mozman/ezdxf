#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.tools.difftags import diff_tags, OpCode, round_tags
from ezdxf.lldxf.tags import Tags


def test_equal_string_tags():
    tags = Tags.from_text("0\nStringA\n0\nStringB\n")
    result = list(diff_tags(tags, tags))
    assert result == [(OpCode.equal, 0, 2, 0, 2)]


def test_round_tags():
    a = Tags.from_text("40\n1.0001\n40\n2.0001\n")
    b = list(round_tags(a, ndigits=3))
    assert b[0].value == 1.000
    assert b[1].value == 2.000


def test_equal_rounded_float_tags():
    a = Tags.from_text("40\n1.0001\n40\n2.0001\n")
    b = Tags.from_text("40\n1.0002\n40\n2.0002\n")
    result = list(diff_tags(a, b, ndigits=3))
    assert result == [(OpCode.equal, 0, 2, 0, 2)]


def test_equal_vertex_tags():
    tags = Tags.from_text("0\nA\n10\n1\n20\n2\n30\n3\n")
    result = list(diff_tags(tags, tags))
    assert result == [(OpCode.equal, 0, 2, 0, 2)]


if __name__ == '__main__':
    pytest.main([__file__])
