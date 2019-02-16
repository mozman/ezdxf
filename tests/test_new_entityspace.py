# Created: 2019-02-15
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.entitydb import EntitySpace
from ezdxf.order import priority, zorder


class Entity:
    def __init__(self, priority):
        self.priority = priority
        self.is_alive = True

    def __priority__(self):
        return self.priority


NUMBERS = [1, 4, 5, 6, 76, -4, 7]


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
    assert len(space) == 7, 'still 7 items'

    space.purge()
    assert len(space) == 6, 'removed dead entities'

    e = Entity(1)
    assert e not in space


def test_remove(space):
    e = space[3]
    space.remove(e)
    assert e not in space

    space.clear()
    assert len(space) == 0


def test_order_of_appearance(space):
    assert list(e.priority for e in space) == NUMBERS


def test_supports_priority_order(space):
    assert list(e.priority for e in priority(space)) == sorted(NUMBERS, reverse=True), 'highest priority first'


def test_supports_zorder(space):
    assert list(e.priority for e in zorder(space)) == sorted(NUMBERS), 'lowest priority first'


def test_reorder_no_order(space):
    space.reorder(order=0)
    assert list(e.priority for e in space) == NUMBERS


def test_reorder_zorder(space):
    space.reorder(order=2)
    assert list(e.priority for e in space) == sorted(NUMBERS), 'lowest priority first'


def test_reorder_priority(space):
    space.reorder(order=1)
    assert list(e.priority for e in space) == sorted(NUMBERS, reverse=True), 'highest priority first'



