import pytest


import re


import ezdxf


from ezdxf.query import EntityQuery


from ezdxf.entities import Line


def test_repeated_query_reads_changed_entity_attributes():
    entity = Line.new(dxfattribs={"layer": "before"})
    query = 'LINE[layer == "before"]'
    assert list(EntityQuery([entity], query)) == [entity]
    entity.dxf.layer = "after"
    assert len(EntityQuery([entity], query)) == 0


def test_repeated_query_does_not_retain_other_document_entities():
    first = ezdxf.new().modelspace().add_line((0, 0), (1, 1))
    second = ezdxf.new().modelspace().add_line((0, 0), (1, 1))
    query = 'LINE[layer == "0"]'
    assert list(EntityQuery([first], query)) == [first]
    assert list(EntityQuery([second], query)) == [second]


def test_repeated_query_keeps_case_options_separate():
    entity = Line.new(dxfattribs={"layer": "UPPER"})
    query = 'LINE[layer == "upper"]'
    assert list(EntityQuery([entity], query + "i")) == [entity]
    assert len(EntityQuery([entity], query)) == 0


def test_invalid_query_does_not_break_later_repeated_queries():
    entity = Line.new(dxfattribs={"layer": "before"})
    query = 'LINE[layer ? "before"]'
    assert list(EntityQuery([entity], query)) == [entity]
    for _ in range(2):
        with pytest.raises(re.error):
            EntityQuery([entity], 'LINE[layer ? "["]')
    assert list(EntityQuery([entity], query)) == [entity]
