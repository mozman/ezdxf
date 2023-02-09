# Copyright (c) 2011-2021, Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf.tools.test import load_entities
from ezdxf.sections.objects import ObjectsSection
from ezdxf.entities import Point


def test_load_section():
    doc = ezdxf.new("R2000")
    ent = load_entities(TESTOBJECTS, "OBJECTS")

    section = ObjectsSection(doc, ent)
    assert len(section) == 6
    assert section[0].dxftype() == "DICTIONARY"


def test_auditor_removes_invalid_entities():
    doc = ezdxf.new()
    count = len(doc.objects)
    # hack hack hack!
    doc.objects._entity_space.add(Point())
    auditor = doc.audit()
    assert len(auditor.fixes) == 1
    assert len(doc.objects) == count, "should call purge() automatically"


TESTOBJECTS = """  0
SECTION
  2
OBJECTS
  0
DICTIONARY
  5
C
330
0
100
AcDbDictionary
281
     1
  3
ACAD_COLOR
350
73
  3
ACAD_GROUP
350
D
  3
ACAD_LAYOUT
350
1A
  3
ACAD_MATERIAL
350
72
  3
ACAD_MLEADERSTYLE
350
D7
  3
ACAD_MLINESTYLE
350
17
  3
ACAD_PLOTSETTINGS
350
19
  3
ACAD_PLOTSTYLENAME
350
E
  3
ACAD_SCALELIST
350
B6
  3
ACAD_TABLESTYLE
350
86
  3
ACAD_VISUALSTYLE
350
99
  3
ACDB_RECOMPOSE_DATA
350
499
  3
AcDbVariableDictionary
350
66
  0
DICTIONARY
  5
2A2
330
2
100
AcDbDictionary
280
     1
281
     1
  3
ACAD_LAYERSTATES
360
2A3
  0
DICTIONARY
  5
E6
330
10
100
AcDbDictionary
280
     1
281
     1
  0
DICTIONARY
  5
15D
330
1F
100
AcDbDictionary
280
     1
281
     1
  0
DICTIONARY
  5
28C
330
28B
100
AcDbDictionary
280
     1
281
     1
  3
ASDK_XREC_ANNOTATION_SCALE_INFO
360
28D
  0
DICTIONARY
  5
291
330
290
100
AcDbDictionary
280
     1
281
     1
  3
ASDK_XREC_ANNOTATION_SCALE_INFO
360
292
  0
ENDSEC
"""
