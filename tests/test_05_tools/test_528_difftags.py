#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.tools.difftags import diff_tags, OpCode, round_tags
from ezdxf.lldxf.tags import Tags, dxftag

A = dxftag(0, "TagA")
B = dxftag(0, "TagB")
C = dxftag(0, "TagC")
D = dxftag(0, "TagD")


def test_equal_string_tags():
    a = Tags([A, B])
    result = list(diff_tags(a, a))
    assert result == [(OpCode.equal, 0, 2, 0, 2)]


def test_round_tags():
    a = Tags([dxftag(40, 1.0001), dxftag(40, 2.0001)])
    b = list(round_tags(a, ndigits=3))
    assert b[0].value == 1.000
    assert b[1].value == 2.000


def test_equal_rounded_float_tags():
    a = Tags([dxftag(40, 1.0001), dxftag(40, 2.0001)])
    b = Tags([dxftag(40, 1.0002), dxftag(40, 2.0002)])
    result = list(diff_tags(a, b, ndigits=3))
    assert result == [(OpCode.equal, 0, 2, 0, 2)]


def test_equal_vertex_tags():
    a = Tags([A, dxftag(10, (1, 2, 3))])
    result = list(diff_tags(a, a))
    assert result == [(OpCode.equal, 0, 2, 0, 2)]


def test_prepend_tag():
    a = Tags([A, B])
    b = Tags([C, A, B])
    result = list(diff_tags(a, b))
    assert result == [
        (OpCode.insert, 0, 0, 0, 1),
        (OpCode.equal, 0, 2, 1, 3),
    ]


def test_insert_tag():
    a = Tags([A, B])
    b = Tags([A, C, B])
    result = list(diff_tags(a, b))
    assert result == [
        (OpCode.equal, 0, 1, 0, 1),
        (OpCode.insert, 1, 1, 1, 2),
        (OpCode.equal, 1, 2, 2, 3),
    ]


def test_append_tag():
    a = Tags([A, B])
    b = Tags([A, B, C])
    result = list(diff_tags(a, b))
    assert result == [
        (OpCode.equal, 0, 2, 0, 2),
        (OpCode.insert, 2, 2, 2, 3),
    ]


def test_replace_last_tag():
    a = Tags([A, B])
    b = Tags([A, C])
    result = list(diff_tags(a, b))
    assert result == [
        (OpCode.equal, 0, 1, 0, 1),
        (OpCode.replace, 1, 2, 1, 2),
    ]


def test_replace_inner_tag():
    a = Tags([A, B, C])
    b = Tags([A, D, C])
    result = list(diff_tags(a, b))
    assert result == [
        (OpCode.equal, 0, 1, 0, 1),
        (OpCode.replace, 1, 2, 1, 2),
        (OpCode.equal, 2, 3, 2, 3),
    ]


def test_delete_last_tag():
    a = Tags([A, B, C])
    b = Tags([A, B])
    result = list(diff_tags(a, b))
    assert result == [
        (OpCode.equal, 0, 2, 0, 2),
        (OpCode.delete, 2, 3, 2, 2),
    ]


def test_delete_inner_tag():
    a = Tags([A, B, C])
    b = Tags([A, C])
    result = list(diff_tags(a, b))
    assert result == [
        (OpCode.equal, 0, 1, 0, 1),
        (OpCode.delete, 1, 2, 1, 1),
        (OpCode.equal, 2, 3, 1, 2),
    ]


if __name__ == '__main__':
    pytest.main([__file__])
