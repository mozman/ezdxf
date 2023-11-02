#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf import appsettings
from ezdxf.math import Vec3


def test_update_extents():
    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_line((0, 0), (7, 8, 9))
    appsettings.update_extents(doc)

    assert msp.dxf.extmin.isclose((0, 0))
    assert msp.dxf.extmax.isclose((7, 8, 9))

    assert Vec3(0, 0).isclose(doc.header["$EXTMIN"])
    assert Vec3(7, 8, 9).isclose(doc.header["$EXTMAX"])


if __name__ == "__main__":
    pytest.main([__file__])
