#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest

bezier = pytest.importorskip('ezdxf.acc.bspline')

if __name__ == '__main__':
    pytest.main([__file__])
