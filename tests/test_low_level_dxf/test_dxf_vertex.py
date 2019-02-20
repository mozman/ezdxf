# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from ezdxf.lldxf.types import DXFVertex


def test_init():
    v = DXFVertex(10, (1, 2, 3))
    assert v.value == (1., 2., 3.)


def test_clone():
    v = DXFVertex(10, (1, 2, 3))
    v2 = v.clone()
    assert v2.code == v.code
    assert v2.value == v.value


def test_dxf_tags():
    v = DXFVertex(10, (1, 2, 3))
    tags = tuple(v.dxftags())
    assert tags[0] == (10, 1.)
    assert tags[1] == (20, 2.)
    assert tags[2] == (30, 3.)


def test_dxf_string():
    v = DXFVertex(10, (1, 2, 3))
    assert v.dxfstr() == " 10\n1.0\n 20\n2.0\n 30\n3.0\n"

