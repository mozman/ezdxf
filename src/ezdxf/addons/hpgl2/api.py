#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
import enum
import ezdxf
from ezdxf.document import Drawing
from ezdxf import zoom

from .tokenizer import hpgl2_commands
from .plotter import Plotter
from .interpreter import Interpreter
from .backend import Recorder, placement_matrix, Player
from .dxf_backend import DXFBackend, ColorMode
from .svg_backend import SVGBackend
from .pdf_backend import PDFBackend, pdf_is_supported


DEBUG = False
ENTER_HPGL2_MODE = b"%1B"


class Hpgl2Error(Exception):
    """Base exception for the :mod:`hpgl2` add-on."""

    pass


class Hpgl2DataNotFound(Hpgl2Error):
    """No HPGL/2 data was found, maybe the "Enter HPGL/2 mode" escape sequence is missing."""

    pass


class EmptyDrawing(Hpgl2Error):
    """The HPGL/2 commands do not produce any content."""

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
    """
    Exports the HPGL/2 commands of the byte stream `b` as a DXF document.

    The page content is created at the origin of the modelspace and 1 drawing unit is 1
    plot unit (1 plu = 0.025mm) unless scaling values are provided.

    The content of HPGL files is intended to be plotted on white paper, so the appearance on
    a dark background in modelspace is not very clear. To fix this, set the argument
    `map_black_to_white` to ``True``, which maps black fillings and lines to white.

    All entities are assigned to a layer according to the pen number with the name schema
    ``COLOR_<#>``. In order to be able to process the file better, it is also possible to
    assign an :term:`ACI` color to the DXF entities according to the pen number by setting
    the argument `color_mode` to :attr:`ColorMode.ACI`, but then the RGB color is lost
    because the RGB color has always the higher priority over the :term:`ACI`.

    The first paperspace layout "Layout0" of the DXF document is set up to print the entire
    modelspace on one sheet, the size of the page is the size of the original plot file in
    millimeters.

    HPGL/2's merge control works at the pixel level and cannot be replicated by DXF,
    but to prevent fillings from obscuring text, the filled polygons are
    sorted by luminance - this can be forced or disabled by the argument `merge_control`,
    see also :class:`MergeControl` enum.

    Args:
        b: plot file content as bytes
        rotation: rotation angle of 0, 90, 180 or 270 degrees
        sx: scaling factor in x-axis direction, negative values to mirror the image
        sy: scaling factor in y-axis direction, negative values to mirror the image
        color_mode: the color mode controls how color values are assigned to DXF entities,
            see :class:`ColorMode`
        map_black_rgb_to_white_rgb: map black fillings to white
        merge_control: how to order filled polygons, see :class:`MergeControl`

    Returns: DXF document as instance of class :class:`~ezdxf.document.Drawing`

    """
    if rotation not in (0, 90, 180, 270):
        raise ValueError("invalid rotation angle: should be 0, 90, 180, or 270")

    # 1st pass records output of the plotting commands and detects the bounding box
    doc = ezdxf.new()
    try:
        player = record_plotter_output(b, rotation, sx, sy, merge_control)
    except Hpgl2Error:
        return doc

    msp = doc.modelspace()
    dxf_backend = DXFBackend(
        msp,
        color_mode=color_mode,
        map_black_rgb_to_white_rgb=map_black_rgb_to_white_rgb,
    )
    # 2nd pass replays the plotting commands to plot the DXF
    player.replay(dxf_backend)
    bbox = player.bbox()
    del player

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
    """
    Exports the HPGL/2 commands of the byte stream `b` as SVG string.

    The plot units are mapped 1:1 to ``viewBox`` units and the size of image is the size
    of the original plot file in millimeters.

    HPGL/2's merge control works at the pixel level and cannot be replicated by SVG,
    but to prevent fillings from obscuring text, the filled polygons are
    sorted by luminance - this can be forced or disabled by the argument `merge_control`,
    see also :class:`MergeControl` enum.

    Args:
        b: plot file content as bytes
        rotation: rotation angle of 0, 90, 180 or 270 degrees
        sx: scaling factor in x-axis direction, negative values to mirror the image
        sy: scaling factor in y-axis direction, negative values to mirror the image
        merge_control: how to order filled polygons, see :class:`MergeControl`

    Returns: SVG content as ``str``

    """
    if rotation not in (0, 90, 180, 270):
        raise ValueError("invalid rotation angle: should be 0, 90, 180, or 270")
    # 1st pass records output of the plotting commands and detects the bounding box
    try:
        player = record_plotter_output(b, rotation, sx, sy, merge_control)
    except Hpgl2Error:
        return ""

    # 2nd pass replays the plotting commands to plot the SVG
    svg_backend = SVGBackend(player.bbox())
    player.replay(svg_backend)
    del player
    return svg_backend.get_string()


def to_pdf(
    b: bytes,
    *,
    rotation: int = 0,
    sx: float = 1.0,
    sy: float = 1.0,
    merge_control=MergeControl.AUTO,
) -> bytes:
    """
    Exports the HPGL/2 commands of the byte stream `b` as PDF data.

    The plot units (1 plu = 0.025mm) are converted to PDF units (1/72 inch) so the size
    of image is the size of the original plot file in millimeters.

    HPGL/2's merge control works at the pixel level and cannot be replicated by PDF,
    but to prevent fillings from obscuring text, the filled polygons are
    sorted by luminance - this can be forced or disabled by the argument `merge_control`,
    see also :class:`MergeControl` enum.

    Python module PyMuPDF is required: https://pypi.org/project/PyMuPDF/

    Args:
        b: plot file content as bytes
        rotation: rotation angle of 0, 90, 180 or 270 degrees
        sx: scaling factor in x-axis direction, negative values to mirror the image
        sy: scaling factor in y-axis direction, negative values to mirror the image
        merge_control: how to order filled polygons, see :class:`MergeControl`

    Returns: PDF content as ``bytzs``

    """
    if not pdf_is_supported:
        print("Python module PyMuPDF is required: https://pypi.org/project/PyMuPDF/")
        return b""

    if rotation not in (0, 90, 180, 270):
        raise ValueError("invalid rotation angle: should be 0, 90, 180, or 270")
    # 1st pass records output of the plotting commands and detects the bounding box
    try:
        player = record_plotter_output(b, rotation, sx, sy, merge_control)
    except Hpgl2Error:
        return b""
    # 2nd pass replays the plotting commands to plot the SVG
    pdf_backend = PDFBackend(player.bbox())
    player.replay(pdf_backend)
    del player
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
) -> Player:
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
    player = recorder.player()
    bbox = player.bbox()
    if not bbox.has_data:
        raise EmptyDrawing
    m = placement_matrix(bbox, sx, sy, rotation)
    player.transform(m)

    if merge_control == MergeControl.AUTO:
        if plotter.has_merge_control:
            merge_control = MergeControl.LUMINANCE  # type: ignore
    if merge_control == MergeControl.LUMINANCE:
        if DEBUG:
            print("merge control on: sorting filled polygons by luminance")
        player.sort_filled_polygons()
    return player
