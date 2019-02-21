# Created: 25.01.2018
# Copyright (C) 2018-2019, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.lldxf.tagger import internal_tag_compiler
from ezdxf.lldxf.loader import load_dxf_structure
from ezdxf.lldxf.const import DXFStructureError


def test_loader():
    sections = load_dxf_structure(internal_tag_compiler(TEST_HEADER))
    assert len(sections) == 3
    header = sections['HEADER']
    assert len(header) == 1  # header load_section has always only one entity
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
        load_dxf_structure(internal_tag_compiler(SECTION_INVALID_NAME_TAG))

    with pytest.raises(DXFStructureError):
        load_dxf_structure(internal_tag_compiler(SECTION_NO_NAME_TAG))


def validator(text):
    tags = internal_tag_compiler(text)
    return load_dxf_structure(tags)


def test_valid_structure():
    sections = validator("  0\nSECTION\n 2\nHEADER\n  0\nENDSEC\n  0\nSECTION\n  2\nCLASSES\n  0\nENDSEC\n  0\nEOF\n")
    assert len(sections) == 2
    assert len(sections['HEADER']) == 1  # ENDSEC is not present
    assert len(sections['CLASSES']) == 1  # ENDSEC is not present


def test_eof_without_lineending():
    sections = validator("  0\nSECTION\n 2\nHEADER\n  0\nENDSEC\n  0\nSECTION\n  2\nCLASSES\n  0\nENDSEC\n  0\nEOF")
    assert len(sections) == 2
    assert len(sections['HEADER']) == 1  # ENDSEC is not present
    assert len(sections['CLASSES']) == 1  # ENDSEC is not present


def test_missing_eof():
    with pytest.raises(DXFStructureError):
        validator("999\ncomment")


def test_missing_endsec():
    with pytest.raises(DXFStructureError):
        validator("  0\nSECTION\n 2\nHEADER\n  0\nSECTION\n  2\nCLASSES\n  0\nENDSEC\n  0\nEOF\n")

    with pytest.raises(DXFStructureError):
        validator("  0\nSECTION\n 2\nHEADER\n  0\nSECTION\n  2\nCLASSES\n  0\nEOF\n")


def test_missing_endsec_and_eof():
    with pytest.raises(DXFStructureError):
        validator("  0\nSECTION\n 2\nHEADER\n  0\nENDSEC\n  0\nSECTION\n  2\nCLASSES\n")


def test_missing_section():
    with pytest.raises(DXFStructureError):
        validator("  0\nENDSEC\n  0\nSECTION\n  2\nCLASSES\n  0\nENDSEC\n  0\nEOF\n")


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
