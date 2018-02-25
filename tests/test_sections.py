# Created: 12.03.2011, , 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest

import ezdxf
from ezdxf.lldxf.tagger import internal_tag_compiler
from ezdxf.lldxf.loader import load_dxf_structure
from ezdxf.sections import Sections
from ezdxf.lldxf.const import DXFStructureError


@pytest.fixture(scope='module')
def sections():
    dwg = ezdxf.new('R12')
    return Sections(load_dxf_structure(internal_tag_compiler(TEST_HEADER)), dwg)


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
