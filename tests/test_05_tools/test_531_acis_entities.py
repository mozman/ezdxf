#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.acis import Loader


def test_load_sab(cube_sab):
    loader = Loader.load_sab(cube_sab)
    assert len(loader.bodies) == 1


if __name__ == '__main__':
    pytest.main([__file__])
