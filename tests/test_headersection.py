# Purpose: test header section
# Created: 12.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
import ezdxf
from ezdxf.drawing import Drawing
from ezdxf.tools.test import DrawingProxy, Tags
from ezdxf.sections.header import HeaderSection
from ezdxf.lldxf.validator import header_validator


INVALID_HEADER_STRUCTURE = """   9
$ACADVER
  1
AC1009
  100
$INSBASE
 10
0.0
 20
0.0
 30
0.0
"""

INVALID_HEADER_VAR_NAME = """   9
$ACADVER
  1
AC1009
  9
INSBASE
 10
0.0
 20
0.0
 30
0.0
"""

MINIMALISTIC_DXF12 = """  0
SECTION
  2
ENTITIES
  0
ENDSEC
  0
EOF
"""


def test_new_drawing():
    dwg = ezdxf.new('AC1009')
    assert 'AC1009' == dwg.dxfversion


def test_min_r12_drawing():
    tags = Tags.from_text(MINIMALISTIC_DXF12)
    return Drawing(tags)


def test_valid_header():
    tags = Tags.from_text(TESTHEADER)[2:-1]
    result = list(header_validator(tags))
    assert 8 == len(result)


def test_invalid_header_structure():
    tags = Tags.from_text(INVALID_HEADER_STRUCTURE)
    with pytest.raises(ezdxf.DXFStructureError):
        list(header_validator(tags))


def test_invalid_header_var_name():
    tags = Tags.from_text(INVALID_HEADER_VAR_NAME)
    with pytest.raises(ezdxf.DXFValueError):
        list(header_validator(tags))


@pytest.fixture
def header():
    tags = Tags.from_text(TESTHEADER)
    tags.pop()  # remove 'ENDSEC'
    dwg = DrawingProxy('AC1009')
    header = HeaderSection(tags)
    header.set_headervar_factory(dwg.dxffactory.headervar_factory)
    return header


def test_get_acadver(header):
    result = header['$ACADVER']
    assert 'AC1009' == result


def test_get_insbase(header):
    result = header['$INSBASE']
    assert (0., 0., 0.) == result


def test_getitem_keyerror(header):
    with pytest.raises(ezdxf.DXFKeyError):
        var = header['$TEST']


def test_get(header):
    result = header.get('$TEST', 'TEST')
    assert 'TEST' == result


def test_set_existing_var(header):
    header['$ACADVER'] = 'AC666'
    assert 'AC666' == header['$ACADVER']


def test_set_existing_point(header):
    header['$INSBASE'] = (1, 2, 3)
    assert (1, 2, 3) == header['$INSBASE']


def test_set_unknown_var(header):
    with pytest.raises(ezdxf.DXFKeyError):
        header['$TEST'] = 'test'


def test_create_var(header):
    header['$LIMMAX'] = (10, 20)
    assert (10, 20) == header['$LIMMAX']


def test_create_var_wrong_args_2d(header):
    header['$LIMMAX'] = (10, 20, 30)
    assert (10, 20) == header['$LIMMAX']


def test_create_var_wrong_args_3d(header):
    with pytest.raises(ezdxf.DXFValueError):
        header['$PUCSORG'] = (10, 20)


def test_contains(header):
    assert '$ACADVER' in header


def test_not_contains(header):
    assert '$MOZMAN' not in header


def test_remove_headervar(header):
    del header['$ACADVER']
    assert '$ACADVER' not in header


def test_str_point(header):
    insbase_str = str(header.hdrvars['$INSBASE'])
    assert INSBASE == insbase_str


@pytest.fixture
def header_custom():
    tags = Tags.from_text(TESTCUSTOMPROPERTIES)
    tags.pop()  # remove 'ENDSEC'
    dwg = DrawingProxy('AC1009')
    header = HeaderSection(tags)
    header.set_headervar_factory(dwg.dxffactory.headervar_factory)
    return header


def test_custom_properties_exists(header_custom):
    assert header_custom.custom_vars.has_tag("Custom Property 1")


def test_order_of_occurrence(header_custom):
    properties = header_custom.custom_vars.properties
    assert ("Custom Property 1", "Custom Value 1") == properties[0]
    assert ("Custom Property 2", "Custom Value 2") == properties[1]


def test_get_custom_property(header_custom):
    assert "Custom Value 1" == header_custom.custom_vars.get("Custom Property 1")


def test_get_custom_property_2(header_custom):
    assert "Custom Value 2" == header_custom.custom_vars.get("Custom Property 2")


def test_add_custom_property(header_custom):
    header_custom.custom_vars.append("Custom Property 3", "Custom Value 3")
    assert 3 == len(header_custom.custom_vars)
    assert "Custom Value 3" == header_custom.custom_vars.get("Custom Property 3")


def test_remove_custom_property(header_custom):
    header_custom.custom_vars.remove("Custom Property 1")
    assert 1 == len(header_custom.custom_vars)


def test_remove_not_existing_property(header_custom):
    with pytest.raises(ValueError):
        header_custom.custom_vars.remove("Does not Exist")


def test_replace_custom_property(header_custom):
    header_custom.custom_vars.replace("Custom Property 1", "new value")
    assert "new value" == header_custom.custom_vars.get("Custom Property 1")


def test_replace_not_existing_property(header_custom):
    with pytest.raises(ValueError):
        header_custom.custom_vars.replace("Does not Exist", "new value")


INSBASE = """ 10
0.0
 20
0.0
 30
0.0
"""

TESTHEADER = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1009
  9
$INSBASE
 10
0.0
 20
0.0
 30
0.0
  9
$EXTMIN
 10
1.0000000000000000E+020
 20
1.0000000000000000E+020
 30
1.0000000000000000E+020
  9
$EXTMAX
 10
-1.0000000000000000E+020
 20
-1.0000000000000000E+020
 30
-1.0000000000000000E+020
  0
ENDSEC
"""

TESTCUSTOMPROPERTIES = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1009
  9
$CUSTOMPROPERTYTAG
  1
Custom Property 1
  9
$CUSTOMPROPERTY
  1
Custom Value 1
  9
$CUSTOMPROPERTYTAG
  1
Custom Property 2
  9
$CUSTOMPROPERTY
  1
Custom Value 2
  0
ENDSEC
"""
