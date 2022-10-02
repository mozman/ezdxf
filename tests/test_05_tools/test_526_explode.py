#  Copyright (c) 2021-2022, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf import explode
from ezdxf.layouts import Modelspace


@pytest.fixture(scope="module")
def msp() -> Modelspace:
    doc = ezdxf.new()
    block = doc.blocks.new("BLK1")
    block.add_line((0, 0), (1, 0))
    return doc.modelspace()


def test_virtual_entities_from_insert(msp: Modelspace):
    insert = msp.add_blockref("BLK1", (0, 0))
    result = list(explode.virtual_block_reference_entities(insert))
    assert len(result) == 1


def test_transparency_of_virtual_entities_from_insert(msp: Modelspace):
    insert = msp.add_blockref("BLK1", (0, 0))
    line = list(explode.virtual_block_reference_entities(insert))[0]
    assert line.transparency == 0.0
    assert line.dxf.hasattr("transparency") is False


def test_complex_target_coordinate_system(msp: Modelspace):
    doc = msp.doc
    block2 = doc.blocks.new("BLK2")
    insert0 = block2.add_blockref("BLK1", (0, 0))
    insert0.dxf.rotation = 30
    insert0.dxf.xscale = 7
    insert0.dxf.yscale = 3
    insert0.dxf.zscale = 1

    # this raises an internal InsertTransformationError!
    insert0.dxf.extrusion = (1, 1, 1)

    insert = msp.add_blockref("BLK2", (0, 0))
    insert.dxf.rotation = 30
    insert.dxf.xscale = 2
    insert.dxf.yscale = -5
    insert.dxf.zscale = 1

    line = list(explode.virtual_block_reference_entities(insert))[0]
    assert line.dxf.start.isclose((0, 0, 0))
    assert line.dxf.end.isclose(
        (-2.755149853494064, -18.089844737258662, 2.857738033247041)
    )


if __name__ == "__main__":
    pytest.main([__file__])
