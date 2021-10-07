#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import pytest

pytest.importorskip("PySide6")

from io import StringIO
import math
from ezdxf.lldxf.tags import Tags, DXFTag
from ezdxf.lldxf.loader import load_dxf_structure
from ezdxf.lldxf.tagger import ascii_tags_loader

from ezdxf.addons.browser import DXFTagsModel, DXFStructureModel, DXFDocument
from ezdxf.addons.browser.tags import compile_tags
from ezdxf.addons.browser.data import (
    LineIndex,
    EntityHistory,
    SearchIndex,
)

from ezdxf.addons.xqt import Qt, QModelIndex


def txt2tags(s: str) -> Tags:
    return Tags(ascii_tags_loader(StringIO(s), skip_comments=False))


NAN = float("nan")


# noinspection PyMissingConstructor
class ModelIndex(QModelIndex):
    """Proxy"""

    def __init__(self, row, col):
        self._row = row
        self._col = col

    def row(self):
        return self._row

    def column(self):
        return self._col


class TestDXFTagsModel:
    def tags(self):
        return txt2tags(POINT)

    @pytest.fixture
    def model(self):
        return DXFTagsModel(self.tags())

    def test_fixed_column_count(self, model):
        assert model.columnCount() == 3

    def test_row_count(self, model):
        assert model.rowCount() == len(compile_tags(self.tags()))

    def test_render_display_role(self, model):
        assert model.data(ModelIndex(0, 0), role=Qt.DisplayRole) == "0"
        assert model.data(ModelIndex(0, 1), role=Qt.DisplayRole) == "<ctrl>"
        assert model.data(ModelIndex(0, 2), role=Qt.DisplayRole) == "POINT"


POINT = """0
POINT
5
0
330
0
100
AcDbEntity
8
0
100
AcDbPoint
10
0.0
20
0.0
30
0.0
"""


def test_setup_dxf_structure_model():
    sections = load_dxf_structure(txt2tags(ENTITIES))
    doc = DXFDocument(sections)
    model = DXFStructureModel("ez.dxf", doc)
    parent = model.item(0, 0)
    assert parent.data(Qt.DisplayRole) == "ez.dxf"
    assert "ENTITIES" in parent.child(0, 0).data(Qt.DisplayRole)
    # one level down
    parent = parent.child(0, 0)
    assert "LINE" in parent.child(0, 0).data(Qt.DisplayRole)
    assert "LINE" in parent.child(1, 0).data(Qt.DisplayRole)


class TestDXFDocument:
    @pytest.fixture
    def doc(self):
        sections = load_dxf_structure(txt2tags(ENTITIES))
        return DXFDocument(sections)

    def test_get_entity_returns_entity_tags(self, doc):
        entity = doc.get_entity("100")
        assert entity[0] == (0, "LINE")

    def test_get_entity_by_invalid_handle_returns_none(self, doc):
        assert doc.get_entity("XXX") is None

    def test_get_start_line_number_for_entity(self, doc):
        entity = doc.get_entity("101")
        assert doc.get_line_number(entity) == 9

    def test_get_entity_by_line_number(self, doc):
        entity = doc.get_entity("101")
        assert doc.get_entity_at_line(9) is entity
        assert doc.get_entity_at_line(10) is entity
        assert (
            doc.get_entity_at_line(99) is entity
        ), "should return the last entity"


