#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable, no_type_check
import copy

from ezdxf.math import Vec2, BoundingBox2d
from ezdxf.colors import RGB
from ezdxf.path import Command
from ezdxf.version import __version__

from .type_hints import Color
from .backend import BackendInterface, BkPath2d, BkPoints2d
from .config import Configuration, LineweightPolicy
from .properties import BackendProperties
from . import layout, recorder

is_pymupdf_installed = True
try:
    import fitz
except ImportError:
    print(
        "Python module PyMuPDF (AGPL!) is required: https://pypi.org/project/PyMuPDF/"
    )
    fitz = None
    is_pymupdf_installed = False
# PyMuPDF docs: https://pymupdf.readthedocs.io/en/latest/

__all__ = ["PyMuPdfBackend", "is_pymupdf_installed"]

# PDF units are points (pt), 1 pt is 1/72 of an inch:
MM_TO_POINTS = 72.0 / 25.4  # 25.4 mm = 1 inch / 72
# psd does not work in PyMuPDF v1.22.3
SUPPORTED_IMAGE_FORMATS = ("png", "ppm", "pbm")


class PyMuPdfBackend(recorder.Recorder):
    """This backend uses the `PyMuPdf`_ package to create PDF, PNG, PPM and PBM output.
    This backend support content cropping at page margins.

    PyMuPDF is licensed under the `AGPL`_. Sorry, but it's the best package for the job
    I've found so far.

    Install package::

        pip install pymupdf

    .. _PyMuPdf: https://pypi.org/project/PyMuPDF/
    .. _AGPL: https://www.gnu.org/licenses/agpl-3.0.html

    """

    def __init__(self) -> None:
        super().__init__()
        self._init_flip_y = True

    def _get_replay(
        self,
        page: layout.Page,
        *,
        settings: layout.Settings = layout.Settings(),
        render_box: BoundingBox2d | None = None,
    ) -> PyMuPdfRenderBackend:
        """Returns the PDF document as bytes.

        Args:
            page: page definition, see :class:`~ezdxf.addons.drawing.layout.Page`
            settings: layout settings, see :class:`~ezdxf.addons.drawing.layout.Settings`
            render_box: set explicit region to render, default is content bounding box
        """
        top_origin = True
        # This player changes the original recordings!
        player = self.player()
        if render_box is None:
            render_box = player.bbox()

        # the page origin (0, 0) is in the top-left corner.
        output_layout = layout.Layout(render_box, flip_y=self._init_flip_y)
        page = output_layout.get_final_page(page, settings)

        # DXF coordinates are mapped to PDF Units in the first quadrant
        settings = copy.copy(settings)
        settings.output_coordinate_space = get_coordinate_output_space(page)

        m = output_layout.get_placement_matrix(
            page, settings=settings, top_origin=top_origin
        )
        # transform content to the output coordinates space:
        player.transform(m)
        if settings.crop_at_margins:
            p1, p2 = page.get_margin_rect(top_origin=top_origin)  # in mm
            # scale factor to map page coordinates to output space coordinates:
            output_scale = settings.page_output_scale_factor(page)
            max_sagitta = 0.1 * MM_TO_POINTS  # curve approximation 0.1 mm
            # crop content inplace by the margin rect:
            player.crop_rect(p1 * output_scale, p2 * output_scale, max_sagitta)

        self._init_flip_y = False
        backend = self.make_backend(page, settings)
        player.replay(backend)
        return backend

    def get_pdf_bytes(
        self,
        page: layout.Page,
        *,
        settings: layout.Settings = layout.Settings(),
        render_box: BoundingBox2d | None = None,
    ) -> bytes:
        """Returns the PDF document as bytes.

        Args:
            page: page definition, see :class:`~ezdxf.addons.drawing.layout.Page`
            settings: layout settings, see :class:`~ezdxf.addons.drawing.layout.Settings`
            render_box: set explicit region to render, default is content bounding box
        """
        backend = self._get_replay(page, settings=settings, render_box=render_box)
        return backend.get_pdf_bytes()

    def get_pixmap_bytes(
        self,
        page: layout.Page,
        *,
        fmt="png",
        settings: layout.Settings = layout.Settings(),
        dpi: int = 96,
        alpha=False,
        render_box: BoundingBox2d | None = None,
    ) -> bytes:
        """Returns a pixel image as bytes, supported image formats:

        === =========================
        png Portable Network Graphics
        ppm Portable Pixmap (no alpha channel)
        pbm Portable Bitmap (no alpha channel)
        === =========================

        Args:
            page: page definition, see :class:`~ezdxf.addons.drawing.layout.Page`
            fmt: image format
            settings: layout settings, see :class:`~ezdxf.addons.drawing.layout.Settings`
            dpi: output resolution in dots per inch
            alpha: add alpha channel (transparency)
            render_box: set explicit region to render, default is content bounding box
        """
        if fmt not in SUPPORTED_IMAGE_FORMATS:
            raise ValueError(f"unsupported image format: '{fmt}'")
        backend = self._get_replay(page, settings=settings, render_box=render_box)
        try:
            pixmap = backend.get_pixmap(dpi=dpi, alpha=alpha)
            return pixmap.tobytes(output=fmt)
        except RuntimeError as e:
            print(f"PyMuPDF Runtime Error: {str(e)}")
            return b""

    @staticmethod
    def make_backend(
        page: layout.Page, settings: layout.Settings
    ) -> PyMuPdfRenderBackend:
        """Override this method to use a customized render backend."""
        return PyMuPdfRenderBackend(page, settings)


