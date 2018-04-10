# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def dwg():
    return ezdxf.new('R2000')


def test_new_extension_dict(dwg):
    msp = dwg.modelspace()
    entity = msp.add_line((0, 0), (10, 0))
    with pytest.raises(ezdxf.DXFValueError):
        entity.get_extension_dict()

    xdict = entity.new_extension_dict()
    assert xdict.dxftype() == 'DICTIONARY'
    assert xdict.dxf.owner == entity.dxf.handle
    assert entity.has_app_data('{ACAD_XDICTIONARY')
    assert entity.has_extension_dict() is True

    xdict2 = entity.get_extension_dict()
    assert xdict.dxf.handle == xdict2.dxf.handle


def test_del_entity_with_ext_dict(dwg):
    msp = dwg.modelspace()
    entity = msp.add_line((0, 0), (10, 0))
    xdict = entity.new_extension_dict()
    xdict_handle = xdict.dxf.handle
    objects = dwg.objects
    assert xdict_handle in objects
    msp.delete_entity(entity)
    assert xdict_handle not in objects

