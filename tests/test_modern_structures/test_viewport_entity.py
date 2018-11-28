# Created: 10.10.2015, 2018 rewritten for pytest
# Copyright (C) 2015-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest

from ezdxf.modern.viewport import Viewport, _VIEWPORT_TPL
from ezdxf.lldxf.extendedtags import ExtendedTags


@pytest.fixture
def viewport():
    return Viewport(ExtendedTags.from_text(_VIEWPORT_TPL))


def test_viewport_init_values(viewport):
    assert (0, 0, 0) == viewport.dxf.center
    assert 1.0 == viewport.dxf.height
    assert 1.0 == viewport.dxf.width


def test_viewport_attribute_access(viewport):
    assert (0, 0, 0) == viewport.dxf.view_target_point
    assert (0, 0, 0) == viewport.dxf.view_direction_vector
    assert 0 == viewport.dxf.view_twist_angle
    assert 1 == viewport.dxf.view_height
    assert (0, 0) == viewport.dxf.view_center_point
    assert 50 == viewport.dxf.perspective_lens_length
    assert 0 == viewport.dxf.front_clip_plane_z_value
    assert 0 == viewport.dxf.back_clip_plane_z_value
    assert 32864 == viewport.dxf.flags
    assert 100 == viewport.dxf.circle_zoom
    assert 0 == viewport.dxf.ucs_icon
    assert 0 == viewport.dxf.snap_angle
    assert (0, 0) == viewport.dxf.snap_base_point
    assert (0.1, 0.1) == viewport.dxf.snap_spacing
    assert (0.1, 0.1) == viewport.dxf.grid_spacing
    assert [] == list(viewport.get_frozen_layer_handles())


def test_viewport_set_frozen_layer_handles(viewport):
    layer_handles = ['A000', 'A001', 'A002']
    viewport.set_frozen_layers(layer_handles)
    assert layer_handles == list(viewport.get_frozen_layer_handles())


class Layer:
    class DXF(object):
        def __init__(self, handle):
            self.handle = handle

    def __init__(self, handle):
        self.dxf = Layer.DXF(handle)


def test_viewport_set_frozen_layer_objects(viewport):
    layer_handles = ['A000', 'A001', 'A002']
    layers = [Layer(handle) for handle in layer_handles]
    viewport.set_frozen_layers(layers)
    assert layer_handles == list(viewport.get_frozen_layer_handles())

