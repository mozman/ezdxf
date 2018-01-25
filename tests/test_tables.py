# Created: 12.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
from io import StringIO

import ezdxf
from ezdxf.tools.test import DrawingProxy, Tags, compile_tags_without_handles, load_section
from ezdxf.sections.tables import TablesSection
from ezdxf.lldxf.tagwriter import TagWriter
from ezdxf.drawing import Drawing


@pytest.fixture
def tables():
    dwg = DrawingProxy('AC1009')
    tables = load_section(TEST_TABLES, 'TABLES')
    return TablesSection(tables, dwg)


def test_constructor(tables):
    assert tables.layers is not None


def test_getattr_lower_case(tables):
    assert tables.linetypes is not None


def test_getattr_upper_case(tables):
    assert tables.LINETYPES is not None


def test_error_getattr(tables):
    with pytest.raises(ezdxf.DXFAttributeError):
        tables.test


def test_write(tables):
    stream = StringIO()
    tables.write(TagWriter(stream))
    result = stream.getvalue()
    stream.close()
    t1 = list(compile_tags_without_handles(TEST_TABLES))
    t1.pop()  # remove EOF tag
    t2 = list(compile_tags_without_handles(result))
    assert t1 == t2


def test_min_r12_drawing():
    tags = Tags.from_text(MINIMALISTIC_DXF12)
    drawing = Drawing(tags)
    assert len(drawing.linetypes) == 0


MINIMALISTIC_DXF12 = """  0
SECTION
  2
ENTITIES
  0
ENDSEC
  0
EOF
"""


TEST_TABLES = """  0
SECTION
  2
TABLES
  0
TABLE
  2
LTYPE
 70
     1
  0
LTYPE
  2
CONTINUOUS
 70
     0
  3
Solid line
 72
    65
 73
     0
 40
0.0
  0
ENDTAB
  0
TABLE
  2
LAYER
 70
     1
  0
LAYER
  2
0
 70
     0
 62
     7
  6
CONTINUOUS
  0
ENDTAB
  0
TABLE
  2
STYLE
 70
     1
  0
STYLE
  2
STANDARD
 70
     0
 40
0.0
 41
1.0
 50
0.0
 71
     0
 42
0.2
  3
txt
  4

  0
ENDTAB
  0
TABLE
  2
VIEW
 70
     0
  0
ENDTAB
  0
TABLE
  2
UCS
 70
     0
  0
ENDTAB
  0
TABLE
  2
APPID
 70
    0
  0
ENDTAB
  0
TABLE
  2
DIMSTYLE
 70
     0
  0
ENDTAB
  0
ENDSEC
  0
EOF
"""