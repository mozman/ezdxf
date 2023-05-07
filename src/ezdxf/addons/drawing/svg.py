#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable, Sequence, no_type_check, NamedTuple
from typing_extensions import Self
import math
import itertools
import dataclasses
from xml.etree import ElementTree as ET

from ezdxf.math import AnyVec, Vec2, BoundingBox2d, Matrix44
from ezdxf.path import Path, Path2d, Command

from .type_hints import Color
from .backend import BackendInterface
from .config import Configuration
from .properties import BackendProperties
from .recorder import Recorder

CMD_M_ABS = "M {0.x:.0f} {0.y:.0f}"
CMD_M_REL = "m {0.x:.0f} {0.y:.0f}"
CMD_L_ABS = "L {0.x:.0f} {0.y:.0f}"
CMD_L_REL = "l {0.x:.0f} {0.y:.0f}"
CMD_C3_ABS = "Q {0.x:.0f} {0.y:.0f} {1.x:.0f} {1.y:.0f}"
CMD_C3_REL = "q {0.x:.0f} {0.y:.0f} {1.x:.0f} {1.y:.0f}"
CMD_C4_ABS = "C {0.x:.0f} {0.y:.0f} {1.x:.0f} {1.y:.0f} {2.x:.0f} {2.y:.0f}"
CMD_C4_REL = "c {0.x:.0f} {0.y:.0f} {1.x:.0f} {1.y:.0f} {2.x:.0f} {2.y:.0f}"
CMD_CONT = "{0.x:.0f} {0.y:.0f}"

__all__ = ["SVGBackend", "Settings"]

CSS_UNITS_TO_MM = {
    "cm": 10.0,
    "mm": 1.0,
    "in": 25.4,
    "px": 25.4 / 96.0,
    "pt": 25.4 / 72.0,
}

# all page sizes in landscape orientation
PAGE_SIZES = {
    "ISO A0": (1189, 841, "mm"),
    "ISO A1": (841, 594, "mm"),
    "ISO A2": (594, 420, "mm"),
    "ISO A3": (420, 297, "mm"),
    "ISO A4": (297, 210, "mm"),
    "ANSI A": (11, 8.5, "in"),
    "ANSI B": (17, 11, "in"),
    "ANSI C": (22, 17, "in"),
    "ANSI D": (34, 22, "in"),
    "ANSI E": (44, 34, "in"),
    "ARCH C": (24, 18, "in"),
    "ARCH D": (36, 24, "in"),
    "ARCH E": (48, 36, "in"),
    "ARCH E1": (42, 30, "in"),
    "Letter": (11, 8.5, "in"),
    "Legal": (14, 8.5, "in"),
}
MAX_VIEW_BOX_COORDS = 1_000_000


class Margins(NamedTuple):
    """Page margins definition class"""

    top: float
    right: float
    bottom: float
    left: float

    @classmethod
    def all(cls, margin: float) -> Self:
        """Returns a page margins definition class with four equal margins."""
        return cls(margin, margin, margin, margin)

    @classmethod
    def all2(cls, top_bottom: float, left_right: float) -> Self:
        """Returns a page margins definition class with equal top-bottom and
        left-right margins.
        """
        return cls(top_bottom, left_right, top_bottom, left_right)

    def scale(self, factor: float) -> Self:
        return self.__class__(
            self.top * factor,
            self.right * factor,
            self.bottom * factor,
            self.left * factor,
        )


@dataclasses.dataclass
class Page:
    """Page definition class"""

    width: float
    height: float
    units: str = "mm"
    margins: Margins = Margins.all(0)

    def __post_init__(self):
        if self.units not in CSS_UNITS_TO_MM:
            raise ValueError(f"unsupported or invalid units: {self.units}")

    @property
    def width_in_mm(self) -> int:
        return round(self.width * CSS_UNITS_TO_MM[self.units])

    @property
    def height_in_mm(self) -> int:
        return round(self.height * CSS_UNITS_TO_MM[self.units])

    @property
    def margins_in_mm(self) -> Margins:
        return self.margins.scale(CSS_UNITS_TO_MM[self.units])

    def to_landscape(self) -> None:
        if self.width < self.height:
            self.width, self.height = self.height, self.width

    def to_portrait(self) -> None:
        if self.height < self.width:
            self.width, self.height = self.height, self.width


