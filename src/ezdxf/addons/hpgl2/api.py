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
from .pdf_backend import PDFBackend
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
    *,
    rotation: int = 0,
    sx=1.0,
    sy=1.0,
    color_mode=ColorMode.RGB,
    map_black_rgb_to_white_rgb=False,
    merge_control: MergeControl = MergeControl.AUTO,
) -> Drawing:
    if rotation not in (0, 90, 180, 270):
        raise ValueError("invalid rotation angle: should be 0, 90, 180, or 270")

    # 1st pass records output of the plotting commands and detects the bounding box
    doc = ezdxf.new()
    try:
        recorder = record_plotter_output(b, rotation, sx, sy, merge_control)
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
    bbox = recorder.bbox()
    del recorder

    if bbox.has_data:  # non-empty page
        zoom.window(msp, bbox.extmin, bbox.extmax)
        _update_doc(doc, bbox)
    return doc


def _update_doc(doc, bbox):
    doc.header["$EXTMIN"] = (bbox.extmin.x, bbox.extmin.y, 0)
    doc.header["$EXTMAX"] = (bbox.extmax.x, bbox.extmax.y, 0)

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
    sx: float = 1.0,
    sy: float = 1.0,
    merge_control=MergeControl.AUTO,
) -> str:
    if rotation not in (0, 90, 180, 270):
        raise ValueError("invalid rotation angle: should be 0, 90, 180, or 270")
    # 1st pass records output of the plotting commands and detects the bounding box
    try:
        recorder = record_plotter_output(b, rotation, sx, sy, merge_control)
    except Hpgl2Error:
        return ""

    # 2nd pass replays the plotting commands to plot the SVG
    svg_backend = SVGBackend(recorder.bbox())
    recorder.replay(svg_backend)
    del recorder
    return svg_backend.get_string()


def to_pdf(
    b: bytes,
    *,
    rotation: int = 0,
    sx: float = 1.0,
    sy: float = 1.0,
    merge_control=MergeControl.AUTO,
) -> bytes:
    if rotation not in (0, 90, 180, 270):
        raise ValueError("invalid rotation angle: should be 0, 90, 180, or 270")
    # 1st pass records output of the plotting commands and detects the bounding box
    try:
        recorder = record_plotter_output(b, rotation, sx, sy, merge_control)
    except Hpgl2Error:
        return b""
    # 2nd pass replays the plotting commands to plot the SVG
    pdf_backend = PDFBackend(recorder.bbox())
    recorder.replay(pdf_backend)
    del recorder
    return pdf_backend.get_bytes()


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
    sx: float,
    sy: float,
    merge_control: MergeControl,
) -> Recorder:
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
    bbox = recorder.bbox()
    if not bbox.has_data:
        raise EmptyDrawing
    m = placement_matrix(bbox, sx, sy, rotation)
    recorder.transform(m)

    if merge_control == MergeControl.AUTO:
        if plotter.has_merge_control:
            merge_control = merge_control.LUMINANCE  # type: ignore
    if merge_control == MergeControl.LUMINANCE:
        if DEBUG:
            print("merge control on: sorting filled polygons by luminance")
        recorder.sort_filled_polygons()
    return recorder
