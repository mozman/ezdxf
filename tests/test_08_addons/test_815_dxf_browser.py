#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import pytest

pytest.importorskip("PyQt5")

from io import StringIO
import math
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.loader import load_dxf_structure
from ezdxf.lldxf.tagger import ascii_tags_loader

from ezdxf.addons.browser import DXFTagsModel, DXFStructureModel
from ezdxf.addons.browser.tags import compile_tags

from PyQt5.QtCore import Qt, QModelIndex


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
999
Dummy - a vertex is never the last tag in a DXF file
"""


def test_setup_dxf_structure_model():
    sections = load_dxf_structure(Tags.from_text(ENTITIES))
    model = DXFStructureModel("ez.dxf", sections)
    parent = model.item(0, 0)
    assert parent.data(Qt.DisplayRole) == "ez.dxf"
    assert "ENTITIES" in parent.child(0, 0).data(Qt.DisplayRole)
    # one level down
    parent = parent.child(0, 0)
    assert "LINE" in parent.child(0, 0).data(Qt.DisplayRole)
    assert "LINE" in parent.child(1, 0).data(Qt.DisplayRole)


def txt2tags(s: str) -> Tags:
    return Tags(ascii_tags_loader(StringIO(s), skip_comments=False))


NAN = float("nan")


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

    def test_preserve_comments(self):
        tags = compile_tags(txt2tags("999\ncomment"))
        assert tags[0] == (999, "comment")


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

if __name__ == "__main__":
    pytest.main([__file__])
