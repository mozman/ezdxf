# Copyright (c) 2013-2022, Manfred Moitzi
# License: MIT-License
import pytest
import ezdxf

from ezdxf.query import EntityQuery, name_query, unique_entities
from ezdxf.entities import Text, Line, Circle, Arc, MText
from ezdxf.math import Vec3
from ezdxf import colors


class TestNameQuery:
    @pytest.fixture
    def entities(self):
        return ["LINE", "CIRCLE", "POLYLINE", "MESH", "SOLID"]

    def test_all_names(self, entities):
        result = list(name_query(entities, "*"))
        assert result == entities

    def test_some_names(self, entities):
        result = list(name_query(entities, "LINE SOLID"))
        assert result == ["LINE", "SOLID"]

    def test_exclude_some_names(self, entities):
        result = list(name_query(entities, "* !SOLID"))
        assert "SOLID" not in result


def test_unique_entities_supports_virtual_entities():
    text = Text()
    result = list(unique_entities([text, Line(), Arc(), text]))
    assert len(result) == 3


def test_remove_supports_virtual_entities():
    result = EntityQuery([Text(), Line(), Arc()]).remove("TEXT")
    assert len(result) == 2


@pytest.fixture(scope="module")
def modelspace():
    doc = ezdxf.new()
    modelspace = doc.modelspace()
    modelspace.add_line((0, 0), (10, 0), {"layer": "lay_lines", "color": 7})
    modelspace.add_polyline2d(
        [(0, 0), (3, 1), (7, 4), (10, 0)],
        dxfattribs={"layer": "lay_lines", "color": 6},
    )
    modelspace.add_text("TEST", dxfattribs={"layer": "lay_text", "color": 6})
    modelspace.add_circle((0, 0), 1, dxfattribs={"layer": "π"})
    # just 4 entities: LINE, TEXT, POLYLINE, CIRCLE
    # VERTEX & SEQEND are linked to the POLYLINE entity and do not appear in any entity space
    return doc.modelspace()


def test_empty_init():
    result = EntityQuery()
    assert len(result) == 0


def test_select_all(modelspace):
    result = EntityQuery(modelspace, "*")
    # 1xLINE, 1xPOLYLINE, 0xVERTEX, 0xSEQEND, 1x TEXT, 1x CIRCLE
    assert len(result.entities) == 4
    assert len(result) == 4


def test_first(modelspace):
    result = EntityQuery(modelspace, "*")
    assert result.first.dxftype() == "LINE"


def test_last(modelspace):
    result = EntityQuery(modelspace, "*")
    assert result.last.dxftype() == "CIRCLE"


def test_new_query_select_all(modelspace):
    result = ezdxf.query.new(modelspace, "*")
    # 1xLINE, 1xPOLYLINE, 0xVERTEX, 0xSEQEND, 1x TEXT, 1x CIRCLE
    assert len(result.entities) == 4
    assert len(result) == 4


def test_new_empty_query():
    result = ezdxf.query.new()
    assert len(result.entities) == 0
    assert len(result) == 0


def test_select_line(modelspace):
    result = EntityQuery(modelspace, "LINE")
    assert len(result) == 1, "should be 1 LINE"


def test_select_layer_1(modelspace):
    result = EntityQuery(modelspace, '*[layer=="lay_lines"]')
    assert len(result) == 2
    assert result.first.dxftype() == "LINE"
    assert result.last.dxftype() == "POLYLINE"


def test_select_unicode_layer_name(modelspace):
    result = EntityQuery(modelspace, '*[layer=="π"]')
    assert len(result) == 1
    assert result.first.dxftype() == "CIRCLE"


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
    result = EntityQuery(
        modelspace, '*[layer=="lay_lines" & color==7 | color==6]'
    )
    # 1xLINE(layer=="lay_lines" & color==7) 1xPOLYLINE(color==6) 1xTEXT(color==6)
    assert len(result) == 3


def test_bool_select_3(modelspace):
    result = EntityQuery(
        modelspace, '*[layer=="lay_lines" & (color==7 | color==6)]'
    )
    # 1xLINE(layer=="lay_lines" & color==7) 1xPOLYLINE(layer=="lay_lines" & color==6)
    assert len(result) == 2


