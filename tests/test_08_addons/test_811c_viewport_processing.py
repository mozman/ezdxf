#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.addons.drawing.frontend import _draw_viewports
from ezdxf.entities import Viewport


# The "id" attribute is not evaluated in the current implementation of VIEWPORT
# processing.
def new_viewport(status=0, id=0):
    return Viewport.new(dxfattribs={"status": status, "id": id})


class Frontend:
    def __init__(self):
        self.viewports = []

    def draw_viewport(self, vp):
        self.viewports.append(vp)


@pytest.fixture
def frontend():
    return Frontend()


def test_ignore_active_viewport(frontend):
    # The "active" viewport determines how the paperspace layout is presented as a
    # whole (location & zoom state).
    vp0 = new_viewport(1, 1)  # "active" viewport - ignored
    vp1 = new_viewport(2, 2)  # paperspace viewport - drawn
    _draw_viewports(frontend, [vp0, vp1])
    assert frontend.viewports[0] is vp1


def test_ignore_only_the_first_active_viewport(frontend):
    vp0 = new_viewport(1, 1)  # "active" viewport - ignored
    vp1 = new_viewport(1, 1)  # accidentally second "active" viewport - drawn
    vp2 = new_viewport(2, 2)  # paperspace viewport - drawn
    _draw_viewports(frontend, [vp0, vp1, vp2])
    assert frontend.viewports[0] is vp1
    assert frontend.viewports[1] is vp2


def test_ignore_missing_active_viewport(frontend):
    # No "active" viewport (status=1) defined - this is maybe not a valid paperspace
    # setup!
    vp0 = new_viewport(2, 2)  # paperspace viewport - drawn
    vp1 = new_viewport(3, 3)  # paperspace viewport - drawn
    _draw_viewports(frontend, [vp0, vp1])
    assert frontend.viewports[0] is vp0
    assert frontend.viewports[1] is vp1


def test_ignore_BricsCAD_off_viewports(frontend):
    vp0 = new_viewport(1, 1)  # "active" viewport - ignored
    # BricsCAD set the id to -1 if the viewport is off and 'status' (group code 68)
    # is not present.
    vp1 = Viewport.new(dxfattribs={"id": -1})
    vp2 = new_viewport(3, 3)  # paperspace viewport - drawn
    _draw_viewports(frontend, [vp0, vp1, vp2])
    assert frontend.viewports[0] is vp2


def test_ignore_off_screen_viewports(frontend):
    vp0 = new_viewport(1, 1)  # "active" viewport - ignored
    vp1 = new_viewport(-1, 2)  # off-screen viewport - ignored
    vp2 = new_viewport(2, 3)  # paperspace viewport - drawn
    _draw_viewports(frontend, [vp0, vp1, vp2])
    assert frontend.viewports[0] is vp2


def test_draw_viewports_in_order_of_status(frontend):
    vp0 = new_viewport(1, 1)  # "active" viewport - ignored
    vp1 = new_viewport(status=3, id=2)
    vp2 = new_viewport(status=2, id=3)
    _draw_viewports(frontend, [vp0, vp1, vp2])
    assert frontend.viewports[0] is vp2
    assert frontend.viewports[1] is vp1


if __name__ == "__main__":
    pytest.main([__file__])
