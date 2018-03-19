# Created: 15.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
from io import StringIO
import ezdxf
from ezdxf.lldxf.tags import Tags, internal_tag_compiler, group_tags
from ezdxf.sections.classes import ClassesSection
from ezdxf.lldxf.tagwriter import TagWriter
from ezdxf.tools.test import load_section


@pytest.fixture(scope='module')
def section():
    return ClassesSection(load_section(TESTCLASSES, 'CLASSES'), None)


def test_write(section):
    stream = StringIO()
    section.write(TagWriter(stream))
    result = stream.getvalue()
    stream.close()
    t1 = list(internal_tag_compiler(TESTCLASSES))
    t2 = list(internal_tag_compiler(result))
    assert t1 == t2


def test_empty_section():
    tags = load_section(EMPTYSEC, 'CLASSES')
    section = ClassesSection(tags, None)
    stream = StringIO()
    section.write(TagWriter(stream))
    result = stream.getvalue()
    stream.close()
    assert EMPTYSEC == result


def test_count_class_instances():
    def instance_count(name):
        return classes[name].dxf.instance_count
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
