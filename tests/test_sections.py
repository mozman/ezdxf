# Created: 12.03.2011, , 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest

from ezdxf.lldxf.tagger import internal_tag_compiler
from ezdxf.tools.test import DrawingProxy
from ezdxf.sections.sections import Sections, loader
from ezdxf.lldxf.const import DXFStructureError


@pytest.fixture
def sections():
    dwg = DrawingProxy('AC1009')
    return Sections(internal_tag_compiler(TEST_HEADER), dwg)


def test_constructor(sections):
    header = sections.header
    assert header is not None


def test_getattr_lower_case(sections):
    result = sections.header
    assert result is not None


def test_getattr_upper_case(sections):
    result = sections.HEADER
    assert result is not None


def test_error_getitem(sections):
    with pytest.raises(DXFStructureError):
        sections.testx


def test_error_getattr(sections):
    with pytest.raises(DXFStructureError):
        sections.testx


def test_loader():
    sections = loader(internal_tag_compiler(TEST_HEADER))
    assert len(sections) == 3
    header = sections['HEADER']
    assert len(header) == 1  # header section has always only one entity
    header_entity = header[0]
    assert header_entity[0] == (0, 'SECTION')
    assert header_entity[1] == (2, 'HEADER')
    assert header_entity[2] == (9, '$ACADVER')
    assert header_entity[-1] == (3, 'ANSI_1252')

    tables = sections['TABLES']
    assert len(tables) == 1
    tables_header = tables[0]
    assert tables_header[0] == (0, 'SECTION')
    assert tables_header[1] == (2, 'TABLES')

    entities = sections['ENTITIES']
    assert len(entities) == 1
    entities_header = entities[0]
    assert entities_header[0] == (0, 'SECTION')
    assert entities_header[1] == (2, 'ENTITIES')


def test_error_section():
    with pytest.raises(DXFStructureError):
        loader(internal_tag_compiler(SECTION_INVALID_NAME_TAG))

    with pytest.raises(DXFStructureError):
        loader(internal_tag_compiler(SECTION_NO_NAME_TAG))


TEST_HEADER = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1018
  9
$DWGCODEPAGE
  3
ANSI_1252
  0
ENDSEC
  0
SECTION
  2
TABLES
  0
ENDSEC
  0
SECTION
  2
ENTITIES
  0
ENDSEC
  0
EOF
"""

SECTION_INVALID_NAME_TAG = """  0
SECTION
  3
HEADER
  0
ENDSEC
"""

SECTION_NO_NAME_TAG = """  0
SECTION
  0
ENDSEC
"""
