# Created: 10.10.2015, 2018 rewritten for pytest
# Copyright (C) 2015-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest

from ezdxf.legacy.viewport import Viewport, _VPORT_TPL
from ezdxf.lldxf.extendedtags import ExtendedTags


@pytest.fixture
def viewport():
    return Viewport(ExtendedTags.from_text(_VPORT_TPL))


def test_vport_init_values(viewport):
    assert (0, 0, 0) == viewport.dxf.center
    assert 1.0 == viewport.dxf.height
    assert 1.0 == viewport.dxf.width


def test_vport_attribute_access(viewport):
    vp_data = viewport.get_viewport_data()
    assert (0, 0, 0) == vp_data.view_target_point
    assert (0, 0, 0) == vp_data.view_direction_vector
    assert 0 == vp_data.view_twist_angle
    assert 1 == vp_data.view_height
    assert (0, 0) == vp_data.view_center_point
    assert 50 == vp_data.perspective_lens_length
    assert 0 == vp_data.front_clip_plane_z_value
    assert 0 == vp_data.back_clip_plane_z_value
    assert 0 == vp_data.view_mode
    assert 100 == vp_data.circle_zoom
    assert 1 == vp_data.fast_zoom
    assert 3 == vp_data.ucs_icon
    assert 0 == vp_data.snap
    assert 0 == vp_data.grid
    assert 0 == vp_data.snap_style
    assert 0 == vp_data.snap_isopair
    assert 0 == vp_data.snap_angle
    assert (0, 0) == vp_data.snap_base_point
    assert (0.1, 0.1) == vp_data.snap_spacing
    assert (0.1, 0.1) == vp_data.grid_spacing
    assert 0 == vp_data.hidden_plot
    assert [] == vp_data.frozen_layers
