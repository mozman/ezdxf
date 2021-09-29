#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.lldxf.attributes import (
    DXFAttr,
    DefSubclass,
    group_code_mapping,
    XType,
)

acdb_unique = DefSubclass(
    "AcDbUniqueGroupCodes",
    {
        "n1": DXFAttr(1),
        "n2": DXFAttr(2),
        "n3": DXFAttr(3),
        "n4": DXFAttr(4),
        "n5": DXFAttr(5, xtype=XType.callback),
    },
)

acdb_dublicates = DefSubclass(
    "AcDbDuplicateGroupCodes",
    {
        "n1": DXFAttr(1),
        "n2": DXFAttr(1),
        "n3": DXFAttr(1),
        "n4": DXFAttr(2),
        "n5": DXFAttr(2),
        "n6": DXFAttr(3),
    },
)


def test_unique_group_codes():
    m = group_code_mapping(acdb_unique)
    assert len(m) == 5
    assert set(type(v) for v in m.values()) == {str}


def test_ignored_group_codes():
    # These group codes are ignored from logging as unprocessed tags, which
    # would happen if they are just left out:
    m = group_code_mapping(acdb_unique, ignore=(1, 2))
    assert m[1] == "*IGNORE"
    assert m[2] == "*IGNORE"


def test_duplicate_group_codes():
    m = group_code_mapping(acdb_dublicates)
    assert m[1] == ["n1", "n2", "n3"]
    assert m[2] == ["n4", "n5"]
    assert m[3] == "n6"


def test_if_callbacks_are_marked():
    m = group_code_mapping(acdb_unique)
    assert m[5] == "*n5", 'callbacks have to marked with a leading "*"'


if __name__ == "__main__":
    pytest.main([__file__])
