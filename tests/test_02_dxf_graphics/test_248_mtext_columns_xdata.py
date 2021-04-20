#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.entities.mtext import (
    load_columns_from_xdata, MText, ColumnType,
)
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.entities.xdata import XData

DYNAMIC_MANUAL_HEIGHT = """0
MTEXT
5
9C
330
1F
100
AcDbEntity
8
0
100
AcDbMText
1001
ACAD
1000
ACAD_MTEXT_COLUMN_INFO_BEGIN
1070
75
1070
2
1070
79
1070
0
1070
76
1070
3
1070
78
1070
0
1070
48
1040
50.0
1070
49
1040
12.5
1070
50
1070
3
1040
164.8
1040
154.3
1040
0.0
1000
ACAD_MTEXT_COLUMN_INFO_END
1000
ACAD_MTEXT_COLUMNS_BEGIN
1070
47
1070
3
1005
238
1005
239
1000
ACAD_MTEXT_COLUMNS_END
"""

DYNAMIC_AUTO_HEIGHT = """0
MTEXT
5
A2
330
1F
100
AcDbEntity
8
0
100
AcDbMText
1001
ACAD
1000
ACAD_MTEXT_COLUMN_INFO_BEGIN
1070
75
1070
2
1070
79
1070
1
1070
76
1070
3
1070
78
1070
0
1070
48
1040
50.0
1070
49
1040
12.5
1000
ACAD_MTEXT_COLUMN_INFO_END
1000
ACAD_MTEXT_COLUMNS_BEGIN
1070
47
1070
3
1005
23C
1005
23D
1000
ACAD_MTEXT_COLUMNS_END
1000
ACAD_MTEXT_DEFINED_HEIGHT_BEGIN
1070
46
1040
158.1
1000
ACAD_MTEXT_DEFINED_HEIGHT_END
"""

STATIC = """0
MTEXT
5
9D
330
1F
100
AcDbEntity
8
0
100
AcDbMText
1001
ACAD
1000
ACAD_MTEXT_COLUMN_INFO_BEGIN
1070
75
1070
1
1070
79
1070
0
1070
76
1070
3
1070
78
1070
0
1070
48
1040
50.0
1070
49
1040
12.5
1000
ACAD_MTEXT_COLUMN_INFO_END
1000
ACAD_MTEXT_COLUMNS_BEGIN
1070
47
1070
3
1005
23A
1005
23B
1000
ACAD_MTEXT_COLUMNS_END
1000
ACAD_MTEXT_DEFINED_HEIGHT_BEGIN
1070
46
1040
150.0
1000
ACAD_MTEXT_DEFINED_HEIGHT_END
"""

NO_COLUMN_INFO = """0
MTEXT
5
9D
330
1F
100
AcDbEntity
8
0
100
AcDbMText
1001
ACAD
"""


# The dynamic auto height and static types are very similar, the difference is
# important for CAD applications, but not for the DXF format itself.

def get_xdata(txt: str):
    tags = ExtendedTags.from_text(txt)
    return XData(tags.xdata)


def test_load_dynamic_cols_manual_height():
    """ Every column can have a different height.

    The linked MTEXT entities do NOT have the "defined_height" stored in the
    XDATA section ACAD. The only source for the column height is the
    MTextColumns.heights list.

    The linked MTEXT entities do not have an ACAD section at all.

    """
    xdata = get_xdata(DYNAMIC_MANUAL_HEIGHT)
    cols = load_columns_from_xdata(MText().dxf, xdata)
    assert cols.count == 3
    assert cols.column_type == ColumnType.DYNAMIC_COLUMNS
    assert cols.auto_height is False
    assert cols.reversed_column_flow is False
    assert cols.defined_height == 0.0, "not defined if auto_height is False"
    assert cols.width == 50.0
    assert cols.gutter_width == 12.5
    assert cols.total_width == 175.0  # 3 * 50 + 2 * 12.5
    # total_height = max(heights) even if the last column is the tallest
    assert cols.total_height == 164.8  # max height
    assert len(cols.linked_handles) == 2
    assert len(cols.heights) == 3  # not stored the main MTEXT entity
    assert cols.heights[-1] == 0.0, "last column height has to be 0.0"
    assert cols.heights == [164.8, 154.3, 0.0]


def test_load_dynamic_cols_with_auto_height():
    """ All columns have the same column height.

    Each linked MTEXT has the "defined_height" stored in the XDATA section ACAD.

    """
    xdata = get_xdata(DYNAMIC_AUTO_HEIGHT)
    cols = load_columns_from_xdata(MText().dxf, xdata)
    # Count is a calculated value, group code 72 (column height count) is 0!
    assert cols.count == 3
    assert cols.column_type == ColumnType.DYNAMIC_COLUMNS
    assert cols.auto_height is True
    assert cols.reversed_column_flow is False
    assert cols.defined_height == 158.1, "required if auto_height is True"
    assert cols.width == 50.0
    assert cols.gutter_width == 12.5
    assert cols.total_width == 175.0  # 3 * 50 + 2 * 12.5
    assert cols.total_height == 158.1
    assert len(cols.linked_handles) == 2
    assert len(cols.heights) == 0


def test_load_static_cols():
    """ All columns have the same column height.

    Each linked MTEXT has the "defined_height" stored in the XDATA section ACAD.

    """
    xdata = get_xdata(STATIC)
    cols = load_columns_from_xdata(MText().dxf, xdata)
    assert cols.count == 3
    assert cols.column_type == ColumnType.STATIC_COLUMNS
    assert cols.auto_height is False
    assert cols.reversed_column_flow is False
    assert cols.defined_height == 150.0, "required for static columns"
    assert cols.width == 50.0
    assert cols.gutter_width == 12.5
    assert cols.total_width == 175.0  # 3 * 50 + 2 * 12.5
    assert cols.total_height == 150.0
    assert len(cols.linked_handles) == 2
    assert len(cols.heights) == 0


def test_mtext_without_column_info():
    xdata = get_xdata(NO_COLUMN_INFO)
    cols = load_columns_from_xdata(MText().dxf, xdata)
    assert cols is None


def make_mtext(txt: str) -> MText:
    mtext = MText()
    xdata = get_xdata(txt)
    mtext._columns = load_columns_from_xdata(mtext.dxf, xdata)
    return mtext


@pytest.mark.parametrize('txt', [
    STATIC, DYNAMIC_AUTO_HEIGHT, DYNAMIC_MANUAL_HEIGHT
], ids=['STATIC', 'DYNAMIC_AUTO', 'DYNAMIC_MANUAL'])
def test_set_columns_xdata(txt):
    """ Create column data as XDATA for DXF versions before R2018. """
    mtext = make_mtext(txt)
    mtext.set_column_xdata()
    acad = mtext.xdata.get('ACAD')
    expected_xdata = get_xdata(txt)
    assert acad == expected_xdata.get('ACAD')


if __name__ == '__main__':
    pytest.main([__file__])
