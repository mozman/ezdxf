#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.acis import load


def test_load_any_format(any_cube):
    bodies = load(any_cube)
    assert len(bodies) == 1


if __name__ == "__main__":
    pytest.main([__file__])