class TestTagCompiler:
    def test_compile_single_int(self):
        tags = compile_tags(txt2tags("70\n3"))
        assert tags[0] == (70, 3)

    def test_compile_invalid_int_to_str(self):
        tags = compile_tags(txt2tags("70\nx"))
        assert tags[0] == (70, "x")

    def test_compile_single_float(self):
        tags = compile_tags(txt2tags("40\n3.14"))
        assert tags[0] == (40, 3.14)

    def test_compile_invalid_float_to_str(self):
        tags = compile_tags(txt2tags("40\nx.14"))
        assert tags[0] == (40, "x.14")

    def test_compile_single_2d_point(self):
        tags = compile_tags(txt2tags("10\n1.2\n20\n2.3"))
        assert tags[0] == (10, (1.2, 2.3))

    def test_compile_two_2d_points(self):
        tags = compile_tags(txt2tags("10\n1.1\n20\n1.2\n10\n2.1\n20\n2.2"))
        assert tags[0] == (10, (1.1, 1.2))
        assert tags[1] == (10, (2.1, 2.2))

    def test_compile_nan_coords_2d(self):
        tags = compile_tags(txt2tags("10\nx.2\n20\n2.3"))
        assert math.isnan(tags[0].value[0])

    def test_compile_single_3d_point(self):
        tags = compile_tags(txt2tags("10\n1.2\n20\n2.3\n30\n3.4"))
        assert tags[0] == (10, (1.2, 2.3, 3.4))

    def test_compile_nan_coords_3d(self):
        tags = compile_tags(txt2tags("10\n1\n20\n2\n30\nx"))
        assert math.isnan(tags[0].value[2])

    def test_compile_single_group_code_10(self):
        tags = compile_tags(txt2tags("10\n1.1"))
        assert tags[0] == (10, 1.1)

    def test_compile_two_group_code_10(self):
        tags = compile_tags(txt2tags("10\n1.1\n10\n2.2"))
        assert tags[0] == (10, 1.1)
        assert tags[1] == (10, 2.2)

    def test_compile_swapped_coords(self):
        tags = compile_tags(txt2tags("20\n2.2\n10\n1.1"))
        assert tags[0] == (20, 2.2), "expected coords as single tags"
        assert tags[1] == (10, 1.1), "expected coords as single tags"


def test_line_index_adds_missing_endsec_tag():
    # The function load_dxf_structure() throws the ENDSEC tag away.
    # The line indexer must take this issue into account!
    sections = load_dxf_structure(txt2tags(SECTIONS))
    index = LineIndex(sections)
    entity = index.get_entity_at_line(15)
    assert entity.get_handle() == "100"
    assert index.get_start_line_for_entity(entity) == 15


ENTITIES = """0
SECTION
2
ENTITIES
0
LINE
5
100
0
LINE
5
101
0
ENDSEC
0
EOF
"""

SECTIONS = """0
SECTION
2
HEADER
9
$ACADVER
1
AC1032
0
ENDSEC
0
SECTION
2
ENTITIES
0
LINE
5
100
0
ENDSEC
0
EOF
"""


class TestEntityHistory:
    @pytest.fixture
    def history2(self):
        history = EntityHistory()
        history.append(Tags([DXFTag(1, "first")]))
        history.append(Tags([DXFTag(2, "second")]))
        return history

    def test_setup_history(self):
        history = EntityHistory()
        assert len(history) == 0
        assert history.index == 0

    def test_empty_history_returns_none(self):
        history = EntityHistory()
        assert history.back() is None
        assert history.forward() is None

    def test_append_one_entity(self):
        history = EntityHistory()
        history.append(Tags())
        assert len(history) == 1
        assert history.index == 0

    def test_append_two_entities(self):
        history = EntityHistory()
        history.append(Tags())
        history.append(Tags())
        assert len(history) == 2
        assert history.index == 1

    def test_go_back_in_history(self, history2):
        first, second = history2.content()
        assert history2.index == 1
        assert history2.back() is first
        assert len(history2) == 2, "entity is still in history"
        assert history2.index == 0

    def test_go_back_and_forward_in_history(self, history2):
        first, second = history2.content()
        assert history2.back() is first
        assert history2.forward() is second

    def test_append_should_add_time_travel_history(self, history2):
        first, second = history2.content()
        assert history2.back() is first  # 1st time travel
        assert history2.index == 0

        assert history2.forward() is second  # 2nd time travel
        assert history2.index == 1

        third = Tags([DXFTag(3, "third")])
        history2.append(third)
        assert history2.index == 4

        # complete travel history
        content = history2.content()
        assert len(content) == 5
        #                                 time wraps ->  append
        assert content == [first, second, first, second, third]


SEARCH_EXAMPLE1 = """0
SEARCH1
8
LayerName1
62
7
"""

SEARCH_EXAMPLE2 = """0
SEARCH2
8
LayerName2
62
6
"""


