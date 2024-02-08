# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
# pylint: disable=all
import pytest

from ezdxf.tools import take2, pairwise


class TestTake2:
    def test_empty_list(self):
        assert len(list(take2([]))) == 0

    def test_1_item(self):
        assert len(list(take2([1]))) == 0

    def test_2_items(self):
        assert list(take2([1, 2])) == [(1, 2)]

    def test_3_items(self):
        assert list(take2([1, 2, 3])) == [(1, 2)]

    def test_4_items(self):
        assert list(take2([1, 2, 3, 4])) == [(1, 2), (3, 4)]

class TestPairwiseOpen:
    def test_empty_list(self):
        assert len(list(pairwise([]))) == 0

    def test_1_item(self):
        assert len(list(pairwise([1]))) == 0

    def test_2_items(self):
        assert list(pairwise([1, 2])) == [(1, 2)]

    def test_3_items(self):
        assert list(pairwise([1, 2, 3])) == [(1, 2), (2, 3)]

class TestPairwiseClose:
    def test_empty_list(self):
        assert len(list(pairwise([], close=True))) == 0

    def test_1_item(self):
        assert len(list(pairwise([1], close=True))) == 0

    def test_2_items(self):
        assert list(pairwise([1, 2], close=True)) == [(1, 2), (2, 1)]

    def test_3_items(self):
        assert list(pairwise([1, 2, 3], close=True)) == [(1, 2), (2, 3), (3, 1)]


if __name__ == '__main__':
    pytest.main([__file__])