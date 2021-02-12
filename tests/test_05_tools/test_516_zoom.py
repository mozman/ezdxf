#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf import zoom


class TestModelSpace:
    @pytest.fixture(scope='class')
    def msp(self):
        doc = ezdxf.new()
        msp_ = doc.modelspace()
        msp_.add_point((-25, -25))
        msp_.add_point((25, 25))
        msp_.add_point((-100, -50))
        msp_.add_point((100, 50))
        return msp_

    def test_zoom_center(self, msp):
        zoom.center(msp, (10, 10), 10)
        vp = msp.doc.viewports.get('*Active')[0]
        assert vp.dxf.center == (10, 10)
        assert vp.dxf.height == 10

    def test_zoom_extents(self, msp):
        zoom.extends(msp)
        vp = msp.doc.viewports.get('*Active')[0]
        assert vp.dxf.center == (0, 0)
        # 2:1 = 200 / 2 = 100 == height
        assert vp.dxf.height == 100

    def test_zoom_extents_factor_2(self, msp):
        zoom.extends(msp, factor=2)
        vp = msp.doc.viewports.get('*Active')[0]
        assert vp.dxf.center == (0, 0)
        # 2:1 = 200 / 2 = 100 * 2 == height
        assert vp.dxf.height == 200

    def test_zoom_window(self, msp):
        zoom.window(msp, (-30, -10), (0, 20))
        vp = msp.doc.viewports.get('*Active')[0]
        assert vp.dxf.center == (-15, 5)
        assert vp.dxf.height == 30

    def test_zoom_objects(self, msp):
        points = msp[:2]
        zoom.objects(msp, points)
        vp = msp.doc.viewports.get('*Active')[0]
        assert vp.dxf.center == (0, 0)
        assert vp.dxf.height == 50

    def test_zoom_objects_of_empty_set(self, msp):
        vp = msp.doc.viewports.get('*Active')[0]
        old_center = vp.dxf.center
        old_height = vp.dxf.height
        zoom.objects(msp, [])
        vp = msp.doc.viewports.get('*Active')[0]
        assert vp.dxf.center == old_center
        assert vp.dxf.height == old_height


if __name__ == '__main__':
    pytest.main([__file__])
