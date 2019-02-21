# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
from io import StringIO

import ezdxf
from ezdxf.tools.test import compile_tags_without_handles, load_section, internal_tag_compiler
from ezdxf.sections.table import Table
from ezdxf.lldxf.tagwriter import TagWriter


@pytest.fixture(scope='module')
def table_ac1009():
    dwg = ezdxf.new('R12')
    entities = load_section(AC1009TABLE, 'TABLES', dwg.entitydb)
    return Table(entities[1:-1], dwg)  # without SECTION tags and ENDTAB


def test_ac1009_table_setup(table_ac1009):
    assert 10 == len(table_ac1009)


def test_ac1009_write(table_ac1009):
    stream = StringIO()
    table_ac1009.write(TagWriter(stream))
    result = stream.getvalue()
    stream.close()
    t1 = list(compile_tags_without_handles(AC1009TABLE))[2:-1]   # without section tags
    t2 = list(compile_tags_without_handles(result))
    assert t1 == t2


def test_ac1009_get_table_entry(table_ac1009):
    entry = table_ac1009.get('ACAD')
    assert 'ACAD' == entry.dxf.name


def test_ac1009_entry_names_are_case_insensitive(table_ac1009):
    entry = table_ac1009.get('acad')
    assert 'ACAD' == entry.dxf.name


def test_ac1009_duplicate_entry(table_ac1009):
    new_entry = table_ac1009.duplicate_entry('ACAD', 'ACAD2018')
    assert new_entry.dxf.name == 'ACAD2018'

    entry2 = table_ac1009.get('ACAD2018')
    assert new_entry.dxf.handle == entry2.dxf.handle

    new_entry2 = table_ac1009.duplicate_entry('ACAD2018', 'ACAD2019')
    new_entry.dxf.flags = 71
    new_entry2.dxf.flags = 17
    # really different entities
    assert new_entry.dxf.flags == 71
    assert new_entry2.dxf.flags == 17


@pytest.fixture(scope='module')
def table_ac1024():
    dwg = ezdxf.new('R2010')
    entities = load_section(AC1024TABLE, 'TABLES', dwg.entitydb)
    return Table(entities[1:-1], dwg)  # without SECTION tags and ENDTAB


def test_ac1024table_setup(table_ac1024):
    assert 10 == len(table_ac1024)


def test_ac1024_write(table_ac1024):
    stream = StringIO()
    table_ac1024.write(TagWriter(stream))
    result = stream.getvalue()
    stream.close()
    t1 = list(internal_tag_compiler(AC1024TABLE))[2:-1]  # without section tags
    t2 = list(internal_tag_compiler(result))
    assert t1 == t2


def test_ac1024_get_table_entry(table_ac1024):
    entry = table_ac1024.get('ACAD')
    assert 'ACAD' == entry.dxf.name


AC1009TABLE = """0
SECTION
2
TABLES
  0
TABLE
  2
APPID
 70
    10
  0
APPID
  2
ACAD
 70
     0
  0
APPID
  2
ACADANNOPO
 70
     0
  0
APPID
  2
ACADANNOTATIVE
 70
     0
  0
APPID
  2
ACAD_DSTYLE_DIMJAG
 70
     0
  0
APPID
  2
ACAD_DSTYLE_DIMTALN
 70
     0
  0
APPID
  2
ACAD_MLEADERVER
 70
     0
  0
APPID
  2
ACAECLAYERSTANDARD
 70
     0
  0
APPID
  2
ACAD_EXEMPT_FROM_CAD_STANDARDS
 70
     0
  0
APPID
  2
ACAD_DSTYLE_DIMBREAK
 70
     0
  0
APPID
  2
ACAD_PSEXT
 70
     0
  0
ENDTAB
  0
ENDSEC
"""

AC1024TABLE = """  0
SECTION
2
TABLES
0
TABLE
  2
APPID
  5
9
330
0
100
AcDbSymbolTable
 70
    10
  0
APPID
  5
12
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
ACAD
 70
     0
  0
APPID
  5
DD
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
AcadAnnoPO
 70
     0
  0
APPID
  5
DE
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
AcadAnnotative
 70
     0
  0
APPID
  5
DF
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
ACAD_DSTYLE_DIMJAG
 70
     0
  0
APPID
  5
E0
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
ACAD_DSTYLE_DIMTALN
 70
     0
  0
APPID
  5
107
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
ACAD_MLEADERVER
 70
     0
  0
APPID
  5
1B5
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
AcAecLayerStandard
 70
     0
  0
APPID
  5
1BA
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
ACAD_EXEMPT_FROM_CAD_STANDARDS
 70
     0
  0
APPID
  5
237
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
ACAD_DSTYLE_DIMBREAK
 70
     0
  0
APPID
  5
28E
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
ACAD_PSEXT
 70
     0
  0
ENDTAB
  0
ENDSEC
"""


