# Copyright (c) 2018-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
import os

CP936_FILE = r"D:\Source\dxftest\ChineseChars_cp936_R2004.dxf"


@pytest.mark.skipif(not os.path.exists(CP936_FILE), reason='File {} not found'.format(CP936_FILE))
def test_read_plain_cp936_chinese():
    dwg = ezdxf.readfile(CP936_FILE)
    assert dwg.filename is not None
    assert dwg.dxfversion is not None


CP936_ZIP_FILE = r"D:\Source\dxftest\ChineseChars_cp936_R2004.zip"


@pytest.mark.skipif(not os.path.exists(CP936_ZIP_FILE), reason='File {} not found'.format(CP936_ZIP_FILE))
def test_read_from_zip():
    dwg = ezdxf.readzip(CP936_ZIP_FILE)
    assert dwg.filename is not None
    assert dwg.dxfversion is not None


PROE_FILE = r"D:\Source\dxftest\ProE_AC1018.dxf"


@pytest.mark.skipif(not os.path.exists(PROE_FILE), reason='File {} not found'.format(PROE_FILE))
def test_read_crappy_ProE():
    dwg = ezdxf.readfile(PROE_FILE)
    assert dwg.filename is not None
    assert dwg.dxfversion is not None


FILE_CIVIL_3D = r"D:\Source\dxftest\AutodeskProducts\Civil3D_2018.dxf"


@pytest.mark.skipif(not os.path.exists(FILE_CIVIL_3D), reason='File {} not found'.format(FILE_CIVIL_3D))
def test_read_civil_3d():
    dwg = ezdxf.readfile(FILE_CIVIL_3D)
    assert dwg.filename == FILE_CIVIL_3D
    assert dwg.dxfversion == 'AC1032'


FILE_MAP_3D = r"D:\Source\dxftest\AutodeskProducts\Map3D_2017.dxf"


@pytest.mark.skipif(not os.path.exists(FILE_MAP_3D), reason='File {} not found'.format(FILE_MAP_3D))
def test_read_map_3d():
    dwg = ezdxf.readfile(FILE_MAP_3D)
    assert dwg.filename == FILE_MAP_3D
    assert dwg.dxfversion == 'AC1027'