def get_coordinate_output_space(page: layout.Page) -> int:
    page_width_in_pt = int(page.width_in_mm * MM_TO_POINTS)
    page_height_in_pt = int(page.height_in_mm * MM_TO_POINTS)
    return max(page_width_in_pt, page_height_in_pt)


class PyMuPdfRenderBackend(BackendInterface):
    """Creates the PDF/PNG/PSD/SVG output.

    This backend requires some preliminary work, record the frontend output via the
    Recorder backend to accomplish the following requirements:

    - Move content in the first quadrant of the coordinate system.
    - The page is defined by the upper left corner in the origin (0, 0) and
      the lower right corner at (page-width, page-height)
    - The output coordinates are floats in 1/72 inch, scale the content appropriately
    - Replay the recorded output on this backend.

    .. important::

        Python module PyMuPDF is required: https://pypi.org/project/PyMuPDF/

    """

    def __init__(self, page: layout.Page, settings: layout.Settings) -> None:
        assert (
            is_pymupdf_installed
        ), "Python module PyMuPDF is required: https://pypi.org/project/PyMuPDF/"
        self.doc = fitz.open()
        self.doc.set_metadata(
            {
                "producer": f"PyMuPDF {fitz.version[0]}",
                "creator": f"ezdxf {__version__}",
            }
        )
        self.settings = settings
        self._stroke_width_cache: dict[float, float] = dict()
        self._color_cache: dict[str, tuple[float, float, float]] = dict()
        self.page_width_in_pt = int(page.width_in_mm * MM_TO_POINTS)
        self.page_height_in_pt = int(page.height_in_mm * MM_TO_POINTS)
        # LineweightPolicy.ABSOLUTE:
        self.min_lineweight = 0.05  # in mm, set by configure()
        self.lineweight_scaling = 1.0  # set by configure()
        self.lineweight_policy = LineweightPolicy.ABSOLUTE  # set by configure()

        # when the stroke width is too thin PDF viewers may get confused;
        self.abs_min_stroke_width = 0.1  # pt == 0.03528mm (arbitrary choice)

        # LineweightPolicy.RELATIVE:
        # max_stroke_width is determined as a certain percentage of settings.output_coordinate_space
        self.max_stroke_width: float = max(
            self.abs_min_stroke_width,
            int(settings.output_coordinate_space * settings.max_stroke_width),
        )
        # min_stroke_width is determined as a certain percentage of max_stroke_width
        self.min_stroke_width: float = max(
            self.abs_min_stroke_width,
            int(self.max_stroke_width * settings.min_stroke_width),
        )
        # LineweightPolicy.RELATIVE_FIXED:
        # all strokes have a fixed stroke-width as a certain percentage of max_stroke_width
        self.fixed_stroke_width: float = max(
            self.abs_min_stroke_width,
            int(self.max_stroke_width * settings.fixed_stroke_width),
        )
        self.page = self.doc.new_page(-1, self.page_width_in_pt, self.page_height_in_pt)

    def get_pdf_bytes(self) -> bytes:
        return self.doc.tobytes()

    def get_pixmap(self, dpi: int, alpha=False):
        return self.page.get_pixmap(dpi=dpi, alpha=alpha)

    def get_svg_image(self) -> bytes:
        return self.page.get_svg_image()

    def set_background(self, color: Color) -> None:
        rgb = self.resolve_color(color)
        opacity = alpha_to_opacity(color[7:9])
        if color == (1.0, 1.0, 1.0) or opacity == 0.0:
            return
        shape = self.new_shape()
        shape.draw_rect([0, 0, self.page_width_in_pt, self.page_height_in_pt])
        shape.finish(width=None, color=None, fill=rgb, fill_opacity=opacity)
        shape.commit()

    def new_shape(self):
        return self.page.new_shape()

    def finish_line(self, shape, properties: BackendProperties, close: bool) -> None:
        color = self.resolve_color(properties.color)
        width = self.resolve_stroke_width(properties.lineweight)
        shape.finish(
            width=width,
            color=color,
            fill=None,
            lineJoin=1,
            lineCap=1,
            stroke_opacity=alpha_to_opacity(properties.color[7:9]),
            closePath=close,
        )

    def finish_filling(self, shape, properties: BackendProperties) -> None:
        shape.finish(
            width=None,
            color=None,
            fill=self.resolve_color(properties.color),
            fill_opacity=alpha_to_opacity(properties.color[7:9]),
            lineJoin=1,
            lineCap=1,
            closePath=True,
            even_odd=True,
        )

    def resolve_color(self, color: Color) -> tuple[float, float, float]:
        key = color[:7]
        try:
            return self._color_cache[key]
        except KeyError:
            pass
        color_floats = RGB.from_hex(color).to_floats()
        self._color_cache[key] = color_floats
        return color_floats

    def resolve_stroke_width(self, width: float) -> float:
        try:
            return self._stroke_width_cache[width]
        except KeyError:
            pass
        stroke_width = self.min_stroke_width
        if self.lineweight_policy == LineweightPolicy.ABSOLUTE:
            stroke_width = (  # in points (pt) = 1/72 inch
                max(self.min_lineweight, width) * MM_TO_POINTS * self.lineweight_scaling
            )
        elif self.lineweight_policy == LineweightPolicy.RELATIVE:
            stroke_width = map_lineweight_to_stroke_width(
                width, self.min_stroke_width, self.max_stroke_width
            )
        stroke_width = max(self.abs_min_stroke_width, stroke_width)
        self._stroke_width_cache[width] = stroke_width
        return stroke_width

    def draw_point(self, pos: Vec2, properties: BackendProperties) -> None:
        shape = self.new_shape()
        pos = Vec2(pos)
        shape.draw_line(pos, pos)
        self.finish_line(shape, properties, close=False)
        shape.commit()

    def draw_line(self, start: Vec2, end: Vec2, properties: BackendProperties) -> None:
        shape = self.new_shape()
        shape.draw_line(Vec2(start), Vec2(end))
        self.finish_line(shape, properties, close=False)
        shape.commit()

    def draw_solid_lines(
        self, lines: Iterable[tuple[Vec2, Vec2]], properties: BackendProperties
    ) -> None:
        shape = self.new_shape()
        for start, end in lines:
            shape.draw_line(start, end)
        self.finish_line(shape, properties, close=False)
        shape.commit()

    def draw_path(self, path: BkPath2d, properties: BackendProperties) -> None:
        if len(path) == 0:
            return
        shape = self.new_shape()
        add_path_to_shape(shape, path, close=False)
        self.finish_line(shape, properties, close=False)
        shape.commit()

    def draw_filled_paths(
        self, paths: Iterable[BkPath2d], properties: BackendProperties
    ) -> None:
        shape = self.new_shape()
        for p in paths:
            add_path_to_shape(shape, p, close=True)
        self.finish_filling(shape, properties)
        shape.commit()

    def draw_filled_polygon(
        self, points: BkPoints2d, properties: BackendProperties
    ) -> None:
        vertices = points.vertices()
        if len(vertices) < 3:
            return
        # input coordinates are page coordinates in pdf units
        shape = self.new_shape()
        shape.draw_polyline(vertices)
        self.finish_filling(shape, properties)
        shape.commit()

    def configure(self, config: Configuration) -> None:
        self.lineweight_policy = config.lineweight_policy
        if config.min_lineweight:
            # config.min_lineweight in 1/300 inch!
            min_lineweight_mm = config.min_lineweight * 25.4 / 300
            self.min_lineweight = max(0.05, min_lineweight_mm)
        self.lineweight_scaling = config.lineweight_scaling

    def clear(self) -> None:
        pass

    def finalize(self) -> None:
        pass

    def enter_entity(self, entity, properties) -> None:
        pass

    def exit_entity(self, entity) -> None:
        pass


