# Copyright (c) 2014-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf

from ezdxf.entities.acis import tags2textlines, textlines2tags


@pytest.fixture(scope='module')
def layout():
    doc = ezdxf.new('R2007')
    return doc.modelspace()


def test_body_default_settings(layout):
    body = layout.add_body()
    assert '0' == body.dxf.layer


def test_body_getting_acis_data(layout):
    body = layout.add_body(acis_data=TEST_DATA.splitlines())
    assert TEST_DATA == body.tostring()


def test_backward_compatibility(layout):
    body = layout.add_body()
    with body.edit_data() as data:
        data.text_lines.extend(TEST_DATA.splitlines())

    assert TEST_DATA == "\n".join(body.get_acis_data())
    body.set_acis_data(TEST_DATA.splitlines())
    assert TEST_DATA == body.tostring()


def test_region_default_settings(layout):
    region = layout.add_region()
    assert region.dxf.layer == '0'


def test_region_getting_acis_data(layout):
    region = layout.add_region(acis_data=TEST_DATA.splitlines())
    assert TEST_DATA == region.tostring()


def test_3dsolid_default_settings(layout):
    _3dsolid = layout.add_3dsolid()
    assert _3dsolid.dxf.layer == '0'
    assert _3dsolid.dxf.history_handle == '0'


def test_3dsolid_getting_acis_data(layout):
    _3dsolid = layout.add_3dsolid(acis_data=TEST_DATA.splitlines())
    assert TEST_DATA == _3dsolid.tostring()


TEST_DATA = """21200 115 2 26
16 Autodesk AutoCAD 19 ASM 217.0.0.4503 NT 0
1 9.9999999999999995e-007 1e-010
asmheader $-1 -1 @12 217.0.0.4503 #
body $2 -1 $-1 $3 $-1 $-1 #
ref_vt-eye-attrib $-1 -1 $-1 $-1 $1 $4 $5 #
lump $6 -1 $-1 $-1 $7 $1 #
eye_refinement $-1 -1 @5 grid  1 @3 tri 1 @4 surf 0 @3 adj 0 @4 grad 0 @9 postcheck 0 @4 stol 0.020115179941058159 @4 ntol 30 @4 dsil 0 @8 flatness 0 @7 pixarea 0 @4 hmax 0 @6 gridar 0 @5 mgrid 3000 @5 ugrid 0 @5 vgrid 0 @10 end_fields #
vertex_template $-1 -1 3 0 1 8 #"""


def test_tag2lines():
    expected = 'AB' * 50 + 'CD' * 50 + 'EF' * 50
    tags = [
        (1, 'AB' * 50),
        (3, 'CD' * 50),
        (3, 'EF' * 50),
    ]
    assert list(tags2textlines(tags))[0] == expected


def test_lines2tags():
    line = 'AB' * 100 + 'CD' * 100 + 'EF' * 100
    result = list(textlines2tags([line]))
    code, value = result[0]
    assert code == 1
    assert value == line[:255]
    code, value = result[1]
    assert code == 3
    assert value == line[255:510]
    code, value = result[2]
    assert code == 3
    assert value == line[510:]
