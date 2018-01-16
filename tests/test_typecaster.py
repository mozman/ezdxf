# Created: 10.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from ezdxf.lldxf.tags import cast_tag


def test_cast_string():
    result = cast_tag((1, 'STRING'))
    assert (1, 'STRING') == result


def test_cast_float():
    result = cast_tag((10, ('1', '2', '3')))
    assert (10, (1, 2, 3)) == result


def test_cast_int():
    result = cast_tag((60, '4711'))
    assert (60, 4711) == result


def test_cast_bool_True():
    result = cast_tag((290, '1'))
    assert (290, 1) == result


def test_cast_bool_False():
    result = cast_tag((290, '0'))
    assert (290, 0) == result


def test_cast_2d_point():
    result = cast_tag((10, ('1', '2')))
    assert (10, (1, 2)) == result


def test_cast_3d_point():
    result = cast_tag((10, ('1', '2', '3')))
    assert (10, (1, 2, 3)) == result

