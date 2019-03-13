# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf

from ezdxf.pp.__main__ import readfile, dxfpp
from ezdxf.pp.rawpp import rawpp


@pytest.mark.skipif(ezdxf.PYPY_ON_WINDOWS, reason='Does not work on Windows with PyPy 3.5.3')
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
