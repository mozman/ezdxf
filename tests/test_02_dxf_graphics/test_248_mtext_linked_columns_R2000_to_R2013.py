#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest

import ezdxf
from ezdxf.entities.mtext import (
    load_columns_from_xdata, MText, ColumnType, MTextColumns,
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
    assert cols.column_type == ColumnType.DYNAMIC
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
    assert cols.column_type == ColumnType.DYNAMIC
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
    assert cols.column_type == ColumnType.STATIC
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


def new_mtext_with_linked_columns(count=3) -> MText:
    columns = MTextColumns()
    columns.count = count
    columns.width = 10
    columns.gutter_width = 0.5
    columns.defined_height = 50
    mtext = MText.new()
    mtext.setup_columns(columns, linked=True)
    return mtext


def test_create_new_mtext_with_linked_columns():
    mtext = new_mtext_with_linked_columns(3)
    columns = mtext.columns
    assert columns.column_type == ColumnType.STATIC
    assert len(columns.linked_columns) == 2
    assert len(columns.heights) == 0, "all columns have the same defined height"
    assert mtext.dxf.width == columns.width
    assert columns.total_height == columns.defined_height
    assert columns.total_width == 31

    # default location and text direction:
    assert mtext.dxf.insert == (0, 0, 0)
    assert mtext.dxf.text_direction == (1, 0, 0)

    for column in columns.linked_columns:
        assert column.columns is None
        assert column.dxf.width == columns.width
        assert column.dxf.defined_height == columns.defined_height
        assert column.dxf.text_direction == (1, 0, 0)

    col0, col1 = columns.linked_columns
    assert col0.dxf.insert == (10.5, 0, 0)
    assert col1.dxf.insert == (21, 0, 0)


def test_destroy_mtext_with_linked_columns():
    mtext = new_mtext_with_linked_columns(3)
    columns = mtext.columns
    mtext.destroy()
    assert mtext.is_alive is False
    for col in columns.linked_columns:
        assert col.is_alive is False


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new('R2013')


def test_add_mtext_with_linked_columns_to_entitydb(doc):
    db = doc.entitydb
    mtext = new_mtext_with_linked_columns(3)
    count = len(db)
    doc.entitydb.add(mtext)
    assert len(db) == count + 3, "should add all columns to the entitydb"
    columns = mtext.columns
    for col in columns.linked_columns:
        assert col.dxf.handle is not None
        assert col.dxf.handle in db, "should be stored in the entity db"


def test_add_mtext_with_linked_columns_to_msp(doc):
    msp = doc.modelspace()
    mtext = new_mtext_with_linked_columns(3)
    count = len(msp)
    msp.add_entity(mtext)
    assert len(msp) == count + 1, "should only add the main column to the msp"

    columns = mtext.columns
    db = doc.entitydb
    for col in columns.linked_columns:
        assert col.dxf.handle is not None
        assert col.dxf.handle in db, "should be stored in the entity db"
        assert col.dxf.owner is None, "should not be stored in an entity space"


def test_delete_mtext_with_linked_columns_from_entitydb(doc):
    """ Delete MTEXT by EntityDB.delete_entity(). """
    db = doc.entitydb
    mtext = new_mtext_with_linked_columns(3)
    doc.entitydb.add(mtext)
    count = len(db)
    doc.entitydb.delete_entity(mtext)
    db.purge()
    assert len(db) == count - 3, "should delete all columns from entitydb"


def test_discard_mtext_with_linked_columns_from_entitydb(doc):
    """ Discard MTEXT columns from entitydb, but do not destroy the entities. """
    db = doc.entitydb
    mtext = new_mtext_with_linked_columns(3)
    doc.entitydb.add(mtext)
    count = len(db)
    doc.entitydb.discard(mtext)
    assert len(db) == count - 3, "should discard all columns from entitydb"
    assert mtext.is_alive is True
    for col in mtext.columns.linked_columns:
        assert col.is_alive is True


def test_destroy_mtext_with_linked_columns_from_entitydb(doc):
    """ Delete MTEXT from EntityDB using MText.destroy(). """
    db = doc.entitydb
    mtext = new_mtext_with_linked_columns(3)
    doc.entitydb.add(mtext)
    count = len(db)
    mtext.destroy()
    db.purge()
    assert len(db) == count - 3, "should delete all columns from entitydb"


if __name__ == '__main__':
    pytest.main([__file__])
