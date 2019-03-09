# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest

from ezdxf.entities.underlay import PdfDefinition, DgnDefinition, DwfDefinition
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

PDFDEFINITION = """0
PDFDEFINITION
5
0
330
0
100
AcDbUnderlayDefinition
1
doc.pdf
2
1
"""


@pytest.fixture
def entity():
    return PdfDefinition.from_text(PDFDEFINITION)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'PDFDEFINITION' in ENTITY_CLASSES


def test_default_init():
    entity = PdfDefinition()
    assert entity.dxftype() == 'PDFDEFINITION'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = PdfDefinition.new(handle='ABBA', owner='0', dxfattribs={
        'filename': 'doc.pdf',
        'name': '1',
    })
    assert entity.dxf.filename == 'doc.pdf'
    assert entity.dxf.name == '1'


def test_load_from_text(entity):
    assert entity.dxf.filename == 'doc.pdf'
    assert entity.dxf.name == '1'


def test_write_dxf():
    entity = PdfDefinition.from_text(PDFDEFINITION)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(PDFDEFINITION)
    assert result == expected


def test_dwf_definition():
    assert DwfDefinition.DXFTYPE == 'DWFDEFINITION'


def test_dgn_definition():
    assert DgnDefinition.DXFTYPE == 'DGNDEFINITION'
