# Copyright (c) 2011-2021, Manfred Moitzi
# License: MIT License
import pytest

import ezdxf
from ezdxf.tools.test import load_entities
from ezdxf.sections.table import Table, AppIDTable
from ezdxf.lldxf.tagwriter import TagCollector


@pytest.fixture(scope="module")
def table():
    doc = ezdxf.new()
    return doc.appids


def test_table_entry_dxf_type(table):
    assert table.TABLE_TYPE == "APPID"


def test_ac1009_load_table():
    doc = ezdxf.new("R12")
    entities = list(load_entities(AC1009TABLE, "TABLES"))
    table = AppIDTable()
    table.load(doc, iter(entities[1:-1]))  # without SECTION tags and ENDTAB
    assert len(table) == 10


def test_load_table_with_invalid_table_entry():
    """This LAYERS table has an invalid APPID table entry, which should be
    ignored at the loading stage.
    """
    doc = ezdxf.new("R12")
    entities = list(load_entities(INVALID_TABLE_ENTRY, "TABLES"))
    table = Table()
    table.load(doc, iter(entities[1:-1]))  # without SECTION tags and ENDTAB
    assert len(table) == 0


def test_ac1009_write(table):
    collector = TagCollector(dxfversion="AC1009")
    table.export_dxf(collector)
    tags = collector.tags
    assert tags[0] == (0, "TABLE")
    assert tags[1] == (2, "APPID")
    # exporting table entries is tested by associated class tests
    assert tags[-1] == (0, "ENDTAB")


def test_ac1024_load_table():
    doc = ezdxf.new("R2010")
    entities = list(load_entities(AC1024TABLE, "TABLES"))
    table = AppIDTable()
    table.load(doc, iter(entities[1:-1]))  # without SECTION tags and ENDTAB
    assert 10 == len(table)


def test_ac1024_write(table):
    collector = TagCollector(dxfversion="R2004")
    table.export_dxf(collector)
    tags = collector.tags
    assert tags[0] == (0, "TABLE")
    assert tags[1] == (2, "APPID")
    # exporting table entries is tested by associated class tests
    assert tags[-1] == (0, "ENDTAB")


def test_get_table_entry(table):
    entry = table.get("ACAD")
    assert "ACAD" == entry.dxf.name


def test_entry_names_are_case_insensitive(table):
    entry = table.get("acad")
    assert "ACAD" == entry.dxf.name


def test_duplicate_entry(table):
    new_entry = table.duplicate_entry("ACAD", "ACAD2018")
    assert new_entry.dxf.name == "ACAD2018"

    entry2 = table.get("ACAD2018")
    assert new_entry.dxf.handle == entry2.dxf.handle

    new_entry2 = table.duplicate_entry("ACAD2018", "ACAD2019")
    new_entry.dxf.flags = 71
    new_entry2.dxf.flags = 17
    # really different entities
    assert new_entry.dxf.flags == 71
    assert new_entry2.dxf.flags == 17


def test_create_vport_table():
    doc = ezdxf.new()
    assert len(doc.viewports) == 1
    # standard viewport exists
    assert "*Active" in doc.viewports

    # create a multi-viewport configuration
    # create two entries with same name
    vp1 = doc.viewports.new("V1")
    vp2 = doc.viewports.new("V1")
    assert len(doc.viewports) == 3

    # get multi-viewport configuration as list
    conf = doc.viewports.get_config("V1")
    assert len(conf) == 2

    # check handles
    vports = [vp1, vp2]
    assert conf[0] in vports
    assert conf[1] in vports

    assert "Test" not in doc.viewports
    with pytest.raises(ezdxf.DXFTableEntryError):
        _ = doc.viewports.get_config("test")

    # delete: ignore not existing configurations
    with pytest.raises(ezdxf.DXFTableEntryError):
        doc.viewports.delete_config("test")

    # delete multi config
    doc.viewports.delete_config("V1")
    assert len(doc.viewports) == 1


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

INVALID_TABLE_ENTRY = """0
SECTION
2
TABLES
0
TABLE
2
LAYERS
70
10
0
APPID
2
ACAD
70
0
0
ENDTAB
0
ENDSEC
"""