def test_bool_select_4(modelspace):
    result = EntityQuery(
        modelspace, '*[(layer=="lay_lines" | layer=="lay_text") & !color==7]'
    )
    # 1xPOLYLINE(layer=="lay_lines" & color==6) 1xTEXT(layer=="lay_text" & color==6)
    assert len(result) == 2


def test_ignore_case(modelspace):
    result = EntityQuery(modelspace, '*[layer=="LAY_lines"]i')
    # 1xLINE 1xPOLYLINE
    assert len(result) == 2


def test_ignore_case_for_num_values(modelspace):
    result = EntityQuery(modelspace, "*[color==6]i")
    # 1xPOLYLINE 1xTEXT
    assert len(result) == 2


def test_ignore_case_match_regex(modelspace):
    result = EntityQuery(modelspace, '*[layer ? "LaY_.*"]i')
    assert len(result) == 3


def test_extend_query(modelspace):
    result = EntityQuery(modelspace, "*")
    length = len(result)
    result.extend(result, unique=True)
    assert len(result) == length


def test_all_names():
    names = "ONE TWO THREE"
    result = " ".join(name_query(names.split(), "*"))
    assert names == result


def test_match_one_string():
    names = "ONE TWO THREE"
    result = list(name_query(names.split(), "ONE"))
    assert "ONE" == result[0]


def test_match_full_string():
    names = "ONEONE TWO THREE"
    result = list(name_query(names.split(), "ONE"))
    assert len(result) == 0


def test_match_default_values():
    """An attribute query should match the default value if the attribute is
    not present.
    """
    text = Text()
    assert text.dxf.hasattr("style") is False
    result = EntityQuery([text], "*[style=='Standard']")
    assert result.first is text


class TestGetSetDelItemInterface:
    def test_select_entities_with_supported_attribute(self, modelspace):
        """EntityQuery.__getitem__("attribute") returns all entities which
        support the given DXF attribute
        """
        query = modelspace.query()
        assert len(query) == 4, "expected all entities"
        lines = query["start"]
        assert len(lines) == 1
        assert lines.selected_dxf_attribute == "start"

        assert lines.first.dxftype() == "LINE"
        assert query["center"].first.dxftype() == "CIRCLE"

    def test_set_item_accepts_only_strings_as_key(self):
        query = EntityQuery()
        with pytest.raises(TypeError):
            query[1] = "has to fail"
        with pytest.raises(TypeError):
            query[:] = "has to fail"

    def test_set_item_set_supported_dxf_attributes(self):
        query = EntityQuery([Line(), Circle(), Text()])
        query["layer"] = "MyLayer"
        assert all(e.dxf.layer == "MyLayer" for e in query) is True

    def test_set_item_ignores_unsupported_attributes(self):
        query = EntityQuery([Line(), Text()])
        query["text"] = "MyText"
        assert query.query("TEXT").first.dxf.text == "MyText"

    def test_set_item_does_not_ignore_invalid_attribute_values(self):
        query = EntityQuery([Line(), Text()])
        with pytest.raises(TypeError):
            query["start"] = "InvalidVertex"
        with pytest.raises(ValueError):
            query["color"] = "red"

    def test_del_item_ignores_unsupported_attributes(self):
        query = EntityQuery([Line(), Text()])
        query["layer"] = "MyLayer"
        del query["layer"]
        assert query[0].dxf.layer == "0", "expected the default value"
        assert query[1].dxf.layer == "0", "expected the default value"


class TestVirtualAttributes:
    @pytest.fixture
    def entities(self):
        return EntityQuery([
            MText.new(dxfattribs={"text": "content"}),  # virtual text attribute
            Text.new(dxfattribs={"text": "content"})
        ])

    def test_get_virtual_attributes(self, entities):
        assert len(entities["text"]) == 2

    def test_set_virtual_attributes(self, entities):
        entities["text"] = "XYZ"
        assert all(e.dxf.text == "XYZ" for e in entities)

    def test_cannot_delete_virtual_attributes(self, entities):
        """Cannot delete virtual DXF attributes! """
        del entities["text"]
        assert entities.query("MTEXT").first.dxf.text == "content"


