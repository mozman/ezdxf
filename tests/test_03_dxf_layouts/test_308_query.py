# Copyright (c) 2013-2020, Manfred Moitzi
# License: MIT-License
import pytest
import ezdxf

from ezdxf.query import EntityQuery, name_query


class TestNameQuery:
    @pytest.fixture
    def entities(self):
        return ['LINE', 'CIRCLE', 'POLYLINE', 'MESH', 'SOLID']

    def test_all_names(self, entities):
        result = list(name_query(entities, '*'))
        assert result == entities

    def test_some_names(self, entities):
        result = list(name_query(entities, 'LINE SOLID'))
        assert result == ['LINE', 'SOLID']

    def test_exclude_some_names(self, entities):
        result = list(name_query(entities, '* !SOLID'))
        assert 'SOLID' not in result


@pytest.fixture(scope='module')
def modelspace():
    doc = ezdxf.new()
    modelspace = doc.modelspace()
    modelspace.add_line((0, 0), (10, 0), {'layer': 'lay_lines', 'color': 7})
    modelspace.add_polyline2d([(0, 0), (3, 1), (7, 4), (10, 0)],
                              dxfattribs={'layer': 'lay_lines', 'color': 6})
    modelspace.add_text("TEST", dxfattribs={'layer': 'lay_text', 'color': 6})
    modelspace.add_circle((0, 0), 1, dxfattribs={'layer': 'π'})
    # just 4 entities: LINE, TEXT, POLYLINE, CIRCLE
    # VERTEX & SEQEND are linked to the POLYLINE entity and do not appear in any entity space
    return doc.modelspace()


def test_empty_init():
    result = EntityQuery()
    assert len(result) == 0


def test_select_all(modelspace):
    result = EntityQuery(modelspace, '*')
    # 1xLINE, 1xPOLYLINE, 0xVERTEX, 0xSEQEND, 1x TEXT, 1x CIRCLE
    assert len(result.entities) == 4
    assert len(result) == 4


def test_first(modelspace):
    result = EntityQuery(modelspace, '*')
    assert result.first.dxftype() == 'LINE'


def test_last(modelspace):
    result = EntityQuery(modelspace, '*')
    assert result.last.dxftype() == 'CIRCLE'


def test_new_query_select_all(modelspace):
    result = ezdxf.query.new(modelspace, '*')
    # 1xLINE, 1xPOLYLINE, 0xVERTEX, 0xSEQEND, 1x TEXT, 1x CIRCLE
    assert len(result.entities) == 4
    assert len(result) == 4


def test_new_empty_query():
    result = ezdxf.query.new()
    assert len(result.entities) == 0
    assert len(result) == 0


def test_select_line(modelspace):
    result = EntityQuery(modelspace, 'LINE')
    assert len(result) == 1, 'should be 1 LINE'


def test_select_layer_1(modelspace):
    result = EntityQuery(modelspace, '*[layer=="lay_lines"]')
    assert len(result) == 2
    assert result.first.dxftype() == 'LINE'
    assert result.last.dxftype() == 'POLYLINE'


def test_select_unicode_layer_name(modelspace):
    result = EntityQuery(modelspace, '*[layer=="π"]')
    assert len(result) == 1
    assert result.first.dxftype() == 'CIRCLE'


def test_select_layer_1_exclude_line(modelspace):
    result = EntityQuery(modelspace, '* !LINE[layer=="lay_lines"]')
    # 1xPOLYLINE
    assert len(result) == 1


def test_match_regex(modelspace):
    result = EntityQuery(modelspace, '*[layer ? "lay_.*"]')
    assert len(result) == 3


def test_match_regex_not_text(modelspace):
    result = EntityQuery(modelspace, '* !TEXT[layer ? "lay_.*"]')
    assert len(result) == 2


def test_match_whole_string(modelspace):
    # re just compares the start of a string, check for an
    # implicit '$' at the end of the search string.
    result = EntityQuery(modelspace, '*[layer=="lay"]')
    assert len(result) == 0


def test_not_supported_attribute(modelspace):
    result = EntityQuery(modelspace, '*[mozman!="TEST"]')
    assert len(result) == 0


def test_bool_select(modelspace):
    result = EntityQuery(modelspace, '*[layer=="lay_lines" & color==7]')
    # 1xLINE
    assert len(result) == 1


def test_bool_select_2(modelspace):
    result = EntityQuery(modelspace,
                         '*[layer=="lay_lines" & color==7 | color==6]')
    # 1xLINE(layer=="lay_lines" & color==7) 1xPOLYLINE(color==6) 1xTEXT(color==6)
    assert len(result) == 3


def test_bool_select_3(modelspace):
    result = EntityQuery(modelspace,
                         '*[layer=="lay_lines" & (color==7 | color==6)]')
    # 1xLINE(layer=="lay_lines" & color==7) 1xPOLYLINE(layer=="lay_lines" & color==6)
    assert len(result) == 2


def test_bool_select_4(modelspace):
    result = EntityQuery(modelspace,
                         '*[(layer=="lay_lines" | layer=="lay_text") & !color==7]')
    # 1xPOLYLINE(layer=="lay_lines" & color==6) 1xTEXT(layer=="lay_text" & color==6)
    assert len(result) == 2


def test_ignore_case(modelspace):
    result = EntityQuery(modelspace, '*[layer=="LAY_lines"]i')
    # 1xLINE 1xPOLYLINE
    assert len(result) == 2


def test_ignore_case_for_num_values(modelspace):
    result = EntityQuery(modelspace, '*[color==6]i')
    # 1xPOLYLINE 1xTEXT
    assert len(result) == 2


def test_ignore_case_match_regex(modelspace):
    result = EntityQuery(modelspace, '*[layer ? "LaY_.*"]i')
    assert len(result) == 3


def test_extend_query(modelspace):
    result = EntityQuery(modelspace, '*')
    length = len(result)
    result.extend(result, unique=True)
    assert len(result) == length


def test_all_names():
    names = "ONE TWO THREE"
    result = " ".join(name_query(names.split(), '*'))
    assert names == result


def test_match_one_string():
    names = "ONE TWO THREE"
    result = list(name_query(names.split(), 'ONE'))
    assert "ONE" == result[0]


def test_match_full_string():
    names = "ONEONE TWO THREE"
    result = list(name_query(names.split(), 'ONE'))
    assert len(result) == 0
