# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf

from ezdxf.pp.__main__ import readfile, dxfpp


def test_dxf_drawing_to_html(tmpdir):
    name = tmpdir.join('test.dxf')
    doc = ezdxf.new2()
    doc.saveas(name)

    tagger = readfile(name)
    # checks only if pretty printer is still working
    result = dxfpp(tagger)
    assert len(result) > 0

