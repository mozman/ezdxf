# Copyright (C) 2014-2018, Manfred Moitzi
# License: MIT License
from ezdxf.graphicsfactory import copy_attribs


def test_None():
    result = copy_attribs(None)
    assert result == {}


def test_empty_dict():
    result = copy_attribs({})
    assert result == {}


def test_none_empty_dict():
    dxfattribs = {'height': 1.0, 'width': 0.8}
    result = copy_attribs(dxfattribs)
    assert result == {'height': 1.0, 'width': 0.8}

    # do not change original attribs
    result['height'] = 2.0
    assert dxfattribs['height'] == 1.0
