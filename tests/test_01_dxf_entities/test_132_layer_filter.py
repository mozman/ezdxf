# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
from typing import cast
import pytest
import ezdxf
from ezdxf.entities.idbuffer import LayerFilter
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

LAYERFILTER = """0
LAYER_FILTER
5
0
102
{ACAD_REACTORS
330
0
102
}
330
0
100
AcDbFilter
100
AcDbLayerFilter
"""


@pytest.fixture
def entity():
    return LayerFilter.from_text(LAYERFILTER)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'LAYER_FILTER' in ENTITY_CLASSES


def test_default_init():
    entity = LayerFilter()
    assert entity.dxftype() == 'LAYER_FILTER'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = LayerFilter.new(handle='ABBA', owner='0', dxfattribs={
    })
    assert len(entity.handles) == 0


def test_load_from_text(entity):
    assert len(entity.handles) == 0


def test_write_dxf():
    entity = LayerFilter.from_text(LAYERFILTER)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(LAYERFILTER)
    assert result == expected


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new2('R2007')


def test_generic_field_list(doc):
    layers = doc.objects.new_entity('LAYER_FILTER', {})
    assert layers.dxftype() == 'LAYER_FILTER'
    assert len(layers.handles) == 0


def test_set_get_field_list(doc):
    field_list = doc.objects.new_entity('LAYER_FILTER', {})
    assert field_list.dxftype() == 'LAYER_FILTER'
    field_list.handles = ['FF', 'EE', 'DD']
    handles = field_list.handles
    assert len(handles) == 3
    assert handles == ['FF', 'EE', 'DD']

    handles.append('FFFF')
    assert handles[-1] == 'FFFF'


def test_dxf_tags(doc):
    buffer = cast(LayerFilter, doc.objects.new_entity('LAYER_FILTER', {}))
    buffer.handles = ['FF', 'EE', 'DD', 'CC']
    tags = TagCollector.dxftags(buffer)[-4:]

    assert len(tags) == 4
    assert tags[0] == (330, 'FF')
    assert tags[-1] == (330, 'CC')


def test_clone(doc):
    layers = cast(LayerFilter, doc.objects.new_entity('LAYER_FILTER', {}))
    layers.handles = ['FF', 'EE', 'DD', 'CC']
    layers2 = cast(LayerFilter, layers.copy())
    layers2.handles[-1] = 'ABCD'
    assert layers.handles[:-1] == layers2.handles[:-1]
    assert layers.handles[-1] != layers2.handles[-1]
