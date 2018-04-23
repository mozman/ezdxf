# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.tools.indexing import Index


def test_item_index():
    index = Index(5)
    assert index.index(2) == 2
    assert index.index(7) == 7  # IndexError if used in sequences
    assert index.index(0) == 0
    assert index.index(-1) == 4
    assert index.index(-5) == 0
    assert index.index(-6) == -1  # IndexError if used in sequences


@pytest.fixture
def check_list():
    return list(range(100))


def test_slicing_ascending_order(check_list):
    i = Index(check_list)
    assert list(i.slicing(1000)) == check_list[:]
    assert list(i.slicing(10, 50)) == check_list[10:50]
    assert list(i.slicing(10, 50, 3)) == check_list[10:50:3]
    assert list(i.slicing(10, 50, -3)) == check_list[10:50:-3]
    assert list(i.slicing(10, -30)) == check_list[10:-30]
    assert list(i.slicing(-70, -30, 7)) == check_list[-70:-30:7]
    assert list(i.slicing(-70, -30, -7)) == check_list[-70:-30:-7]

    with pytest.raises(ValueError):
        list(i.slicing(10, 50, 0))


def test_slicing_descending_order(check_list):
    i = Index(check_list)
    assert list(i.slicing(50, 10, -1)) == check_list[50:10:-1]
    assert list(i.slicing(50, 10, -7)) == check_list[50:10:-7]
    assert list(i.slicing(50, 10, 1)) == check_list[50:10:1]
    assert list(i.slicing(-1, -10, -1)) == check_list[-1:-10:-1]
    assert list(i.slicing(-1, -10, -3)) == check_list[-1:-10:-3]