@no_type_check
def add_path_to_shape(shape, path: BkPath2d, close: bool) -> None:
    start = path.start
    sub_path_start = start
    last_point = start
    for command in path.commands():
        end = command.end
        if command.type == Command.MOVE_TO:
            if close and not sub_path_start.isclose(end):
                shape.draw_line(start, sub_path_start)
            sub_path_start = end
        elif command.type == Command.LINE_TO:
            shape.draw_line(start, end)
        elif command.type == Command.CURVE3_TO:
            shape.draw_curve(start, command.ctrl, end)
        elif command.type == Command.CURVE4_TO:
            shape.draw_bezier(start, command.ctrl1, command.ctrl2, end)
        start = end
        last_point = end
    if close and not sub_path_start.isclose(last_point):
        shape.draw_line(last_point, sub_path_start)


def map_lineweight_to_stroke_width(
    lineweight: float,
    min_stroke_width: float,
    max_stroke_width: float,
    min_lineweight=0.05,  # defined by DXF
    max_lineweight=2.11,  # defined by DXF
) -> float:
    """Map the DXF lineweight in mm to stroke-width in viewBox coordinates."""
    lineweight = max(min(lineweight, max_lineweight), min_lineweight) - min_lineweight
    factor = (max_stroke_width - min_stroke_width) / (max_lineweight - min_lineweight)
    return min_stroke_width + round(lineweight * factor, 1)


def alpha_to_opacity(alpha: str) -> float:
    # stroke-opacity: 0.0 = transparent; 1.0 = opaque
    # alpha: "00" = transparent; "ff" = opaque
    if len(alpha):
        try:
            return int(alpha, 16) / 255
        except ValueError:
            pass
    return 1.0