@dataclasses.dataclass
class Settings:
    # Preserves the aspect-ratio at all scaling operations, these are CAD drawings!
    #
    # rotate content about 0, 90,  180 or 270 degrees
    content_rotation: int = 0

    # Scale content to fit the page,
    fit_page: bool = True

    # How to scale the input units, which are the DXF drawing units in model- or paper
    # space, to represent 1 mm in the rendered SVG drawing.
    # e.g. scale 1:100 and input units are m, so 0.01 input units is 1mm in the SVG drawing
    # or 1000mm in input units corresponds to 10mm in the SVG drawing = 10 / 1000 = 0.01;
    # e.g. scale 1:1; input unit is 1mm = 1 / 1 = 1.0 the default value
    # The value is ignored if the page size is defined and the content fits the page.
    # The value is used to determine missing page sizes (width or height).
    scale: float = 1.0

    # limit automatically detected page size
    max_page_height: tuple[float, str] = 0, "mm"
    max_page_width: tuple[float, str] = 0, "mm"

    def __post_init__(self) -> None:
        if self.content_rotation not in (0, 90, 180, 270):
            raise ValueError(
                f"invalid content rotation {self.content_rotation}, valid: 0, 90, 180, 270"
            )

    @property
    def swap_width_height(self) -> bool:
        return self.content_rotation in (90, 270)

    @property
    def max_page_width_in_mm(self) -> float:
        return self.max_page_width[0] * CSS_UNITS_TO_MM[self.max_page_width[1]]

    @property
    def max_page_height_in_mm(self) -> float:
        return self.max_page_height[0] * CSS_UNITS_TO_MM[self.max_page_height[1]]


class SVGBackend(Recorder):
    def __init__(self) -> None:
        super().__init__()
        self._init_y_axis_flip = True

    def get_string(self, page: Page, settings=Settings()) -> str:
        if settings.content_rotation not in (0, 90, 180, 270):
            raise ValueError("content rotation must be 0, 90, 180 or 270 degrees")

        # The SVG coordinate system has an inverted y-axis in comparison to the DXF
        # coordinate system, flip y-axis at the first transformation:
        rotation = settings.content_rotation
        flip_y = 1.0
        if self._init_y_axis_flip:
            flip_y = -1.0
            if rotation == 90:
                rotation = 270
            elif rotation == 270:
                rotation = 90

        bbox = self.bbox()
        page = final_page_size(bbox, page, settings)
        # the output coordinates are integer values in the range [0, MAX_VIEW_BOX_COORDS]
        scale = scale_view_box(bbox, page, settings.swap_width_height)
        vb_scale_mm = MAX_VIEW_BOX_COORDS / max(page.width_in_mm, page.height_in_mm)
        m = placement_matrix(
            bbox,
            sx=scale,
            sy=scale * flip_y,
            rotation=rotation,
            offset_x=page.margins.left * vb_scale_mm,
            offset_y=page.margins.top * vb_scale_mm,
        )
        self.transform(m)
        self._init_y_axis_flip = False
        backend = SVGRenderBackend(page)
        self.replay(backend)
        return backend.get_string()


def final_page_size(content_box: BoundingBox2d, page: Page, settings: Settings) -> Page:
    scale = settings.scale
    content_width, content_height = content_box.size
    if settings.swap_width_height:
        content_width, content_height = content_height, content_width
    width = page.width_in_mm
    height = page.height_in_mm
    margins = page.margins_in_mm
    if width == 0:
        width = scale * content_width + margins.left + margins.right
    if height == 0:
        height = scale * content_height + margins.top + margins.bottom

    width, height = limit_page_size(
        width, height, settings.max_page_width_in_mm, settings.max_page_height_in_mm
    )
    return Page(round(width, 2), round(height, 2), "mm", margins)


