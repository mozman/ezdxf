# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import pytest
from copy import deepcopy
from ezdxf.entities.dxfentity import base_class, DXFAttributes, DXFNamespace, SubclassProcessor
from ezdxf.entities.dxfgfx import acdb_entity
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.const import DXFAttributeError
from ezdxf.lldxf.tagwriter import TagCollector


class DXFEntity:
    """ Mockup """
    DXFTYPE = 'DXFENTITY'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity)


@pytest.fixture
def entity():
    return DXFEntity()


@pytest.fixture
def processor():
    return SubclassProcessor(ExtendedTags.from_text(TEST_1))


def test_handle_and_owner(entity, processor):
    attribs = DXFNamespace(processor, entity)
    assert attribs.handle == 'FFFF'
    assert attribs.owner == 'ABBA'
    assert attribs._entity is entity


def test_default_values(entity, processor):
    attribs = DXFNamespace(processor, entity)
    assert attribs.layer == '0'
    assert attribs.color == 256
    assert attribs.linetype == 'BYLAYER'
    # this attributes do not really exist
    assert attribs.hasattr('layer') is False
    assert attribs.hasattr('color') is False
    assert attribs.hasattr('linetype') is False


def test_get_value_with_default(entity, processor):
    attribs = DXFNamespace(processor, entity)
    # return existing values
    assert attribs.get('handle', '0') == 'FFFF'
    # return given default value not DXF default value, which would be '0'
    assert attribs.get('layer', 'mozman') == 'mozman'
    # attribute has to a valid DXF attribute
    with pytest.raises(DXFAttributeError):
        _ = attribs.get('hallo', 0)

    # attribs without default raises DXFAttributeError
    with pytest.raises(DXFAttributeError):
        _ = attribs.color_name


def test_set_values(entity, processor):
    attribs = DXFNamespace(processor, entity)
    attribs.handle = 'CDEF'
    assert attribs.handle == 'CDEF'
    attribs.set('owner', 'DADA')
    assert attribs.owner == 'DADA'
    # set new attribute
    attribs.color = 7
    assert attribs.color == 7
    attribs.set('linetype', 'DOT')
    assert attribs.linetype == 'DOT'
    # attribute has to a valid DXF attribute
    with pytest.raises(DXFAttributeError):
        attribs.hallo = 0
    with pytest.raises(DXFAttributeError):
        attribs.set('hallo', 0)


def test_delete_attribs(entity, processor):
    attribs = DXFNamespace(processor, entity)
    attribs.layer = 'mozman'
    assert attribs.layer == 'mozman'
    del attribs.layer

    # default value
    assert attribs.layer == '0'
    with pytest.raises(DXFAttributeError):
        del attribs.color
    attribs.discard('color')  # delete silently if not exists
    with pytest.raises(DXFAttributeError):
        del attribs.color


def test_is_supported(entity, processor):
    attribs = DXFNamespace(processor, entity)
    assert attribs.is_supported('linetype') is True
    assert attribs.is_supported('true_color') is True  # ezdxf does not care about DXF versions at runtime
    assert attribs.is_supported('xxx_mozman_xxx') is False


def test_dxftype(entity, processor):
    attribs = DXFNamespace(processor, entity)
    assert attribs.dxftype == 'DXFENTITY'


def test_cloning(entity, processor):
    attribs = DXFNamespace(processor, entity)
    attribs.color = 77
    attribs2 = attribs.clone()
    # clone everything except _entity, handle, owner
    assert attribs2._entity is None
    assert attribs2.handle is None
    assert attribs2.owner is None
    assert attribs2.color == 77
    # do not harm original entity
    assert attribs._entity is entity
    assert attribs.handle == 'FFFF'
    assert attribs.owner == 'ABBA'


def test_prevent_deepcopy_usage(entity, processor):
    attribs = DXFNamespace(processor, entity)
    with pytest.raises(NotImplementedError):
        _ = deepcopy(attribs)


def test_dxf_export_one_attribute(entity, processor):
    attribs = DXFNamespace(processor, entity)
    tagwriter = TagCollector()
    attribs.export_dxf_attribute(tagwriter, 'handle')
    assert len(tagwriter.tags) == 1
    assert tagwriter.tags[0] == (5, 'FFFF')
    with pytest.raises(DXFAttributeError):
        attribs.export_dxf_attribute(tagwriter, 'mozman')


def test_dxf_export_two_attribute(entity, processor):
    attribs = DXFNamespace(processor, entity)
    tagwriter = TagCollector()
    attribs.export_dxf_attribs(tagwriter, ['handle', 'owner'])
    assert len(tagwriter.tags) == 2
    assert tagwriter.tags[0] == (5, 'FFFF')
    assert tagwriter.tags[1] == (330, 'ABBA')


TEST_1 = """0
DXFENTITY
5
FFFF
330
ABBA
"""

if __name__ == '__main__':
    pytest.main([__file__])

