# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# created 2019-02-15
from typing import cast
import pytest

import ezdxf
from ezdxf.entities.image import Wipeout
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.layouts import VirtualLayout
from ezdxf.math import Vec2


@pytest.fixture
def doc():
    return ezdxf.new()


def test_wipeout_default_new():
    entity = Wipeout.new(
        handle="ABBA", owner="0", dxfattribs={"image_size": (640, 200)}
    )
    assert entity.dxf.layer == "0"
    assert entity.dxf.insert is None  # set by add_image()
    assert entity.dxf.u_pixel is None  # set by add_image()
    assert entity.dxf.v_pixel is None  # set by add_image()
    assert entity.dxf.class_version == 0
    assert entity.dxf.image_size == (640, 200)
    assert entity.dxf.image_def_handle == "0"
    assert entity.dxf.flags == 3
    assert entity.dxf.clipping == 0
    assert entity.dxf.brightness == 50
    assert entity.dxf.contrast == 50
    assert entity.dxf.fade == 0
    assert entity.dxf.image_def_reactor_handle == "0"
    assert entity.dxf.clipping_boundary_type == 1
    assert entity.dxf.clip_mode == 0
    assert entity.boundary_path[0] == (-0.5, -0.5)
    assert entity.boundary_path[1] == (639.5, 199.5)


def test_wipeout_write_dxf():
    entity = Wipeout.from_text(WIPEOUT)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(WIPEOUT)
    assert result == expected


def test_wipeout_creator_interface():
    layout = VirtualLayout()
    wipeout = layout.add_wipeout(
        [(150, 100), (250, 100), (250, 200), (150, 200)]
    )
    assert wipeout.dxftype() == "WIPEOUT"
    assert wipeout.dxf.insert == (150, 100, 0)
    assert wipeout.dxf.u_pixel == (100, 0, 0)
    assert wipeout.dxf.v_pixel == (0, 100, 0)
    assert wipeout.dxf.image_size == (1, 1)
    assert wipeout.dxf.flags == 7
    assert wipeout.dxf.clipping == 1
    assert wipeout.dxf.clip_mode == 0

    path = wipeout.boundary_path
    assert path[0].isclose(Vec2(-0.5, 0.5))
    assert path[1].isclose(Vec2(0.5, 0.5))
    assert path[2].isclose(Vec2(0.5, -0.5))
    assert path[3].isclose(Vec2(-0.5, -0.5))
    assert path[4] == path[0]

    path = wipeout.boundary_path_wcs()
    assert path[0] == (150, 100)
    assert path[1] == (250, 100)
    assert path[2] == (250, 200)
    assert path[3] == (150, 200)
    assert path[0] == path[-1]


def test_copy_wipeout():
    layout = VirtualLayout()
    wipeout = layout.add_wipeout([(150, 100), (250, 200)])
    copy = wipeout.copy()
    layout.add_entity(copy)
    assert len(layout) == 2


def test_wipeout_vars(doc):
    doc.set_wipeout_variables(frame=1)
    wipeout_variables = doc.rootdict["ACAD_WIPEOUT_VARS"]
    assert wipeout_variables.dxf.frame == 1


def test_boundary_path_wcs():
    from ezdxf.layouts import VirtualLayout

    layout = VirtualLayout()
    e = cast(
        Wipeout,
        layout.new_entity(
            "WIPEOUT",
            dxfattribs={
                "layer": "0",
                "class_version": 0,
                "insert": (150.0, 100.0, 0.0),
                "u_pixel": (100.0, 0.0, 0.0),
                "v_pixel": (0.0, 100.0, 0.0),
                "image_size": (1.0, 1.0, 0.0),
                "image_def_handle": "0",
                "flags": 7,
                "clipping": 1,
                "brightness": 50,
                "contrast": 50,
                "fade": 0,
                "image_def_reactor_handle": "0",
                "clipping_boundary_type": 2,
                "count_boundary_points": 5,
                "clip_mode": 0,
            },
        ),
    )
    e.set_boundary_path(
        [
            (-0.5, 0.5),
            (0.5, 0.5),
            (0.5, -0.5),
            (-0.5, -0.5),
            (-0.5, 0.5),
        ]
    )
    path = e.boundary_path_wcs()
    assert path[0] == (150, 100)
    assert path[1] == (250, 100)
    assert path[2] == (250, 200)
    assert path[3] == (150, 200)
    assert path[0] == path[-1]


WIPEOUT = """0
WIPEOUT
5
0
330
0
100
AcDbEntity
8
0
100
AcDbWipeout
90
0
10
0.0
20
0.0
30
0.0
11
0.0
21
0.0
31
0.0
12
0.0
22
0.0
32
0.0
13
640
23
320
340
0
70
3
280
1
281
50
282
50
283
0
360
0
71
1
91
2
14
-0.5
24
-0.5
14
639.5
24
319.5
290
0
"""
