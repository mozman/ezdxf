import pytest

from ezdxf.lldxf.validator import entity_structure_validator
from ezdxf.lldxf.tagger import internal_tag_compiler
from ezdxf import DXFAppDataError, DXFXDataError

def test_valid_tags():
    tags = list(entity_structure_validator(internal_tag_compiler(VALID_ENTITY)))
    assert len(tags) == 6


# The structure validator does not know anything about entities, except its basic tag structure
VALID_ENTITY = """0
LINE
102
{APP
40
1
102
}
1001
TEST
1000
STRING
"""


def test_invalid_app_data_without_closing_tag():
    with pytest.raises(DXFAppDataError):
        list(entity_structure_validator(internal_tag_compiler(INVALID_APPDATA_NO_CLOSING_TAG)))


INVALID_APPDATA_NO_CLOSING_TAG = """0
LINE
102
{APP
40
1
1001
TEST
1000
STRING
"""


def test_invalid_app_data_without_opening_tag():
    with pytest.raises(DXFAppDataError):
        list(entity_structure_validator(internal_tag_compiler(INVALID_APPDATA_NO_OPENING_TAG)))


INVALID_APPDATA_NO_OPENING_TAG = """0
LINE
102
}
40
1
1001
TEST
1000
STRING
"""


def test_invalid_app_data_structure_tag():
    with pytest.raises(DXFAppDataError):
        list(entity_structure_validator(internal_tag_compiler(INVALID_APPDATA_STRUCTURE_TAG)))


INVALID_APPDATA_STRUCTURE_TAG = """0
LINE
102
INVALID_APPDATA_STRUCTURE_TAG
40
1
1001
TEST
1000
STRING
"""


def test_invalid_xdata():
    with pytest.raises(DXFXDataError):
        list(entity_structure_validator(internal_tag_compiler(INVALID_XDATA_STRUCTURE_TAG)))


INVALID_XDATA_STRUCTURE_TAG = """0
LINE
40
1
1001
TEST
1000
STRING
1
NO GROUP CODE < 1000 in XDATA SECTION
"""


def test_unbalanced_xdata_list_1():
    with pytest.raises(DXFXDataError):
        list(entity_structure_validator(internal_tag_compiler(UNBALANCED_XDATA_LIST_1)))


UNBALANCED_XDATA_LIST_1 = """0
LINE
40
1
1001
TEST
1000
STRING
1002
{
1002
{
1002
}
"""


def test_unbalanced_xdata_list_2():
    with pytest.raises(DXFXDataError):
        list(entity_structure_validator(internal_tag_compiler(UNBALANCED_XDATA_LIST_2)))


UNBALANCED_XDATA_LIST_2 = """0
LINE
40
1
1001
TEST
1000
STRING
1002
{
1002
{
1002
}
"""


def test_invalid_xdata_list_nesting():
    with pytest.raises(DXFXDataError):
        list(entity_structure_validator(internal_tag_compiler(INVALID_XDATA_LIST_NESTING)))


INVALID_XDATA_LIST_NESTING = """0
LINE
40
1
1001
TEST
1000
STRING
1002
{
1002
}
1002
}
1002
{
"""


if __name__ == '__main__':
    pytest.main([__file__])

