#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import pytest

pytest.importorskip("PyQt5")

from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.loader import load_dxf_structure

from ezdxf.addons.browser import DXFTagsModel, DXFStructureModel
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
        return Tags.from_text(POINT)

    @pytest.fixture
    def model(self):
        return DXFTagsModel(self.tags())

    def test_fixed_column_count(self, model):
        assert model.columnCount() == 3

    def test_row_count(self, model):
        assert model.rowCount() == len(self.tags())

    def test_dxf_entity_type(self, model):
        assert model.dxftype() == "POINT"

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
    sections = load_dxf_structure(Tags.from_text(ENTITIES))
    model = DXFStructureModel(sections)
    item = model.item(0, 0)
    assert item.data(Qt.DisplayRole) == "ENTITIES"
    child1 = item.child(0, 1)
    assert child1.data(Qt.DisplayRole) == "LINE(#100)"
    child2 = item.child(0, 2)
    assert child2.data(Qt.DisplayRole) == "LINE(#101)"


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
