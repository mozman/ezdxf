# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

import pytest
import ezdxf


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new()


def test_new_group(doc):
    msp = doc.modelspace()
    group = doc.groups.new('test1')
    with group.edit_data() as g:
        g.append(msp.add_point((0, 0)))
        g.append(msp.add_line((1, 1), (2, 2)))
    assert len(group) == 2
    assert group[0].dxftype() == 'POINT'
    assert group[1].dxftype() == 'LINE'
    assert len(list(group.handles())) == 2
    handle = group[0].dxf.handle
    assert handle in group


def test_unique_groups(doc):
    doc.groups.new('test2')
    with pytest.raises(ValueError):
        doc.groups.new('test2')


def test_modify_group(doc):
    msp = doc.modelspace()
    group = doc.groups.new('test3')
    with group.edit_data() as g:
        g.append(msp.add_point((0, 0)))
        g.append(msp.add_line((1, 1), (2, 2)))
    assert len(group) == 2
    e = [
        msp.add_point((3, 3)),
        msp.add_point((4, 4)),
    ]
    group.extend(e)
    assert len(group) == 4


def test_remove_invalid_handles(doc):
    pass


if __name__ == '__main__':
    pytest.main([__file__])
