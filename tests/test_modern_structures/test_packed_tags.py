# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.lldxf.packedtags import TagArray, TagDict


@pytest.fixture()
def numbers():
    return [1, 2, 3, 4]


def test_tag_array_init(numbers):
    code = 60  # integer
    array = TagArray(code=code, value=numbers, dtype='i')
    assert array.code == code
    for index, value in enumerate(array.value):
        assert value == numbers[index]


def test_tag_array_dxf_tags(numbers):
    code = 60  # integer
    array = TagArray(code=code, value=numbers, dtype='i')
    tags = list(array.dxftags())
    assert len(tags) == len(numbers)
    for index, value in enumerate(tags):
        assert value == (code, numbers[index])


def test_tag_array_clone(numbers):
    code = 60  # integer
    array = TagArray(code=code, value=numbers, dtype='i')
    array2 = array.clone()
    array2.value[-1] = 9999
    assert array.value[:-1] == array2.value[:-1]
    assert array.value[-1] != array2.value[-1]