def limit_page_size(width, height, max_width, max_height) -> tuple[int, int]:
    ar = width / height
    if max_height:
        height = min(max_height, height)
        width = height * ar
    if max_width and width > max_width:
        width = min(max_width, width)
        height = width / ar
    return round(width), round(height)


def make_view_box(page: Page) -> tuple[int, int]:
    if page.width > page.height:
        return MAX_VIEW_BOX_COORDS, round(
            MAX_VIEW_BOX_COORDS * (page.height / page.width)
        )
    return round(MAX_VIEW_BOX_COORDS * (page.width / page.height)), MAX_VIEW_BOX_COORDS


def scale_view_box(bbox: BoundingBox2d, page: Page, swap_wh: bool) -> int:
    # The viewBox coordinates are integer values in the range of [0, MAX_VIEW_BOX_COORDS]
    scale_x = (page.width + page.margins.left + page.margins.right) / page.width
    scale_y = (page.height + page.margins.top + page.margins.bottom) / page.height
    content_width = bbox.size.x
    content_height = bbox.size.y
    if swap_wh:
        content_width, content_height = content_height, content_width

    return min(
        MAX_VIEW_BOX_COORDS / (content_width * scale_x),
        MAX_VIEW_BOX_COORDS / (content_height * scale_y),
    )


def placement_matrix(
    bbox: BoundingBox2d,
    sx: float,
    sy: float,
    rotation: float,
    offset_x: float,
    offset_y: float,
) -> Matrix44:
    """Returns a matrix to place the bbox in the first quadrant of the coordinate
    system (+x, +y).
    """
    if abs(sx) < 1e-9:
        sx = 1.0
    if abs(sy) < 1e-9:
        sy = 1.0
    m = Matrix44.scale(sx, sy, 1.0)
    if rotation:
        m @= Matrix44.z_rotate(math.radians(rotation))
    corners = m.transform_vertices(bbox.rect_vertices())
    # final output canvas
    canvas = BoundingBox2d(corners)
    # calculate margin offset
    tx, ty = canvas.extmin  # type: ignore
    return m @ Matrix44.translate(-tx + offset_x, -ty + offset_y, 0)


