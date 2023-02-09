#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest

from ezdxf.entities import LWPolyline
from ezdxf.math import BoundingBox
from ezdxf.path import make_path, tools
from ezdxf.disassemble import make_primitive


@pytest.fixture
def lwpolyline() -> LWPolyline:
    # Issue 414 shows an error in the bounding box calculation for a closed
    # LWPOLYLINE representing a filled circle (const_width=0.45) and an
    # inverted extrusion (0, 0, -1).
    #
    # original data of the LWPOLYLINE:
    # [
    #     (-43710.28841108403, 19138.631023711587, 0.0, 0.0, -1.0),
    #     (-43710.28841108403, 19139.079023711445, 0.0, 0.0, -1.0),
    # ]
    # simplified test data:
    points = [(-10.0, 1.0, 0.0, 0.0, -1.0), (-10.0, 1.45, 0.0, 0.0, -1.0)]
    pline = LWPolyline.new(
        dxfattribs={"extrusion": (0, 0, -1), "const_width": 0.45}
    )
    pline.append_points(points)
    pline.close()
    return pline


class TestMakePath:
    def test_WCS_calculation(self, lwpolyline):
        vertices = list(lwpolyline.vertices_in_wcs())
        assert vertices[0].isclose((10, 1, 0))
        assert vertices[1].isclose((10, 1.45, 0))

    def test_make_path(self, lwpolyline):
        p = make_path(lwpolyline)
        assert p.start.isclose((10, 1, 0))
        assert p.is_closed is True

    def test_bounding_box_calculation(self, lwpolyline):
        box = tools.bbox([make_path(lwpolyline)], fast=True)
        assert box.extmin.isclose((9.775, 1.0))
        assert box.extmax.isclose((10.225, 1.45))
        assert box.center.isclose((10, 1.225))
        assert box.size.isclose((0.45, 0.45))

    # Conclusion: Everything works fine at the path level, therefore the
    # error has to be in the ezdxf.disassemble module which converts entities
    # into primitives and which is also the base for the bounding box
    # calculation of the ezdxf.bbox module.


class TestMakePrimitive:
    # Issue was caused by the make_primitive() function for LWPOLYLINE including
    # width values, which creates a TraceBuilder() in OCS, but the
    # transformation into WCS as missing.
    def test_make_primitive(self, lwpolyline):
        p = make_primitive(lwpolyline)
        assert p.path is None, "LWPOLYLINE has width and is a mesh"
        assert p.mesh is not None

    def test_bounding_box_calculation(self, lwpolyline):
        p = make_primitive(lwpolyline)
        box = BoundingBox(p.vertices())
        assert box.center.isclose((10, 1.225))
        assert box.size.isclose((0.90, 0.90))


if __name__ == "__main__":
    pytest.main([__file__])
