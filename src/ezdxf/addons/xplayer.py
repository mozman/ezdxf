#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
"""xplayer = cross backend player."""
from ezdxf import path
from ezdxf.math import Vec2

from ezdxf.addons.drawing.backend import BackendInterface
from ezdxf.addons.drawing.properties import BackendProperties, rgb_to_hex
from ezdxf.addons.hpgl2 import api
from ezdxf.addons.hpgl2.backend import Properties as HPGL2Properties, RecordType


def hpgl2_to_drawing(recorder: api.Recorder, backend: BackendInterface) -> None:
    """Replays the recordings of the HPGL2 Recorder on a backend of the drawing add-on."""
    backend.set_background("#ffffff")  # plotting on white paper
    props = recorder.properties
    for record in recorder.records:
        backend_properties = _make_drawing_backend_properties(
            props[record.property_hash]
        )
        if record.type == RecordType.POLYLINE:
            points: list[Vec2] = record.data.vertices()
            size = len(points)
            if size == 1:
                backend.draw_point(points[0], backend_properties)
            elif size == 2:
                backend.draw_line(points[0], points[1], backend_properties)
            else:
                backend.draw_path(_from_2d_points(points), backend_properties)
        elif record.type == RecordType.FILLED_POLYGON:
            # filled polygons are stored as single paths! see: PolygonBuffer.get_paths()
            external_paths, holes = path.winding_deconstruction(
                path.fast_bbox_detection(p.to_path2d() for p in record.data)
            )
            backend.draw_filled_paths(external_paths, holes, backend_properties)  # type: ignore
    backend.finalize()


def _make_drawing_backend_properties(properties: HPGL2Properties) -> BackendProperties:
    """Make BackendProperties() for the drawing add-on."""
    return BackendProperties(
        color=rgb_to_hex(properties.pen_color),
        lineweight=properties.pen_width,
        layer="0",
        pen=properties.pen_index,
        handle="",
    )


def _from_2d_points(points: list[Vec2]) -> path.Path2d:
    """Returns points as 2D path."""
    path2d = path.Path2d(points[0])
    for point in points[1:]:
        path2d.line_to(point)
    return path2d
