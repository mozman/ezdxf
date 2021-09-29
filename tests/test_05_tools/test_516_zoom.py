#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import cast
import pytest
import ezdxf
from ezdxf import zoom, bbox


class TestModelSpace:
    @pytest.fixture(scope="class")
    def msp(self):
        doc = ezdxf.new()
        msp_ = doc.modelspace()
        msp_.add_point((-25, -25))
        msp_.add_point((25, 25))
        msp_.add_point((-100, -50))
        msp_.add_point((100, 50))
        return msp_

    def test_zoom_center(self, msp):
        zoom.center(msp, (10, 10), (10, 10))
        vp = msp.doc.viewports.get("*Active")[0]
        assert vp.dxf.center == (10, 10)
        assert vp.dxf.height == 10

    def test_zoom_extents(self, msp):
        zoom.extents(msp)
        vp = msp.doc.viewports.get("*Active")[0]
        assert vp.dxf.center == (0, 0)
        # 2:1 = 200 / 2 = 100 == height
        assert vp.dxf.height == 100

    def test_zoom_extents_factor_2(self, msp):
        zoom.extents(msp, factor=2)
        vp = msp.doc.viewports.get("*Active")[0]
        assert vp.dxf.center == (0, 0)
        # 2:1 = 200 / 2 = 100 * 2 == height
        assert vp.dxf.height == 200

    def test_zoom_window(self, msp):
        zoom.window(msp, (-30, -10), (0, 20))
        vp = msp.doc.viewports.get("*Active")[0]
        assert vp.dxf.center == (-15, 5)
        assert vp.dxf.height == 30

    def test_zoom_objects(self, msp):
        points = msp[:2]
        zoom.objects(msp, points)
        vp = msp.doc.viewports.get("*Active")[0]
        assert vp.dxf.center == (0, 0)
        assert vp.dxf.height == 50

    def test_zoom_objects_of_empty_set(self, msp):
        vp = msp.doc.viewports.get("*Active")[0]
        old_center = vp.dxf.center
        old_height = vp.dxf.height
        zoom.objects(msp, [])
        vp = msp.doc.viewports.get("*Active")[0]
        assert vp.dxf.center == old_center
        assert vp.dxf.height == old_height


class TestPaperSpace:
    @pytest.fixture(scope="class")
    def psp(self):
        doc = ezdxf.new()
        psp_ = cast("Paperspace", doc.layout("Layout1"))
        psp_.add_viewport(
            center=(40, 40),
            size=(40, 40),
            view_center_point=(0, 0),
            view_height=1,
        )
        psp_.add_point((5, 5))
        psp_.add_point((405, 305))
        return psp_

    def test_bbox_of_main_viewport(self, psp):
        psp.reset_main_viewport()
        vp = psp.main_viewport()
        box = bbox.extents([vp])
        assert box.has_data is True
        assert box.center.isclose(vp.dxf.center)
        assert box.size.x == pytest.approx(vp.dxf.width)
        assert box.size.y == pytest.approx(vp.dxf.height)

    def test_zoom_center(self, psp):
        zoom.center(psp, (10, 10), size=(20, 15))
        vp = psp.main_viewport()
        assert vp.dxf.center == (10, 10)
        assert vp.dxf.width == 20
        assert vp.dxf.height == 15

    def test_zoom_extents(self, psp):
        zoom.extents(psp)
        vp = psp.main_viewport()
        assert vp.dxf.center == (205, 155)
        assert vp.dxf.width == 400
        assert vp.dxf.height == 300

    def test_zoom_extents_factor_2(self, psp):
        zoom.extents(psp, factor=2)
        vp = psp.main_viewport()
        assert vp.dxf.center == (205, 155)
        assert vp.dxf.width == 800
        assert vp.dxf.height == 600

    def test_zoom_window(self, psp):
        zoom.window(psp, (-30, -10), (0, 20))
        vp = psp.main_viewport()
        assert vp.dxf.center == (-15, 5)
        assert vp.dxf.height == 30

    def test_zoom_objects_but_ignore_main_viewport(self, psp):
        vp = psp.main_viewport()
        # Clipping path of viewports are taken into account, but the main
        # viewport is ignored:
        objects = [psp[0], vp]
        zoom.objects(psp, objects)
        assert vp.dxf.center == (40, 40)
        assert vp.dxf.width == 40
        assert vp.dxf.height == 40

    def test_zoom_objects_of_empty_set(self, psp):
        vp = psp.main_viewport()
        old_center = vp.dxf.center
        old_height = vp.dxf.height
        zoom.objects(psp, [])
        vp = psp.main_viewport()
        assert vp.dxf.center == old_center
        assert vp.dxf.height == old_height


if __name__ == "__main__":
    pytest.main([__file__])
