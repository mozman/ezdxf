# Created: 10.03.2011
# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
from io import StringIO
from copy import deepcopy
from ezdxf.lldxf.tags import Tags, DXFTag
from ezdxf.lldxf.tagwriter import TagWriter
from ezdxf.lldxf.const import DXFValueError

TEST_TAGREADER = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1018
  9
$DWGCODEPAGE
  3
ANSI_1252
  0
ENDSEC
  0
EOF
"""

TEST_TAGREADER_COMMENTS = """999
Comment0
  0
SECTION
  2
HEADER
  9
$ACADVER
999
Comment1
  1
AC1018
  9
$DWGCODEPAGE
  3
ANSI_1252
  0
ENDSEC
  0
EOF
"""

TESTHANDLE5 = """ 0
TEST
  5
F5
"""

TESTHANDLE105 = """ 0
TEST
105
F105
"""

TESTFINDALL = """  0
TEST0
  0
TEST1
  0
TEST2
"""

TAGS_WITH_VERTEX = """  0
TEST
 10
1.0
 20
2.0
 30
3.0
"""


class HandlesMock:
    calls = 0

    @property
    def next(self):
        self.calls += 1
        return 'FF'


class TestTags:
    @pytest.fixture
    def tags(self):
        return Tags.from_text(TEST_TAGREADER)

    def test_from_text(self, tags):
        assert 8, len(tags)

    def test_write(self, tags):
        stream = StringIO()
        tagwriter = TagWriter(stream)
        tagwriter.write_tags(tags)
        result = stream.getvalue()
        stream.close()
        assert TEST_TAGREADER == result

    def test_update(self, tags):
        tags.update(DXFTag(2, 'XHEADER'))
        assert 'XHEADER' == tags[1].value

    def test_update_error(self, tags):
        with pytest.raises(DXFValueError):
            tags.update(DXFTag(999, 'DOESNOTEXIST'))

    def test_set_first(self, tags):
        tags.set_first(DXFTag(999, 'NEWTAG'))
        assert 'NEWTAG' == tags[-1].value

    def test_find_first(self, tags):
        value = tags.get_first_value(9)
        assert '$ACADVER' == value

    def test_find_first_default(self, tags):
        value = tags.get_first_value(1234, default=999)
        assert 999 == value

    def test_find_first_error(self, tags):
        with pytest.raises(DXFValueError):
            tags.get_first_value(1234)

    def test_get_handle_5(self):
        tags = Tags.from_text(TESTHANDLE5)
        assert 'F5' == tags.get_handle()

    def test_get_handle_105(self):
        tags = Tags.from_text(TESTHANDLE105)
        assert 'F105' == tags.get_handle()

    def test_get_handle_create_new(self, tags):
        with pytest.raises(DXFValueError):
            tags.get_handle()

    def test_find_all(self):
        tags = Tags.from_text(TESTFINDALL)
        assert 3 == len(tags.find_all(0))

    def test_tag_index(self):
        tags = Tags.from_text(TESTFINDALL)
        index = tags.tag_index(0)
        assert 0 == index
        index = tags.tag_index(0, index + 1)
        assert 1 == index

    def test_find_first_value_error(self):
        tags = Tags.from_text(TESTFINDALL)
        with pytest.raises(DXFValueError):
            tags.tag_index(1)

    def test_clone_is_equal(self, tags):
        clone = tags.clone()
        assert id(tags) != id(clone)
        assert tags == clone

    def test_clone_is_independent(self, tags):
        clone = tags.clone()
        clone.pop()
        assert self.tags != clone

    def test_deepcopy(self):
        tags = Tags.from_text(TAGS_WITH_VERTEX)
        assert len(tags) == 2
        v = tags[1]
        assert v.value == (1., 2., 3.)

        tags2 = deepcopy(tags)
        assert id(tags) != id(tags2)
        assert tags == tags2, "same content"
        # same ids, DXFTags are immutable
        assert id(v) == id(tags[1])

    def test_replace_handle_5(self):
        tags = Tags.from_text(TESTHANDLE5)
        tags.replace_handle('AA')
        assert 'AA' == tags.get_handle()

    def test_replace_handle_105(self):
        tags = Tags.from_text(TESTHANDLE105)
        tags.replace_handle('AA')
        assert 'AA' == tags.get_handle()

    def test_replace_no_handle_without_error(self, tags):
        tags.replace_handle('AA')
        with pytest.raises(DXFValueError):
            tags.get_handle()  # handle still doesn't exist

    def test_remove_tags(self, tags):
        tags.remove_tags(codes=(0,))
        assert 5 == len(tags)

    def test_strip_tags(self, tags):
        tags.remove_tags(codes=(0,))
        result = Tags.strip(tags, codes=(0,))
        assert 5 == len(result)
        assert isinstance(result, Tags)

    def test_has_tag(self, tags):
        assert tags.has_tag(2)

    def test_has_not_tag(self, tags):
        assert tags.has_tag(7) is False


DUPLICATETAGS = """  0
FIRST
  0
LAST
  1
TEST2
"""

COLLECT_1 = """  0
ZERO
  1
ONE
  2
TWO
  3
THREE
  4
FOUR
  0
ZERO
  1
ONE
  2
TWO
  3
THREE
  4
FOUR
"""


class TestTagsCollect:
    @pytest.fixture
    def tags(self):
        return Tags.from_text(COLLECT_1)

    def test_with_start_param(self, tags):
        collected_tags = tags.collect_consecutive_tags([1, 2, 3], start=1)
        assert 3 == len(collected_tags)
        assert "THREE" == collected_tags[2].value

    def test_with_end_param(self, tags):
        collected_tags = tags.collect_consecutive_tags([0, 1, 2, 3], end=3)
        assert 3 == len(collected_tags)
        assert "TWO" == collected_tags[2].value

    def test_with_start_and_end_param(self, tags):
        collected_tags = tags.collect_consecutive_tags([1, 2, 3], start=6, end=9)
        assert 3 == len(collected_tags)
        assert "THREE" == collected_tags[2].value

    def test_none_existing_codes(self, tags):
        collected_tags = tags.collect_consecutive_tags([7, 8, 9])
        assert 0 == len(collected_tags)

    def test_all_codes(self, tags):
        collected_tags = tags.collect_consecutive_tags([0, 1, 2, 3, 4])
        assert 10 == len(collected_tags)

    def test_emtpy_tags(self):
        tags = Tags()
        collected_tags = tags.collect_consecutive_tags([0, 1, 2, 3, 4])
        assert 0 == len(collected_tags)