class TestOperatorSelection:
    @pytest.fixture
    def query(self):
        return EntityQuery(
            [
                Line.new(dxfattribs={"layer": "Lay1", "color": 1}),
                Text.new(dxfattribs={"layer": "Lay2", "color": 2}),
            ]
        )

    def test_no_selected_dxf_attribute_raises_type_error(self):
        query = EntityQuery()
        with pytest.raises(TypeError):
            _ = query == "MyLayer"

    def test_is_equal_operator(self, query: EntityQuery):
        result = query["layer"] == "Lay1"
        assert len(result) == 1
        assert result.first.dxftype() == "LINE"
        assert (
            result.selected_dxf_attribute == "layer"
        ), "selection should be propagated"

    def test_is_not_equal_operator(self, query: EntityQuery):
        result = query["layer"] != "Lay1"
        assert len(result) == 1
        assert result.first.dxftype() == "TEXT"

    def test_query_is_case_insensitive_by_default(self, query: EntityQuery):
        result = query["layer"] == "LAY1"
        assert len(result) == 1

    def test_less_than_operator(self, query: EntityQuery):
        result = query["color"] < 2
        assert len(result) == 1
        assert result.first.dxftype() == "LINE"

    def test_less_than_raises_type_error_for_vector_attributes(self):
        query = EntityQuery([Text.new(dxfattribs={"insert": Vec3(0, 0)})])
        with pytest.raises(TypeError):
            _ = query["insert"] < (1, 0)

    def test_greater_than_operator(self, query: EntityQuery):
        result = query["color"] > 1
        assert len(result) == 1
        assert result.first.dxftype() == "TEXT"

    def test_greater_than_raises_type_error_for_vector_attributes(self):
        query = EntityQuery([Text.new(dxfattribs={"insert": Vec3(0, 0)})])
        with pytest.raises(TypeError):
            _ = query["insert"] > (1, 0)

    def test_less_equal_operator(self, query: EntityQuery):
        result = query["color"] <= 2
        assert len(result) == 2

    def test_less_equal_raises_type_error_for_vector_attributes(self):
        query = EntityQuery([Text.new(dxfattribs={"insert": Vec3(0, 0)})])
        with pytest.raises(TypeError):
            _ = query["insert"] <= (1, 0)

    def test_greater_equal_operator(self, query: EntityQuery):
        result = query["color"] >= 1
        assert len(result) == 2

    def test_greater_equal_raises_type_error_for_vector_attributes(self):
        query = EntityQuery([Text.new(dxfattribs={"insert": Vec3(0, 0)})])
        with pytest.raises(TypeError):
            _ = query["insert"] >= (1, 0)

    def test_filter_operator(self, query):
        """Build your own operator to filter non DXF attributes."""
        for e in query:
            e.rgb = (0, 0, 0)
        result = query.filter(lambda e: e.rgb == (0, 0, 0))
        assert len(result) == 2


class TestRegexMatch:
    @pytest.fixture
    def base(self):
        return EntityQuery(
            [
                Line.new(dxfattribs={"layer": "Lay_line", "color": 1}),
                Circle.new(
                    dxfattribs={"layer": "lAy_circle", "center": Vec3(0, 0)}
                ),
                Text.new(dxfattribs={"layer": "laY_text"}),
            ]
        )

    def test_match_nothing(self, base: EntityQuery):
        result = base["layer"].match("nothing")
        assert len(result) == 0

    def test_match_is_case_insensitive(self, base: EntityQuery):
        result = base["layer"].match("lay_.*")
        assert len(result) == 3

    def test_match_case_insensitive(self, base: EntityQuery):
        layers = base["layer"]
        layers.ignore_case = False
        assert len(layers.match("Lay_.*")) == 1

    def test_match_invalid_attributes_raise_type_error(self, base: EntityQuery):
        with pytest.raises(TypeError):
            base["color"].match("nothing")
        with pytest.raises(TypeError):
            base["center"].match("nothing")


