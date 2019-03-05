# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf.sections.classes2 import ClassesSection
from ezdxf.entities.dxfclass import DXFClass
from ezdxf.lldxf.tagwriter import TagCollector
from ezdxf.tools.test import load_entities


def test_init():
    classes = ClassesSection()
    assert len(classes.classes) == 0


def test_add_known_class():
    classes = ClassesSection()
    classes.add_class('SUN')
    assert len(classes.classes) == 1


def test_add_required_classes():
    classes = ClassesSection()
    classes.add_required_classes(ezdxf.DXF2004)
    assert len(classes.classes) > 10  # may change


def test_double_keys():
    classes = ClassesSection()
    sun1 = DXFClass()
    sun1.update_dxf_attribs({
        'name': 'SUN',
        'cpp_class_name': 'AcDbSun1'
    })

    sun2 = DXFClass()
    sun2.update_dxf_attribs({
        'name': 'SUN',
        'cpp_class_name': 'AcDbSun2'
    })
    # same class 'name' but different 'cpp class name', example: 'CADKitSamples/AEC Plan Elev Sample.dxf'
    classes.register([sun1, sun2])
    assert len(classes.classes) == 2


def test_export_dxf():
    classes = ClassesSection()
    classes.add_class('SUN')
    collector = TagCollector(dxfversion=ezdxf.DXF2004)
    classes.export_dxf(collector)
    tags = collector.tags
    assert tags[0] == (0, 'SECTION')
    assert tags[1] == (2, 'CLASSES')
    assert tags[2] == (0, 'CLASS')
    # writing classes is tested in 'test_113_dxfclass.py'
    assert tags[-1] == (0, 'ENDSEC')


def test_load_section():
    doc = ezdxf.new2()
    entities = load_entities(TEST_CLASSES, 'CLASSES', doc)
    classes = ClassesSection(doc, entities)
    assert len(classes.classes) == 3

    # this tests internals - use storage key is not exposed by API
    assert ('ACDBDICTIONARYWDFLT', 'AcDbDictionaryWithDefault') in classes.classes
    assert ('DICTIONARYVAR', 'AcDbDictionaryVar') in classes.classes
    assert ('TABLESTYLE', 'AcDbTableStyle') in classes.classes


TEST_CLASSES = """  0
SECTION
  2
CLASSES
  0
CLASS
  1
ACDBDICTIONARYWDFLT
  2
AcDbDictionaryWithDefault
  3
ObjectDBX Classes
 90
0
 91
1
280
0
281
0
  0
CLASS
  1
DICTIONARYVAR
  2
AcDbDictionaryVar
  3
ObjectDBX Classes
 90
0
 91
13
280
0
281
0
  0
CLASS
  1
TABLESTYLE
  2
AcDbTableStyle
  3
ObjectDBX Classes
 90
4095
 91
1
280
0
281
0
  0
ENDSEC
  0
EOF
"""
