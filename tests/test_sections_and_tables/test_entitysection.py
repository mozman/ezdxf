# Created: 13.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
import ezdxf


def drawing(version):
    dwg = ezdxf.new(version)
    modelspace = dwg.modelspace()
    modelspace.add_line((0, 0), (10, 0), {'layer': 'lay_line'})
    modelspace.add_text("TEST", dxfattribs={'layer': 'lay_line'})
    modelspace.add_polyline2d([(0, 0), (3, 1), (7, 4), (10, 0)], {'layer': 'lay_polyline'})
    # just 3 entities: LINE, TEXT, POLYLINE - VERTEX & SEQEND now linked to the POLYLINE entity, and do not appear
    # in any entity space
    return dwg


def test_iteration_with_layout_DXF12():
    dwg = ezdxf.new('AC1009')
    m = dwg.modelspace()
    m.add_line((0, 0), (1, 1))
    entity = list(dwg.entities)[-1]
    assert dwg == entity.drawing  # check drawing attribute


def test_iteration_with_layout_DXF2000():
    dwg = ezdxf.new('AC1015')
    m = dwg.modelspace()
    m.add_line((0, 0), (1, 1))
    entity = list(dwg.entities)[-1]
    assert dwg == entity.drawing  # check drawing attribute


def test_delete_all_entities_DXF12():
    dwg = ezdxf.new('AC1009')
    m = dwg.modelspace()
    for _ in range(5):
        m.add_line((0, 0), (1, 1))
    assert 5 == len(dwg.entities)

    dwg.entities.delete_all_entities()
    assert 0 == len(dwg.entities)


@pytest.fixture(scope='module', params=['AC1009', 'AC1018'])
def dxf(request):
    return drawing(request.param)


def test_query_all_entities(dxf):
    # independent from layout (modelspace or paperspace)
    entities = dxf.entities.query('*')
    assert 3 == len(entities)


def test_query_polyline(dxf):
    entities = dxf.entities.query('POLYLINE')
    assert 1 == len(entities)


def test_query_line_and_polyline(dxf):
    entities = dxf.entities.query('POLYLINE LINE')
    assert 2 == len(entities)


def test_query_vertices(dxf):
    # VERTEX entities are no more in any entity space, they are lined to the POLYLINE entity
    entities = dxf.entities.query('VERTEX')
    assert 0 == len(entities)


def test_query_layer_line(dxf):
    entities = dxf.entities.query('*[layer=="lay_line"]')
    assert 2 == len(entities)


def test_query_layer_polyline(dxf):
    entities = dxf.entities.query('*[layer=="lay_polyline"]')
    assert 1 == len(entities)


def test_query_layer_by_regex(dxf):
    entities = dxf.entities.query('*[layer ? "lay_.*"]')
    assert 3 == len(entities)


EMPTYSEC = """  0
SECTION
  2
ENTITIES
  0
ENDSEC
"""


TESTENTITIES = """  0
SECTION
  2
ENTITIES
  0
VIEWPORT
  5
28B
 67
     1
  8
0
 10
4.7994580606
 20
4.0218994936
 30
0.0
 40
17.880612775
 41
8.9929997457
 68
     1
 69
     1
1001
ACAD
1000
MVIEW
1002
{
1070
    16
1010
0.0
1020
0.0
1030
0.0
1010
0.0
1020
0.0
1030
1.0
1040
0.0
1040
8.99299974
1040
4.79945806
1040
4.02189949
1040
50.0
1040
0.0
1040
0.0
1070
     0
1070
  1000
1070
     1
1070
     1
1070
     0
1070
     0
1070
     0
1070
     0
1040
0.0
1040
0.0
1040
0.0
1040
0.5
1040
0.5
1040
0.5
1040
0.5
1070
     0
1002
{
1002
}
1002
}
  0
VIEWPORT
  5
290
 67
     1
  8
VIEW_PORT
 10
4.8288665
 20
3.9999997
 30
0.0
 40
8.3999996
 41
6.3999996
 68
     2
 69
     2
1001
ACAD
1000
MVIEW
1002
{
1070
    16
1010
0.0
1020
0.0
1030
0.0
1010
0.0
1020
0.0
1030
1.0
1040
0.0
1040
6.399999
1040
6.0
1040
4.5
1040
50.0
1040
0.0
1040
0.0
1070
     0
1070
  1000
1070
     1
1070
     3
1070
     0
1070
     0
1070
     0
1070
     0
1040
0.0
1040
0.0
1040
0.0
1040
0.5
1040
0.5
1040
0.5
1040
0.5
1070
     0
1002
{
1002
}
1002
}
  0
ENDSEC
"""
