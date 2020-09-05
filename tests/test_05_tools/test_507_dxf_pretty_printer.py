# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf

from ezdxf.pp.__main__ import readfile, dxfpp
from ezdxf.pp.rawpp import rawpp


def test_dxf_drawing_to_html(tmpdir):
    name = tmpdir.join('test.dxf')
    doc = ezdxf.new()
    doc.saveas(name)

    tagger = readfile(name)
    # checks only if pretty printer is still working
    result = dxfpp(tagger, 'test.dxf')
    assert len(result) > 0

    # checks only if pretty printer is still working
    result = rawpp(readfile(name), filename='test.dxf')
    assert len(result) > 0