class TestSetOperations:
    @pytest.fixture
    def base(self):
        return EntityQuery(
            [
                Line.new(dxfattribs={"layer": "line", "color": 1}),
                Circle.new(dxfattribs={"layer": "circle", "color": 2}),
                Text.new(dxfattribs={"layer": "text", "color": 3}),
            ]
        )

    def test_union(self, base: EntityQuery):
        other = EntityQuery(
            [
                Line.new(dxfattribs={"layer": "line", "color": 1}),
                Circle.new(dxfattribs={"layer": "circle", "color": 2}),
                Text.new(dxfattribs={"layer": "text", "color": 3}),
            ]
        )
        assert len(base | other) == 6

    def test_union_unique_entities(self, base: EntityQuery):
        assert len(base | base) == 3

    def test_difference(self, base: EntityQuery):
        result = base - base.query("LINE")
        assert len(result) == 2
        assert [e.dxftype() for e in result] == ["CIRCLE", "TEXT"]

    def test_intersection(self, base: EntityQuery):
        result = base & base.query("LINE")
        assert len(result) == 1
        assert [e.dxftype() for e in result] == ["LINE"]

    def test_symmetric_difference(self, base: EntityQuery):
        other = base.query("LINE") | EntityQuery(
            [Arc.new(dxfattribs={"layer": "arc", "color": 4})]
        )
        result = base ^ other
        assert len(result) == 3
        assert [e.dxftype() for e in result] == ["CIRCLE", "TEXT", "ARC"]

    def test_operator_combination(self, base: EntityQuery):
        result = (base["layer"] == "line") | (base["color"] == 2)
        assert len(result) == 2
        assert [e.dxftype() for e in result] == ["LINE", "CIRCLE"]


class TestDescriptors:
    @pytest.fixture
    def entities(self):
        return EntityQuery(
            [
                Line.new(
                    handle="ABBA",
                    dxfattribs={
                        "layer": "line",
                        "color": 1,
                        "linetype": "SOLID",
                        "lineweight": 18,
                    },
                ),
                Circle.new(
                    handle="FEFE",
                    dxfattribs={
                        "layer": "circle",
                        "color": 2,
                        "linetype": "DOT",
                        "lineweight": 25,
                    },
                ),
            ]
        )

    def test_select_layers(self, entities: EntityQuery):
        assert len(entities.layer == "LINE") == 1

    def test_set_layer_attribute(self, entities: EntityQuery):
        entities.layer = "TEST"
        assert len(entities) == 2
        assert all(e.dxf.layer == "TEST" for e in entities) is True

    def test_delete_layer_attribute(self, entities: EntityQuery):
        del entities.layer
        assert len(entities) == 2
        assert all(e.dxf.layer == "0" for e in entities) is True

    def test_color_descriptor_exists(self, entities: EntityQuery):
        assert len(entities.color == 1) == 1
        # set and delete follow the same schema as for layer

    def test_linetype_descriptor_exists(self, entities: EntityQuery):
        assert len(entities.linetype == "DOT") == 1
        # set and delete follow the same schema as for layer

    def test_lineweight_descriptor_exists(self, entities: EntityQuery):
        assert len(entities.lineweight == 18) == 1
        # set and delete follow the same schema as for layer

    def test_ltscale_descriptor_exists(self, entities: EntityQuery):
        assert len(entities.ltscale == 1.0) == 2, "default value"
        # set and delete follow the same schema as for layer

    def test_invisible_descriptor_exists(self, entities: EntityQuery):
        assert len(entities.invisible == 0) == 2, "default value"
        # set and delete follow the same schema as for layer

    def test_true_color_descriptor_exists(self, entities: EntityQuery):
        assert (
            len(entities.true_color == colors.rgb2int((0, 0, 0))) == 0
        ), "has no default value"
        # set and delete follow the same schema as for layer

    def test_transparency_descriptor_exists(self, entities: EntityQuery):
        assert (
            len(entities.transparency == colors.float2transparency(0)) == 0
        ), "has no default value"
        # set and delete follow the same schema as for layer
