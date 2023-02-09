# Created: 2019-02-15
# Copyright (c) 2019-2020, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.entitydb import EntitySpace


class Entity:
    def __init__(self, value):
        self.value = value
        self.is_alive = True


@pytest.fixture
def space():
    return EntitySpace(Entity(p) for p in [1, 4, 5, 6, 76, -4, 7])


def test_init(space):
    assert len(EntitySpace()) == 0
    assert len(space) == 7


def test_existence(space):
    e = space[3]
    assert e in space

    assert len(space) == 7
    e.is_alive = False
    assert e not in space
    assert len(space) == 7, "still 7 items"

    space.purge()
    assert len(space) == 6, "removed dead entities"

    e = Entity(1)
    assert e not in space


def test_remove(space):
    e = space[3]
    space.remove(e)
    assert e not in space

    space.clear()
    assert len(space) == 0
