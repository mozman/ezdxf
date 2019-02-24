# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created: 2019-02-18
import pytest

from ezdxf.drawing2 import Drawing
from ezdxf.sections.objects2 import _OBJECT_TABLE_NAMES


@pytest.fixture
def doc():
    return Drawing.new('r2018')


def test_create_new_empty_drawing(doc):
    assert doc.dxfversion == 'AC1032'
    rootdict = doc.rootdict
    assert rootdict.DXFTYPE == 'DICTIONARY'
    for name in _OBJECT_TABLE_NAMES:
        assert name in rootdict


def test_section(doc):
    assert doc.header['$ACADVER'] == 'AC1032'

    e = doc.objects.get_entity_space()
    assert e[0] is doc.rootdict

    assert len(doc.blocks) == 2
    assert '*Model_Space' in doc.blocks
    assert '*Paper_Space' in doc.blocks


def test_viewports(doc):
    assert len(doc.viewports) == 1
    # viewport table can have multiple entries with same name, therefor returns a list
    assert len(doc.viewports.get('*Active')) == 1

    assert len(doc.linetypes) == 3


def test_layers(doc):
    assert len(doc.layers) == 2
    assert '0' in doc.layers
    assert 'Defpoints' in doc.layers
    assert doc.layers.get('0').dxf.material_handle == doc.materials['Global'].dxf.handle
    assert doc.layers.get('0').dxf.plotstyle_handle == doc.plotstyles['Normal'].dxf.handle
    assert len(doc.views) == 0


def test_linetypes(doc):
    assert len(doc.linetypes) == 3
    assert 'ByLayer' in doc.linetypes
    assert 'ByBlock' in doc.linetypes
    assert 'Continuous' in doc.linetypes


def test_text_styles(doc):
    assert len(doc.styles) == 1
    assert 'Standard' in doc.styles


def test_dim_styles(doc):
    assert len(doc.dimstyles) == 1
    assert 'Standard' in doc.dimstyles


def test_views(doc):
    assert len(doc.views) == 0


def test_appids(doc):
    assert len(doc.appids) == 1


def test_ucs(doc):
    assert len(doc.ucs) == 0


def test_get_modelspace(doc):
    msp = doc.modelspace()
    assert len(msp) == 0
    msp.add_line((0, 0), (1, 1))
    assert len(msp) == 1


def test_get_paperspace(doc):
    psp = doc.layout()
    assert len(psp) == 0
    psp.add_line((0, 0), (1, 1))
    assert len(psp) == 1
