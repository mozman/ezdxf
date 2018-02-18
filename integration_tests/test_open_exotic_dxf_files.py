# Copyright 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
import ezdxf
import os

FILE_1 = r"D:\Source\dxftest\ChineseChars_cp936_R2004.dxf"
FILE_3 = r"D:\Source\dxftest\ChineseChars_cp936_R2004.zip"
FILE_4 = r"D:\Source\dxftest\ProE_AC1018.dxf"


@pytest.mark.skipif(not os.path.exists(FILE_1), reason='File {} not found'.format(FILE_1))
def test_read_plain_cp936_chinese():
    dwg = ezdxf.readfile(FILE_1)
    assert dwg.filename is not None
    assert dwg.dxfversion is not None


@pytest.mark.skipif(not os.path.exists(FILE_3), reason='File {} not found'.format(FILE_3))
def test_read_from_zip():
    dwg = ezdxf.readzip(FILE_3)
    assert dwg.filename is not None
    assert dwg.dxfversion is not None


@pytest.mark.skipif(not os.path.exists(FILE_4), reason='File {} not found'.format(FILE_4))
def test_read_crappy_ProE():
    dwg = ezdxf.readfile(FILE_4)
    assert dwg.filename is not None
    assert dwg.dxfversion is not None
