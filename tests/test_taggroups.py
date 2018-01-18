# Created: 13.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
from ezdxf.lldxf.tags import group_tags, internal_tag_compiler


@pytest.fixture
def groups():
    return list(group_tags(internal_tag_compiler(TESTTAGS)))


def test_init(groups):
    assert 36 == len(groups)


def test_first_group(groups):
    assert 'SECTION' == groups[0][0].value
    assert 2 == len(groups[0])


def test_second_group(groups):
    assert 'TABLE' == groups[1][0].value
    assert 3 == len(groups[1])


def test_last_group(groups):
    assert 'ENDTAB' == groups[-1][0].value
    assert 1 == len(groups[-1])


TESTTAGS = """  0
SECTION
  2
TABLES
  0
TABLE
  2
LTYPE
 70
     5
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
LTYPE
  2
CENTER
 70
     0
  3
Center ____ _ ____ _ ____ _ ____ _ ____ _ ____
 72
    65
 73
     4
 40
2.0
 49
1.25
 49
-0.25
 49
0.25
 49
-0.25
  0
LTYPE
  2
DASHED
 70
     0
  3
Dashed __ __ __ __ __ __ __ __ __ __ __ __ __ _
 72
    65
 73
     2
 40
0.75
 49
0.5
 49
-0.25
  0
LTYPE
  2
PHANTOM
 70
     0
  3
Phantom ______  __  __  ______  __  __  ______
 72
    65
 73
     6
 40
2.5
 49
1.25
 49
-0.25
 49
0.25
 49
-0.25
 49
0.25
 49
-0.25
  0
LTYPE
  2
HIDDEN
 70
     0
  3
Hidden __ __ __ __ __ __ __ __ __ __ __ __ __ __
 72
    65
 73
     2
 40
9.5249999999999986
 49
6.3499999999999988
 49
-3.1749999999999989
  0
ENDTAB
  0
TABLE
  2
LAYER
 70
     3
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
LAYER
  2
VIEW_PORT
 70
     0
 62
     7
  6
CONTINUOUS
  0
LAYER
  2
DEFPOINTS
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
     5
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
STYLE
  2
ANNOTATIVE
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
STYLE
  2
NOTES
 70
     0
 40
3.0
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
STYLE
  2
TITLES
 70
     0
 40
6.0
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
STYLE
  2

 70
     1
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
ltypeshp.shx
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
"""
