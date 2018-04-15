# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2000')


def test_generic_dimassoc(dwg):
    dimassoc = dwg.objects.create_new_dxf_entity('DIMASSOC', {})
    assert dimassoc.dxftype() == 'DIMASSOC'
    assert dimassoc.dxf.object_id == '0'
    assert dimassoc.dxf_attrib_exists('intersect_id') is False




