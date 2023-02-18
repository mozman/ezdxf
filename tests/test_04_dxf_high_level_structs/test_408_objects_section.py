# Copyright (c) 2011-2023, Manfred Moitzi
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


class TestAuditObjectSection:
    def test_auditor_removes_invalid_entities(self):
        doc = ezdxf.new()
        count = len(doc.objects)
        # hack hack hack!
        doc.objects._entity_space.add(Point())
        auditor = doc.audit()
        assert len(auditor.fixes) == 1
        assert len(doc.objects) == count, "should call purge() automatically"

    def test_audit_restores_deleted_owner_tag(self):
        doc = ezdxf.new()
        d = doc.rootdict.add_new_dict("TestMe")
        d.dxf.discard("owner")
        doc.audit()
        assert d.dxf.owner == doc.rootdict.dxf.handle, "expected rootdict as owner"

    def test_validate_known_dictionaries(self):
        doc = ezdxf.new()
        materials = doc.rootdict.get_required_dict("ACAD_MATERIAL")
        v1 = materials.add_dict_var("X", "VAR1")
        v2 = materials.add_dict_var("Y", "VAR2")
        assert len(doc.materials) == 5

        auditor = doc.audit()
        assert len(auditor.fixes) == 2
        assert len(doc.materials) == 3
        assert v1.is_alive is False
        assert v2.is_alive is False


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
