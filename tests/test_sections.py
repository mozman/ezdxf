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


def test_getattr(sections):
    result = sections.header
    assert result is not None


def test_error_getitem(sections):
    with pytest.raises(DXFStructureError):
        sections.test


def test_error_getattr(sections):
    with pytest.raises(DXFStructureError):
        sections.test


def test_loader():
    sections = loader(internal_tag_compiler(TEST_HEADER))
    assert len(sections) == 3
    header = sections[0]
    assert len(header) == 1  # header section has always only one entity
    header_entity = header[0]
    assert header_entity[0] == (0, 'SECTION')
    assert header_entity[1] == (2, 'HEADER')
    assert header_entity[2] == (9, '$ACADVER')
    assert header_entity[-1] == (3, 'ANSI_1252')

    tables = sections[1]
    assert len(tables) == 1
    tables_header = tables[0]
    assert tables_header[0] == (0, 'SECTION')
    assert tables_header[1] == (2, 'TABLES')

    entities = sections[2]
    assert len(entities) == 1
    entities_header = entities[0]
    assert entities_header[0] == (0, 'SECTION')
    assert entities_header[1] == (2, 'ENTITIES')


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
