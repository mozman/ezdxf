# Created: 16.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest

from ezdxf.modern.tableentries import Layer, Linetype, Style
from ezdxf.modern.tableentries import AppID, BlockRecord, DimStyle
from ezdxf.modern.tableentries import UCS, View, VPort


class DXFFactory:
    rootdict = {'ACAD_PLOTSTYLENAME': 'AFAF'}


@pytest.fixture
def layer():
    return Layer.new('FFFF', dxffactory=DXFFactory())


def test_layer_get_handle(layer):
    assert 'FFFF' == layer.dxf.handle


def test_layer_get_name(layer):
    assert 'LayerName' == layer.dxf.name


def test_layer_default_plotstylename(layer):
    assert 'AFAF' == layer.dxf.plot_style_name


def test_layer_is_layer_will_be_plotted_by_default(layer):
    assert layer.dxf.plot == 1


@pytest.fixture
def ltype():
    return Linetype.new('FFFF', dxfattribs={
        'name': 'TEST',
        'description': 'TESTDESC',
        'pattern': [0.2, 0.1, -0.1]
    })


def test_linetype_name(ltype):
    assert 'TEST' == ltype.dxf.name


def test_linetype_description(ltype):
    assert 'TESTDESC' == ltype.dxf.description


def test_linetype_pattern_items_count(ltype):
    def count_items():
        subclass = ltype.tags.get_subclass('AcDbLinetypeTableRecord')
        return len(subclass.find_all(49))

    assert 2 == ltype.dxf.items
    assert ltype.dxf.items == count_items()


@pytest.fixture
def complex_ltype():
    return Linetype.new('FFFF', dxfattribs={
        'name': 'GASLEITUNG',
        'description': 'Gasleitung ----GAS----GAS----GAS----GAS----GAS----GAS--',
        'length': 3.0,  # length is required for complex line types
        'pattern': 'A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25',
    })


def test_complex_linetype_name(complex_ltype):
    assert 'GASLEITUNG' == complex_ltype.dxf.name


def test_complex_linetype_description(complex_ltype):
    assert 'Gasleitung ----GAS----GAS----GAS----GAS----GAS----GAS--' == complex_ltype.dxf.description


def test_complex_linetype_pattern_items_count(complex_ltype):
    # only (49, ...) tags count
    assert 3 == complex_ltype.dxf.items


def test_style_name():
    style = Style.new('FFFF', dxfattribs={
        'name': 'TEST',
        'font': 'NOFONT.ttf',
        'width': 2.0,
    })
    assert 'TEST' == style.dxf.name


def test_appid_name():
    appid = AppID.new('FFFF', dxfattribs={
        'name': 'EZDXF',
    })
    assert 'EZDXF' == appid.dxf.name


@pytest.fixture
def ucs():
    return UCS.new('FFFF', dxfattribs={
        'name': 'UCS+90',
        'origin': (1.0, 1.0, 1.0),
        'xaxis': (0.0, 1.0, 0.0),
        'yaxis': (-1.0, 0.0, 0.0),
    })


def test_ucs_name(ucs):
    assert 'UCS+90' == ucs.dxf.name


def test_ucs_origin(ucs):
    assert (1.0, 1.0, 1.0) == ucs.dxf.origin


def test_viewport_name():
    vport = VPort.new('FFFF', dxfattribs={
        'name': 'VP1',
    })
    assert 'VP1' == vport.dxf.name


@pytest.fixture
def view():
    return View.new('FFFF', dxfattribs={
        'name': 'VIEW1',
        'flags': 0,
        'height': 1.0,
        'width': 1.0,
        'center_point': (0, 0),
        'direction_point': (0, 0, 0),
        'target_point': (0, 0, 0),
        'lens_length': 1.0,
        'front_clipping': 0.0,
        'back_clipping': 0.0,
        'view_twist': 0.0,
        'view_mode': 0,
    })


def test_view_name(view):
    assert 'VIEW1' == view.dxf.name


@pytest.fixture
def dimstyle():
    return DimStyle.new('FFFF', dxfattribs={
        'name': 'DIMSTYLE1',
    })


def test_dimstyle_name(dimstyle):
    assert 'DIMSTYLE1' == dimstyle.dxf.name


def test_dimstyle_handle_code(dimstyle):
    handle = dimstyle.tags.noclass.get_first_value(105)
    assert 'FFFF' == handle


def test_block_record_name():
    blockrec = BlockRecord.new('FFFF', dxfattribs={
        'name': 'BLOCKREC1',
    })
    assert 'BLOCKREC1' == blockrec.dxf.name


