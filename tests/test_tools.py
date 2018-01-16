# Created: 27.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
import ezdxf
from ezdxf.tools.test import DrawingProxy
from ezdxf import DXFValueError, DXFTypeError
from ezdxf.tools import safe_3D_point


def getattributes(obj):
    return (attr for attr in dir(obj) if not attr.startswith('_DrawingProxy__'))


def test_drawing():
    dwg = ezdxf.new('AC1024')
    for attr in getattributes(DrawingProxy('AC1024')):
        if not hasattr(dwg, attr):
            raise Exception("attribute '%s' of DrawingProxy() does not exist in Drawing() class" % attr)


def test_3D_point():
    assert (1, 2, 3) == safe_3D_point((1, 2, 3))


def test_2D_point():
    assert (1, 2, 0) == safe_3D_point((1, 2))


def test_1D_point():
    with pytest.raises(DXFValueError):
        safe_3D_point((1, ))


def test_with_int():
    with pytest.raises(DXFTypeError):
        safe_3D_point(1)


def test_with_float():
    with pytest.raises(DXFTypeError):
        safe_3D_point(1.1)


def test_with_str():
    with pytest.raises(DXFTypeError):
        safe_3D_point("abc")
