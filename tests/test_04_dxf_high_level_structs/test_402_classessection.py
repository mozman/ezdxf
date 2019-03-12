# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
from io import StringIO
import ezdxf
from ezdxf.lldxf.tags import internal_tag_compiler
from ezdxf.sections.classes import ClassesSection
from ezdxf.lldxf.tagwriter import TagWriter
from ezdxf.tools.test import load_section
from ezdxf.drawing import Drawing


@pytest.fixture(scope='module')
def section():
    doc = Drawing()
    sec = load_section(TESTCLASSES, 'CLASSES')
    cls_entities = [doc.dxffactory.entity(e) for e in sec]
    return ClassesSection(None, iter(cls_entities))


def test_write(section):
    stream = StringIO()
    section.export_dxf(TagWriter(stream))
    result = stream.getvalue()
    stream.close()
    t1 = list(internal_tag_compiler(TESTCLASSES))
    t2 = list(internal_tag_compiler(result))
    assert t1 == t2


def test_empty_section():
    doc = Drawing()
    sec = load_section(EMPTYSEC, 'CLASSES')
    cls_entities = [doc.dxffactory.entity(e) for e in sec]

    section = ClassesSection(None, iter(cls_entities))
    stream = StringIO()
    section.export_dxf(TagWriter(stream))
    result = stream.getvalue()
    stream.close()
    assert EMPTYSEC == result


def test_count_class_instances():
    def instance_count(name):
        return doc.classes.get(name).dxf.instance_count
    doc = ezdxf.new('R2004')

    doc.classes.add_class('IMAGE')
    doc.classes.add_class('IMAGEDEF')
    doc.classes.add_class('IMAGEDEF_REACTOR')
    doc.classes.add_class('RASTERVARIABLES')

    doc.classes.update_instance_counters()
    assert instance_count('IMAGE') == 0
    assert instance_count('IMAGEDEF') == 0
    assert instance_count('IMAGEDEF_REACTOR') == 0
    assert instance_count('RASTERVARIABLES') == 0

    image_def = doc.add_image_def('test', size_in_pixel=(400, 400))
    msp = doc.modelspace()
    msp.add_image(image_def, insert=(0, 0), size_in_units=(10, 10))

    doc.classes.update_instance_counters()
    assert instance_count('IMAGE') == 1
    assert instance_count('IMAGEDEF') == 1
    assert instance_count('IMAGEDEF_REACTOR') == 1
    assert instance_count('RASTERVARIABLES') == 1


EMPTYSEC = """  0
SECTION
  2
CLASSES
  0
ENDSEC
"""

TESTCLASSES = """  0
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
"""
