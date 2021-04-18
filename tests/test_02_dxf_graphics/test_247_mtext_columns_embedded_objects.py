#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.entities.mtext import (
    load_columns_from_embedded_object, MText, ColumnType
)
from ezdxf.lldxf.tags import Tags

DYNAMIC_MANUAL_HEIGHT = """101
Embedded Object
70
1
10
1.0
20
0.0
30
0.0
11
69.8
21
276.1
31
0.0
40
62.6
41
0.0
42
175.0
43
164.8
71
2
72
3
44
50.0
45
12.5
73
0
74
0
46
164.8
46
154.3
46
0.0
"""


DYNAMIC_AUTO_HEIGHT = """101
Embedded Object
70
1
10
1.0
20
0.0
30
0.0
11
69.8
21
276.1
31
0.0
40
62.6
41
158.1
42
175.0
43
158.1
71
2
72
0
44
50.0
45
12.5
73
1
74
0
"""


STATIC = """101
Embedded Object
70
1
10
1.0
20
0.0
30
0.0
11
69.8
21
276.1
31
0.0
40
62.6
41
150.0
42
175.0
43
150.0
71
1
72
3
44
50.0
45
12.5
73
0
74
0
"""

# The dynamic auto height and static types are very similar, the difference is
# important for CAD applications, but not for the DXF format itself.


@pytest.mark.parametrize('obj', [
    DYNAMIC_MANUAL_HEIGHT,
    DYNAMIC_AUTO_HEIGHT,
    STATIC
], ids=['DYN_MANUAL', 'DYN_AUTO', 'STATIC'])
def test_load_mtext_attribs_from_embedded_object(obj):
    embedded_obj = Tags.from_text(obj)
    dxf = MText().dxf
    dxf.rotation = 45

    load_columns_from_embedded_object(dxf, embedded_obj)
    assert dxf.width == 62.6
    assert dxf.text_direction == (1, 0, 0)
    assert dxf.hasattr('rotation') is False, "remove rotation attribute"
    assert dxf.insert == (69.8, 276.1, 0)


def test_load_dynamic_cols_manual_height():
    """ Every column can have a different height. """
    embedded_obj = Tags.from_text(DYNAMIC_MANUAL_HEIGHT)
    cols = load_columns_from_embedded_object(MText().dxf, embedded_obj)
    assert cols.count == 3
    assert cols.column_type == ColumnType.DYNAMIC_COLUMNS
    assert cols.auto_height is False
    assert cols.reversed_column_flow is False
    assert cols.defined_height == 0.0, "not defined if auto_height is False"
    assert cols.width == 50.0
    assert cols.gutter_width == 12.5
    assert cols.total_width == 175.0  # 3 * 50 + 2 * 12.5
    # total_height = max(heights) even if the last column is the tallest
    assert cols.total_height == 164.8
    assert cols.total_height == max(cols.heights)
    assert len(cols.linked_columns) == 0, "MTEXT is a single entity in R2018"
    assert len(cols.heights) == 3
    assert cols.heights[-1] == 0.0, "last column height has to be 0.0"
    assert cols.heights == [164.8, 154.3, 0.0]


def test_load_dynamic_cols_with_auto_height():
    """ All columns have the same column height. """
    embedded_obj = Tags.from_text(DYNAMIC_AUTO_HEIGHT)
    cols = load_columns_from_embedded_object(MText().dxf, embedded_obj)
    # Count is a calculated value, group code 72 (column height count) is 0!
    assert cols.count == 3
    assert cols.column_type == ColumnType.DYNAMIC_COLUMNS
    assert cols.auto_height is True
    assert cols.reversed_column_flow is False
    assert cols.defined_height == 158.1,  "required if auto_height is True"
    assert cols.width == 50.0
    assert cols.gutter_width == 12.5
    assert cols.total_width == 175.0  # 3 * 50 + 2 * 12.5
    assert cols.total_height == 158.1
    assert len(cols.linked_columns) == 0, "MTEXT is a single entity in R2018"
    assert len(cols.heights) == 0


def test_load_static_cols():
    """ All columns have the same column height. """
    embedded_obj = Tags.from_text(STATIC)
    cols = load_columns_from_embedded_object(MText().dxf, embedded_obj)
    assert cols.count == 3
    assert cols.column_type == ColumnType.STATIC_COLUMNS
    assert cols.auto_height is False
    assert cols.reversed_column_flow is False
    assert cols.defined_height == 150.0, "required for static columns"
    assert cols.width == 50.0
    assert cols.gutter_width == 12.5
    assert cols.total_width == 175.0  # 3 * 50 + 2 * 12.5
    assert cols.total_height == 150.0
    assert len(cols.linked_columns) == 0, "MTEXT is a single entity in R2018"
    assert len(cols.heights) == 0


if __name__ == '__main__':
    pytest.main([__file__])
