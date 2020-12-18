# Copyright (C) 2011-2020, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.entities.ltype import Linetype, compile_line_pattern


@pytest.fixture
def linetype():
    ltype = Linetype.new('FFFF', dxfattribs={
        'name': 'TEST',
        'description': 'TESTDESC',
    })
    ltype.setup_pattern([0.2, 0.1, -0.1])
    return ltype


def test_name(linetype):
    assert linetype.dxf.name == 'TEST'


def test_description(linetype):
    assert linetype.dxf.description == 'TESTDESC'


def test_pattern_items_count(linetype):
    assert isinstance(linetype, Linetype)
    assert len(linetype.pattern_tags) == 7
    assert linetype.pattern_tags.is_complex_type() is False


def test_pattern_tags_details(linetype):
    # pattern tags are accessible but these are implementation details !!!
    assert linetype.pattern_tags.tags[0] == (72, 65)
    assert linetype.pattern_tags.tags[2].value == .2


def test_complex_linetype_name():
    complex_ltype = Linetype.new('FFFF', dxfattribs={
        'name': 'GASLEITUNG',
        'description': 'Gasleitung ----GAS----GAS----GAS----GAS----GAS----GAS--',
    })
    complex_ltype.setup_pattern('A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25', 3.0)
    assert complex_ltype.dxf.name == 'GASLEITUNG'
    assert complex_ltype.dxf.description == 'Gasleitung ----GAS----GAS----GAS----GAS----GAS----GAS--'
    tags = complex_ltype.pattern_tags.tags
    assert len(tags) == 16
    assert tags.get_first_value(340) == '0', "Default handle without DXF document"


def test_compile_pattern():
    assert compile_line_pattern(0, [0.0]) == tuple()
    assert compile_line_pattern(2.0, [1.25, -0.25, 0.25, -0.25]) == (
        1.25, 0.25, 0.25, 0.25)
    assert compile_line_pattern(3.5, [2.5, -0.25, 0.5, -0.25]) == (
        2.5, 0.25, 0.5, 0.25)
    assert compile_line_pattern(1.4, [1.0, -0.2, 0.0, -0.2]) == (
        1.0, 0.2, 0.0, 0.2)
    assert compile_line_pattern(0.2, [0.0, -0.2]) == (0.0, 0.2)
    assert compile_line_pattern(2.6, [2.0, -0.2, 0.0, -0.2, 0.0, -0.2]) == (
        2.0, 0.2, 0.0, 0.2, 0.0, 0.2)
