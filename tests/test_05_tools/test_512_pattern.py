# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.tools import pattern


def test_load():
    old_pattern = pattern.load(old_pattern=True)
    assert 'ANSI31' in old_pattern

    p = pattern.load(old_pattern=False)
    assert 'ANSI31' in p

    l1 = p['ANSI31'][0]
    l2 = old_pattern['ANSI31'][0]

    assert l1[2] == (-2.2627, 2.2627)
    assert l2[2] == (-0.0884, 0.0884)


def test_scale_pattern():
    p = pattern.load(old_pattern=False)
    ansi31 = p['ANSI31']
    s = pattern.scale_pattern(ansi31, 2, rotate=90)

    angle, base, offset, lines = s[0]
    assert angle == 135
    assert base == (0, 0)
    assert offset == (-4.5254, -4.5254)


if __name__ == '__main__':
    pytest.main([__file__])

