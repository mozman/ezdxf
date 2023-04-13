#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
import enum
import ezdxf
from ezdxf.document import Drawing
from ezdxf import zoom, transform
from ezdxf.math import Matrix44, BoundingBox, BoundingBox2d

from .tokenizer import hpgl2_commands
from .plotter import Plotter
from .interpreter import Interpreter
from .backend import Recorder, placement_matrix
from .dxf_backend import DXFBackend, ColorMode
from .svg_backend import SVGBackend
from .compiler import build

DEBUG = False


class Hpgl2Error(Exception):
    pass


class Hpgl2DataNotFound(Hpgl2Error):
    pass


class EmptyDrawing(Hpgl2Error):
    pass


class MergeControl(enum.IntEnum):
    NONE = 0  # print order
    LUMINANCE = 1  # sort filled polygons by luminance
    AUTO = 2  # guess best method


def to_dxf(
    b: bytes,
    scale: float = 1.0,
    *,
    rotation: int = 0,
    flip_horizontal=False,
    flip_vertical=False,
    color_mode=ColorMode.RGB,
    map_black_rgb_to_white_rgb=False,
    merge_control: MergeControl = MergeControl.AUTO,
) -> Drawing:
    if rotation not in (0, 90, 180, 270):
        raise ValueError("invalid rotation angle: should be 0, 90, 180, or 270")

    # 1st pass records output of the plotting commands and detects the bounding box
    doc = ezdxf.new()
    try:
        recorder, bbox = record_plotter_output(
            b, rotation, flip_horizontal, flip_vertical, merge_control
        )
    except Hpgl2Error:
        return doc

    msp = doc.modelspace()
    dxf_backend = DXFBackend(
        msp,
        color_mode=color_mode,
        map_black_rgb_to_white_rgb=map_black_rgb_to_white_rgb,
    )
    # 2nd pass replays the plotting commands to plot the DXF
    recorder.replay(dxf_backend)
    del recorder

    if bbox.has_data:  # non-empty page
        bbox = _scale_and_zoom(msp, scale, bbox)
        _reset_doc(doc, bbox)
    return doc


def _scale_and_zoom(layout, scale, bbox):
    extmin = bbox.extmin
    extmax = bbox.extmax
    if scale != 1.0 and scale > 1e-9:
        m = Matrix44.scale(scale, scale, scale)
        transform.inplace(layout, m)
        extmin = m.transform(extmin)
        extmax = m.transform(extmax)
    zoom.window(layout, extmin, extmax)
    return BoundingBox([extmin, extmax])


def _reset_doc(doc, bbox):
    doc.header["$EXTMIN"] = bbox.extmin
    doc.header["$EXTMAX"] = bbox.extmax

    psp_size = bbox.size / 40.0  # plu to mm
    psp_center = psp_size * 0.5
    psp = doc.paperspace()
    psp.page_setup(size=(psp_size.x, psp_size.y), margins=(0, 0, 0, 0), units="mm")
    psp.add_viewport(
        center=psp_center,
        size=(psp_size.x, psp_size.y),
        view_center_point=bbox.center,
        view_height=bbox.size.y,
    )


def to_svg(
    b: bytes,
    *,
    rotation: int = 0,
    flip_horizontal=False,
    flip_vertical=False,
    merge_control=MergeControl.AUTO,
) -> str:
    if rotation not in (0, 90, 180, 270):
        raise ValueError("invalid rotation angle: should be 0, 90, 180, or 270")
    # 1st pass records output of the plotting commands and detects the bounding box
    try:
        recorder, bbox = record_plotter_output(
            b, rotation, flip_horizontal, flip_vertical, merge_control
        )
    except Hpgl2Error:
        return ""
    # 2nd pass replays the plotting commands to plot the SVG
    svg_backend = SVGBackend(bbox)
    recorder.replay(svg_backend)
    del recorder
    return svg_backend.get_string()


def print_interpreter_log(interpreter: Interpreter) -> None:
    print("HPGL/2 interpreter log:")
    print(f"unsupported commands: {interpreter.not_implemented_commands}")
    if interpreter.errors:
        print("parsing errors:")
        for err in interpreter.errors:
            print(err)


def record_plotter_output(
    b: bytes,
    rotation: int,
    flip_horizontal: bool,
    flip_vertical: bool,
    merge_control: MergeControl,
) -> tuple[Recorder, BoundingBox2d]:
    commands = hpgl2_commands(b)
    if len(commands) == 0:
        print("HPGL2 data not found.")
        raise Hpgl2DataNotFound

    recorder = Recorder()
    plotter = Plotter(recorder)
    interpreter = Interpreter(plotter)
    interpreter.run(commands)
    if DEBUG:
        print_interpreter_log(interpreter)
    if not plotter.bbox.has_data:
        raise EmptyDrawing

    sx = -1.0 if flip_horizontal else 1.0
    sy = -1.0 if flip_vertical else 1.0
    m = placement_matrix(plotter.bbox, sx, sy, rotation)
    recorder.transform(m)
    bbox = BoundingBox2d(m.transform_vertices(plotter.bbox.rect_vertices()))

    if merge_control == MergeControl.AUTO:
        if plotter.has_merge_control:
            merge_control = merge_control.LUMINANCE  # type: ignore
    if merge_control == MergeControl.LUMINANCE:
        if DEBUG:
            print("merge control on: sorting filled polygons by luminance")
        recorder.sort_filled_polygons()
    return recorder, bbox
