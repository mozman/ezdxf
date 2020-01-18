# Copyright (C) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf

new = ezdxf.new


def test_new_AC1009():
    doc = new('R12')
    assert 'AC1009' == doc.dxfversion


def test_new_AC1015():
    doc = new('R2000')
    assert 'AC1015' == doc.dxfversion


def test_new_AC1018():
    doc = new('R2004')
    assert 'AC1018' == doc.dxfversion


def test_new_AC1021():
    doc = new('R2007')
    assert 'AC1021' == doc.dxfversion


def test_new_AC1024():
    doc = new('R2010')
    assert 'AC1024' == doc.dxfversion


def test_new_AC1027():
    doc = new('R2013')
    assert 'AC1027' == doc.dxfversion


def test_new_AC1032():
    doc = new('R2018')
    assert 'AC1032' == doc.dxfversion


def test_invalid_dxf_version():
    with pytest.raises(ezdxf.const.DXFVersionError):
        new('R13')
    with pytest.raises(ezdxf.const.DXFVersionError):
        new('R14')
    with pytest.raises(ezdxf.const.DXFVersionError):
        new('XYZ')
    with pytest.raises(ezdxf.const.DXFVersionError):
        new('AC1012')
    with pytest.raises(ezdxf.const.DXFVersionError):
        new('AC1013')
    with pytest.raises(ezdxf.const.DXFVersionError):
        new('AC1014')
