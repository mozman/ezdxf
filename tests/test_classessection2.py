# Created: 15.03.2011
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
from io import StringIO
import ezdxf
from ezdxf.lldxf.tags import internal_tag_compiler
from ezdxf.sections.classes2 import ClassesSection
from ezdxf.lldxf.tagwriter import TagWriter
from ezdxf.tools.test import load_section
from ezdxf.drawing2 import Drawing2


@pytest.fixture(scope='module')
def section():
    doc = Drawing2()
    sec = load_section(TESTCLASSES, 'CLASSES')
    cls_entities = [doc.dxffactory.entity(e) for e in sec]
    return ClassesSection(iter(cls_entities), None)


def test_write(section):
    stream = StringIO()
    section.export_dxf(TagWriter(stream))
    result = stream.getvalue()
    stream.close()
    t1 = list(internal_tag_compiler(TESTCLASSES))
    t2 = list(internal_tag_compiler(result))
    assert t1 == t2


def test_empty_section():
    doc = Drawing2()
    sec = load_section(EMPTYSEC, 'CLASSES')
    cls_entities = [doc.dxffactory.entity(e) for e in sec]

    section = ClassesSection(iter(cls_entities), None)
    stream = StringIO()
    section.export_dxf(TagWriter(stream))
    result = stream.getvalue()
    stream.close()
    assert EMPTYSEC == result


def test_count_class_instances():
    def instance_count(name):
        return classes[name].dxf.instance_count
    pytest.skip('Need Drawing.new() support')
    dwg = ezdxf.new('R2004')
    classes = dwg.sections.classes.classes
    dwg.update_class_instance_counters()
    assert instance_count('IMAGE') == 0
    assert instance_count('IMAGEDEF') == 0
    assert instance_count('IMAGEDEF_REACTOR') == 0
    assert instance_count('RASTERVARIABLES') == 0

    image_def = dwg.add_image_def('test', size_in_pixel=(400, 400))
    msp = dwg.modelspace()
    msp.add_image(image_def, insert=(0, 0), size_in_units=(10, 10))

    dwg.update_class_instance_counters()
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
