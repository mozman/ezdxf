#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
import pytest
from ezdxf.entities import DXFEntity
from ezdxf import reorder


@pytest.fixture()
def entities():
    return [
        DXFEntity.new(handle='A'),
        DXFEntity.new(handle='D'),
        DXFEntity.new(handle='B'),
        DXFEntity.new(handle='C'),
    ]


def test_default_sort_structure(entities):
    int_handles = [k for k, i, e in reorder.sort_structure(entities, {})]
    assert int_handles == [10, 13, 11, 12]


def test_mapped_sort_structure(entities):
    int_handles = [k for k, i, e in
                   reorder.sort_structure(entities, {'D': 'FF'})]
    assert int_handles == [10, 255, 11, 12]


def test_ascending_sort_order(entities):
    handles = [e.dxf.handle for e in reorder.ascending(entities)]
    assert handles == ['A', 'B', 'C', 'D']


def test_mapped_ascending_sort_order(entities):
    handles = [e.dxf.handle for e in reorder.ascending(entities, {'B': 'D'})]
    # B has the same sort handle as D and D & B should show up in source order
    assert handles == ['A', 'C', 'D', 'B']


def test_full_mapped_ascending_sort_order(entities):
    handles = [e.dxf.handle for e in reorder.ascending(entities, {
        'A': 'A',
        'B': 'A',
        'C': 'A',
        'D': 'A',
    })]
    assert handles == ['A', 'D', 'B', 'C'], 'Expected the source entity order'


def test_descending_sort_order(entities):
    handles = [e.dxf.handle for e in reorder.descending(entities)]
    assert handles == ['D', 'C', 'B', 'A']


def test_full_mapped_descending_sort_order(entities):
    handles = [e.dxf.handle for e in reorder.descending(entities, {
        'A': 'A',
        'B': 'A',
        'C': 'A',
        'D': 'A',
    })]
    assert handles == ['C', 'B', 'D', 'A'], \
        'Expected the reversed source entity order'


if __name__ == '__main__':
    pytest.main([__file__])