class SVGRenderBackend(BackendInterface):
    """Creates the SVG output.

    This backend requires some preliminary work, record the frontend output via the
    Recorder backend to accomplish the following requirements:

    - Scale the content in y-axis by -1 to invert the y-axis (SVG).
    - Move content in the first quadrant of the coordinate system.
    - The viewBox is defined by the lower left corner in the origin (0, 0) and
      the upper right corner at (view_box_width, view_box_height)
    - The output coordinates are integer values, scale the content appropriately.
    - Replay the recorded output at this backend.

    """

    def __init__(self, page: Page) -> None:
        view_box_width, view_box_height = make_view_box(page)
        self.stroke_width_scale: float = view_box_width / page.width_in_mm
        self.min_stroke_width: float = 0.05  # mm
        self.root = ET.Element(
            "svg",
            xmlns="http://www.w3.org/2000/svg",
            width=f"{page.width}{page.units}",
            height=f"{page.height}{page.units}",
            viewBox=f"0 0 {view_box_width} {view_box_height}",
        )
        self.background = ET.SubElement(
            self.root,
            "rect",
            fill="white",
            x="0",
            y="0",
            width=str(view_box_width),
            height=str(view_box_height),
        )
        self.fillings = ET.SubElement(self.root, "g", stroke="none", fill="black")
        self.fillings.set("fill-rule", "evenodd")
        self.strokes = ET.SubElement(self.root, "g", stroke="black", fill="none")
        self.strokes.set("stroke-linecap", "round")
        self.strokes.set("stroke-linejoin", "round")

    def get_string(self, xml_declaration=True) -> str:
        return ET.tostring(
            self.root, encoding="unicode", xml_declaration=xml_declaration
        )

    def set_background(self, color: Color) -> None:
        self.background.set("fill", color)

    def add_strokes(self, d: str, properties: BackendProperties):
        if not d:
            return
        element = ET.SubElement(self.strokes, "path", d=d)
        element.set("stroke", properties.color)
        lw = max(properties.lineweight, self.min_stroke_width) * self.stroke_width_scale
        element.set("stroke-width", f"{lw:.0f}")

    def add_filling(self, d: str, properties: BackendProperties):
        if not d:
            return
        element = ET.SubElement(self.fillings, "path", d=d)
        element.set("fill", properties.color)

    def draw_point(self, pos: AnyVec, properties: BackendProperties) -> None:
        self.add_strokes(self.make_polyline_str([pos, pos]), properties)

    def draw_line(
        self, start: AnyVec, end: AnyVec, properties: BackendProperties
    ) -> None:
        self.add_strokes(self.make_polyline_str([start, end]), properties)

    def draw_solid_lines(
        self, lines: Iterable[tuple[AnyVec, AnyVec]], properties: BackendProperties
    ) -> None:
        lines = list(lines)
        if len(lines) == 0:
            return
        self.add_strokes(self.make_multi_line_str(lines), properties)

    def draw_path(self, path: Path | Path2d, properties: BackendProperties) -> None:
        self.add_strokes(self.make_path_str(path), properties)

    def draw_filled_paths(
        self,
        paths: Iterable[Path | Path2d],
        holes: Iterable[Path | Path2d],
        properties: BackendProperties,
    ) -> None:
        d = []
        for path in itertools.chain(paths, holes):
            if len(path):
                d.append(self.make_path_str(path, close=True))
        self.add_filling(" ".join(d), properties)

    def draw_filled_polygon(
        self, points: Iterable[AnyVec], properties: BackendProperties
    ) -> None:
        self.add_filling(self.make_polyline_str(list(points), close=True), properties)

    def make_polyline_str(self, points: Sequence[Vec2], close=False) -> str:
        if len(points) < 2:
            return ""
        current = points[0]
        # first move is absolute, consecutive lines are relative:
        d: list[str] = [CMD_M_ABS.format(current), "l"]
        for point in points[1:]:
            relative = point - current
            current = point
            d.append(CMD_CONT.format(relative))
        if close:
            d.append("Z")
        return " ".join(d)

    def make_multi_line_str(self, lines: Sequence[tuple[Vec2, Vec2]]) -> str:
        assert len(lines) > 0
        start, end = lines[0]
        d: list[str] = [CMD_M_ABS.format(start), CMD_L_REL.format(end - start)]
        current = end
        for start, end in lines[1:]:
            d.append(CMD_M_REL.format(start - current))
            current = start
            d.append(CMD_L_REL.format(end - current))
            current = end
        return " ".join(d)

    @no_type_check
    def make_path_str(self, path: Path | Path2d, close=False) -> str:
        d: list[str] = [CMD_M_ABS.format(path.start)]
        if len(path) == 0:
            return ""

        current = path.start
        for cmd in path.commands():
            end = cmd.end
            if cmd.type == Command.MOVE_TO:
                d.append(CMD_M_REL.format(end - current))
            elif cmd.type == Command.LINE_TO:
                d.append(CMD_L_REL.format(end - current))
            elif cmd.type == Command.CURVE3_TO:
                d.append(CMD_C3_REL.format(cmd.ctrl - current, end - current))
            elif cmd.type == Command.CURVE4_TO:
                d.append(
                    CMD_C4_REL.format(
                        cmd.ctrl1 - current, cmd.ctrl2 - current, end - current
                    )
                )
            current = end
        if close:
            d.append("Z")

        return " ".join(d)

    def configure(self, config: Configuration) -> None:
        pass

    def clear(self) -> None:
        pass

    def finalize(self) -> None:
        pass

    def enter_entity(self, entity, properties) -> None:
        pass

    def exit_entity(self, entity) -> None:
        pass