class TestSearchIndex:
    @pytest.fixture(scope="class")
    def entities(self):
        return [txt2tags(SEARCH_EXAMPLE1), txt2tags(SEARCH_EXAMPLE2)]

    @pytest.fixture
    def search(self, entities):
        return SearchIndex(entities)

    @staticmethod
    def move_cursor_forward(s: SearchIndex, count: int):
        for _ in range(count):
            s.move_cursor_forward()

    @staticmethod
    def move_cursor_backward(s: SearchIndex, count: int):
        for _ in range(count):
            s.move_cursor_backward()

    def test_valid_setup_and_default_settings(self, search):
        assert len(search.entities) == 2
        assert search.is_end_of_index is False
        assert (
            search.case_insensitive is True
        ), "should be case insensitive by default"
        assert (
            search.numbers is False
        ), "should not search in number tags by default"

    def test_empty_search_index(self):
        search_index = SearchIndex([])
        assert search_index.is_end_of_index is True

    def test_reset_cursor_forward(self, search):
        search.reset_cursor(backward=False)
        assert search.cursor() == (
            0,
            0,
        ), "cursor should be the first tag of the first entity"
        assert search.is_end_of_index is False

    def test_move_cursor_forward(self, search):
        search.reset_cursor()
        search.move_cursor_forward()
        assert search.cursor() == (0, 1)

    def test_move_cursor_forward_beyond_entity_border(self, search):
        search.reset_cursor()
        self.move_cursor_forward(search, 3)
        assert search.cursor() == (1, 0)

    def test_move_cursor_forward_to_the_end_of_index(self, search):
        search.reset_cursor()
        self.move_cursor_forward(search, 10)
        assert search.is_end_of_index is True
        assert search.cursor() == (
            1,
            2,
        ), "index should stop at the last tag of the last entity"

    def test_reset_cursor_backward(self, search):
        search.reset_cursor(backward=True)
        assert search.cursor() == (
            1,
            2,
        ), "cursor should be the last tag of the last entity"
        assert search.is_end_of_index is False

    def test_move_cursor_backward(self, search):
        search.reset_cursor(backward=True)
        search.move_cursor_backward()
        assert search.cursor() == (1, 1)

    def test_move_cursor_backward_beyond_entity_border(self, search):
        search.reset_cursor(backward=True)
        self.move_cursor_backward(search, 3)
        assert search.cursor() == (0, 2)

    def test_move_cursor_backward_to_the_end_of_index(self, search):
        search.reset_cursor()
        self.move_cursor_backward(search, 10)
        assert search.is_end_of_index is True
        assert search.cursor() == (
            0,
            0,
        ), "index should stop at the first tag of the first entity"

    def test_failing_search(self, search):
        entity, index = search.find("XDATA")
        assert entity is None
        assert index == -1
        assert search.is_end_of_index is True

    def test_find_entity_type(self, search):
        entity, index = search.find("SEARCH1")
        assert entity is search.entities[0]
        assert index == 0

    def test_find_forward_entity_type(self, search):
        search.find("SEARCH")
        entity, index = search.find_forward()
        assert entity is search.entities[1]
        assert index == 0

    def test_find_content(self, search):
        entity, index = search.find("LayerName1")
        assert entity is search.entities[0]
        assert index == 1

    def test_find_forward_content(self, search):
        search.find("LayerName")
        entity, index = search.find_forward()
        assert entity is search.entities[1]
        assert index == 1

    def test_failing_find_forward_returns_none(self, search):
        search.find("LayerName")
        search.find_forward()
        entity, index = search.find_forward()
        assert entity is None
        assert index == -1

    def test_not_initiated_find_forward_returns_none(self, search):
        entity, index = search.find_forward()
        assert entity is None
        assert index == -1

    def test_case_insensitive_search(self, search):
        search.case_insensitive = True
        entity, index = search.find("LAYERNAME1")
        assert entity is search.entities[0]
        assert index == 1

    def test_case_sensitive_search(self, search):
        search.case_insensitive = False
        entity, index = search.find("LAYERNAME1")
        assert entity is None

    def test_ignore_number_tags(self, search):
        search.numbers = False
        entity, index = search.find("6")
        assert entity is None

    def test_search_in_number_tags(self, search):
        search.numbers = True
        entity, index = search.find("6")
        assert entity is search.entities[1]
        assert index == 2

    def test_failing_find_forward_stops_at_the_end(self, search):
        assert search.find("XXX") is search.NOT_FOUND
        assert search.is_end_of_index is True

    def test_failing_find_backwards_stops_at_the_beginning(self, search):
        assert search.find("XXX", backward=True) is search.NOT_FOUND
        assert search.is_end_of_index is True


if __name__ == "__main__":
    pytest.main([__file__])
