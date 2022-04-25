#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf import acis


def test_new_acis_tree():
    atree = acis.new_tree()
    assert atree.header is not None


if __name__ == "__main__":
    pytest.main([__file__])
