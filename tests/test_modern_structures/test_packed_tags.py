# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.lldxf.packedtags import TagArray, TagDict, MultiTagArray


@pytest.fixture()
def numbers():
    return [1, 2, 3, 4]


def test_tag_array_init(numbers):
    code = 60  # integer
    array = TagArray(code=code, values=numbers, dtype='i')
    assert array.code == code
    for index, value in enumerate(array.values):
        assert value == numbers[index]


def test_tag_array_dxf_tags(numbers):
    code = 60  # integer
    array = TagArray(code=code, values=numbers, dtype='i')
    tags = list(array.dxftags())
    assert len(tags) == len(numbers)
    for index, value in enumerate(tags):
        assert value == (code, numbers[index])
