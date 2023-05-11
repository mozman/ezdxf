#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable, Sequence, no_type_check, NamedTuple
from typing_extensions import Self

import enum
import math
import itertools
import dataclasses
from xml.etree import ElementTree as ET

from ezdxf.math import AnyVec, Vec2, BoundingBox2d, Matrix44
from ezdxf.path import Path, Path2d, Command


from .type_hints import Color
from .backend import BackendInterface
from .config import Configuration
from .properties import BackendProperties, hex_to_rgb, rgb_to_hex
from .recorder import Recorder

__all__ = [
    "SVGBackend",
    "Settings",
    "Page",
    "Length",
    "Units",
    "StrokeWidthPolicy",
]


class Units(enum.IntEnum):
    """SVG units as enum.

    Attributes:
        inch: 25.4 mm
        px: 1/72 inch
        pt: 1/96 inch
        mm:
        cm:

    """

    # equivalent to ezdxf.units if possible
    inch = 1
    px = 2  # no equivalent DXF unit
    pt = 3  # no equivalent DXF unit
    mm = 4
    cm = 5


class StrokeWidthPolicy(enum.IntEnum):
    """This enum is used to define how to determine the stroke-width.

    Attributes:
        ABSOLUTE: in mm as resolved by the :class:`Frontend` class
        RELATIVE: in viewBox units relative to MAX_VIEW_BOX_COORDS
        FIXED_1: all strokes have the same stroke-width relative to MAX_VIEW_BOX_COORDS
    """

    ABSOLUTE = 1
    RELATIVE = 2
    FIXED_1 = 3


class Length(NamedTuple):
    """Length with units.

    Attributes:
        length:
        units:

    """

    length: float
    units: Units = Units.mm

    @property
    def in_mm(self) -> float:
        return self.length * CSS_UNITS_TO_MM[self.units]


CSS_UNITS_TO_MM = {
    Units.mm: 1.0,
    Units.cm: 10.0,
    Units.inch: 25.4,
    Units.px: 25.4 / 96.0,
    Units.pt: 25.4 / 72.0,
}

# all page sizes in landscape orientation
PAGE_SIZES = {
    "ISO A0": (1189, 841, Units.mm),
    "ISO A1": (841, 594, Units.mm),
    "ISO A2": (594, 420, Units.mm),
    "ISO A3": (420, 297, Units.mm),
    "ISO A4": (297, 210, Units.mm),
    "ANSI A": (11, 8.5, Units.inch),
    "ANSI B": (17, 11, Units.inch),
    "ANSI C": (22, 17, Units.inch),
    "ANSI D": (34, 22, Units.inch),
    "ANSI E": (44, 34, Units.inch),
    "ARCH C": (24, 18, Units.inch),
    "ARCH D": (36, 24, Units.inch),
    "ARCH E": (48, 36, Units.inch),
    "ARCH E1": (42, 30, Units.inch),
    "Letter": (11, 8.5, Units.inch),
    "Legal": (14, 8.5, Units.inch),
}

# The DXF coordinates are mapped to integer viewBox coordinates in the first
# quadrant, producing compact SVG files. The larger the coordinate range, the
# more precise and the lager the files.
MAX_VIEW_BOX_COORDS = 1_000_000


class Margins(NamedTuple):
    """Page margins definition class

    Attributes:
        top:
        left:
        bottom:
        right:

    """

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

    # noinspection PyArgumentList
    def scale(self, factor: float) -> Self:
        return self.__class__(
            self.top * factor,
            self.right * factor,
            self.bottom * factor,
            self.left * factor,
        )


@dataclasses.dataclass
class Page:
    """Page definition class

    Attributes:

        width: page width, 0 for auto-detect
        height: page height, 0 for auto-detect
        units: page units as enum :class:`Units`
        margins: page margins in page units

    """

    width: float
    height: float
    units: Units = Units.mm
    margins: Margins = Margins.all(0)

    def __post_init__(self):
        assert isinstance(self.units, Units), "units require type <Units>"
        assert isinstance(self.margins, Margins), "margins require type <Margins>"

    @property
    def width_in_mm(self) -> int:
        """Returns the page width in mm."""
        return round(Length(self.width, self.units).in_mm)

    @property
    def height_in_mm(self) -> int:
        """Returns the page height in mm."""
        return round(Length(self.height, self.units).in_mm)

    @property
    def margins_in_mm(self) -> Margins:
        """Returns the page margins in mm."""
        return self.margins.scale(CSS_UNITS_TO_MM[self.units])

    def to_landscape(self) -> None:
        """Converts the page to landscape orientation."""
        if self.width < self.height:
            self.width, self.height = self.height, self.width

    def to_portrait(self) -> None:
        """Converts the page to portrait orientation."""
        if self.height < self.width:
            self.width, self.height = self.height, self.width


@dataclasses.dataclass
class Settings:
    """The SVGBackend settings.

    Attributes:
        content_rotation: Rotate content about 0, 90,  180 or 270 degrees
        fit_page: Scale content to fit the page.
        scale: Factor to scale the DXF units of model- or paperspace, to represent 1mm
            in the rendered SVG drawing.

            e.g. scale 1:100 and DXF units are m, so 0.01 DXF units are 1mm in the SVG
            drawing or 1m = 1000mm corresponds to 10mm in the SVG drawing = 10 / 1000 = 0.01;

            e.g. scale 1:1; DXF units are mm = 1 / 1 = 1.0 the default value

            The value is ignored if the page size is defined and the content fits the page and
            the value is also used to determine missing page sizes (width or height).
        max_page_width: Limit auto-detected page width, 0 is for not limited
        max_page_height: Limit auto-detected page height, 0 is for not limited
        stroke_width_policy:
        max_stroke_width: Used for :class:`StrokeWidthPolicy.relative` policy,
            :attr:`max_stroke_width` is defined as percentage of the content extents,
            e.g. 0.001 is 0.1% of max(page-width, page-height)
        min_stroke_width: Used for :class:`StrokeWidthPolicy.relative` policy,
            :attr:`min_stroke_width` is defined as percentage of :attr:`max_stroke_width`,
            e.g. 0.05 is 5% of :attr:`max_stroke_width`
        fixed_stroke_width: Used for :class:`StrokeWidthPolicy.fixed_1` policy,
            :attr:`fixed_stroke_width` is defined as percentage of :attr:`max_stroke_width`,
            e.g. 0.15 is 15% of :attr:`max_stroke_width`
    """

    content_rotation: int = 0
    fit_page: bool = True
    scale: float = 1.0
    max_page_height: Length = Length(0, Units.mm)
    max_page_width: Length = Length(0, Units.mm)
    stroke_width_policy: StrokeWidthPolicy = StrokeWidthPolicy.ABSOLUTE
    # StrokeWidthPolicy.relative
    # max_stroke_width is defined as percentage of the content extents
    max_stroke_width: float = 0.001  # 0.1% of max(width, height) in viewBox coords
    # min_stroke_width is defined as percentage of max_stroke_width
    min_stroke_width: float = 0.05  # 5% of max_stroke_width
    # StrokeWidthPolicy.fixed_1
    # fixed_stroke_width is defined as percentage of max_stroke_width
    fixed_stroke_width: float = 0.15  # 15% of max_stroke_width

    def __post_init__(self) -> None:
        if self.content_rotation not in (0, 90, 180, 270):
            raise ValueError(
                f"invalid content rotation {self.content_rotation}, "
                f"expected: 0, 90, 180, 270"
            )
        assert isinstance(
            self.max_page_height, Length
        ), "max_page_height require type <Length>"
        assert isinstance(
            self.max_page_width, Length
        ), "max_page_width require type <Length>"


class SVGBackend(Recorder):
    def __init__(self) -> None:
        super().__init__()
        self._init_y_axis_flip = True

    def get_xml_root_element(self, page: Page, settings=Settings()) -> ET.Element:
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
        content_size = bbox.size
        if rotation in (90, 270):
            # swap x, y to apply rotation to content_size
            content_size = Vec2(content_size.y, content_size.x)
        page = final_page_size(content_size, page, settings)
        content_size_mm = content_size * settings.scale
        if settings.fit_page:
            content_size_mm *= fit_to_page(content_size_mm, page)
        scale_dxf_to_mm = content_size_mm.x / content_size.x
        # viewBox coordinates are integer values in the range [0, MAX_VIEW_BOX_COORDS]
        scale_mm_to_vb = MAX_VIEW_BOX_COORDS / max(page.width_in_mm, page.height_in_mm)

        scale = scale_dxf_to_mm * scale_mm_to_vb
        m = placement_matrix(
            bbox,
            sx=scale,
            sy=scale * flip_y,
            rotation=rotation,
            page=page,
        )
        self.transform(m)
        self._init_y_axis_flip = False
        backend = self.make_backend(page, settings)
        self.replay(backend)
        return backend.get_xml_root_element()

    @staticmethod
    def make_backend(page: Page, settings: Settings) -> SVGRenderBackend:
        """Override this method to use a customized render backend."""
        return SVGRenderBackend(page, settings)

    def get_string(self, page: Page, settings=Settings(), xml_declaration=True) -> str:
        """Returns the XML data as unicode string.

        Args:
            page: page definition
            settings: render settings
            xml_declaration: inserts the "<?xml version='1.0' encoding='utf-8'?>" string
                in front of the <svg> element

        """
        xml = self.get_xml_root_element(page, settings)
        return ET.tostring(xml, encoding="unicode", xml_declaration=xml_declaration)


def final_page_size(content_size: Vec2, page: Page, settings: Settings) -> Page:
    scale = settings.scale
    width = float(page.width_in_mm)
    height = float(page.height_in_mm)
    margins = page.margins_in_mm
    if width == 0.0:
        width = scale * content_size.x + margins.left + margins.right
    if height == 0.0:
        height = scale * content_size.y + margins.top + margins.bottom

    width, height = limit_page_size(
        width, height, settings.max_page_width.in_mm, settings.max_page_height.in_mm
    )
    return Page(round(width, 2), round(height, 2), Units.mm, margins)


def limit_page_size(
    width: float, height: float, max_width: float, max_height: float
) -> tuple[float, float]:
    ar = width / height
    if max_height:
        height = min(max_height, height)
        width = height * ar
    if max_width and width > max_width:
        width = min(max_width, width)
        height = width / ar
    return width, height


def fit_to_page(content_size_mm: Vec2, page: Page) -> float:
    margins = page.margins_in_mm
    sx = (page.width_in_mm - margins.left - margins.right) / content_size_mm.x
    sy = (page.height_in_mm - margins.top - margins.bottom) / content_size_mm.y
    return min(sx, sy)


def make_view_box(page: Page) -> tuple[int, int]:
    if page.width > page.height:
        return MAX_VIEW_BOX_COORDS, round(
            MAX_VIEW_BOX_COORDS * (page.height / page.width)
        )
    return round(MAX_VIEW_BOX_COORDS * (page.width / page.height)), MAX_VIEW_BOX_COORDS


def scale_page_to_view_box(page: Page) -> float:
    # The viewBox coordinates are integer values in the range of [0, MAX_VIEW_BOX_COORDS]
    return min(
        MAX_VIEW_BOX_COORDS / page.width,
        MAX_VIEW_BOX_COORDS / page.height,
    )


def placement_matrix(
    bbox: BoundingBox2d,
    sx: float,
    sy: float,
    rotation: float,
    page: Page,
) -> Matrix44:
    """Returns a matrix to place the bbox in the first quadrant of the coordinate
    system (+x, +y).
    """
    scale_mm_to_vb = MAX_VIEW_BOX_COORDS / max(page.width_in_mm, page.height_in_mm)
    margins = page.margins_in_mm

    # create scaling and rotation matrix:
    if abs(sx) < 1e-9:
        sx = 1.0
    if abs(sy) < 1e-9:
        sy = 1.0
    m = Matrix44.scale(sx, sy, 1.0)
    if rotation:
        m @= Matrix44.z_rotate(math.radians(rotation))

    # calc bounding box of the final output canvas:
    corners = m.transform_vertices(bbox.rect_vertices())
    canvas = BoundingBox2d(corners)

    # shift content to first quadrant +x/+y
    tx, ty = canvas.extmin  # type: ignore

    # center content within margins
    view_box_content_x = (
        page.width_in_mm - margins.left - margins.right
    ) * scale_mm_to_vb
    view_box_content_y = (
        page.height_in_mm - margins.top - margins.bottom
    ) * scale_mm_to_vb
    dx = view_box_content_x - canvas.size.x
    dy = view_box_content_y - canvas.size.y
    offset_x = margins.left * scale_mm_to_vb + dx / 2
    offset_y = margins.top * scale_mm_to_vb + dy / 2  # SVG origin is top/left
    return m @ Matrix44.translate(-tx + offset_x, -ty + offset_y, 0)


class Styles:
    def __init__(self, xml: ET.Element) -> None:
        self._xml = xml
        self._class_names: dict[int, str] = dict()
        self._counter = 1

    def get_class(
        self,
        *,
        stroke: Color = "none",
        stroke_width: int | str = "none",
        stroke_opacity: float = 1.0,
        fill: Color = "none",
        fill_opacity: float = 1.0,
    ) -> str:
        style = (
            f"{{stroke: {stroke}; "
            f"stroke-width: {stroke_width}; "
            f"stroke-opacity: {stroke_opacity:.3f}; "
            f"fill: {fill}; "
            f"fill-opacity: {fill_opacity:.3f};}}"
        )
        key = hash(style)
        try:
            return self._class_names[key]
        except KeyError:
            pass
        name = f"C{self._counter:X}"
        self._counter += 1
        self._add_class(name, style)
        self._class_names[key] = name
        return name

    def _add_class(self, name, style_str: str) -> None:
        style = ET.Element("style")
        style.text = f".{name} {style_str}"
        self._xml.append(style)


CMD_M_ABS = "M {0.x:.0f} {0.y:.0f}"
CMD_M_REL = "m {0.x:.0f} {0.y:.0f}"
CMD_L_ABS = "L {0.x:.0f} {0.y:.0f}"
CMD_L_REL = "l {0.x:.0f} {0.y:.0f}"
CMD_C3_ABS = "Q {0.x:.0f} {0.y:.0f} {1.x:.0f} {1.y:.0f}"
CMD_C3_REL = "q {0.x:.0f} {0.y:.0f} {1.x:.0f} {1.y:.0f}"
CMD_C4_ABS = "C {0.x:.0f} {0.y:.0f} {1.x:.0f} {1.y:.0f} {2.x:.0f} {2.y:.0f}"
CMD_C4_REL = "c {0.x:.0f} {0.y:.0f} {1.x:.0f} {1.y:.0f} {2.x:.0f} {2.y:.0f}"
CMD_CONT = "{0.x:.0f} {0.y:.0f}"


class SVGRenderBackend(BackendInterface):
    """Creates the SVG output.

    This backend requires some preliminary work, record the frontend output via the
    Recorder backend to accomplish the following requirements:

    - Scale the content in y-axis by -1 to invert the y-axis (SVG).
    - Move content in the first quadrant of the coordinate system.
    - The viewBox is defined by the lower left corner in the origin (0, 0) and
      the upper right corner at (view_box_width, view_box_height)
    - The output coordinates are integer values, scale the content appropriately.
    - Replay the recorded output on this backend.

    """

    def __init__(self, page: Page, settings: Settings) -> None:
        self.settings = settings
        self._stroke_width_cache: dict[float, int] = dict()
        view_box_width, view_box_height = make_view_box(page)
        # StrokeWidthPolicy.absolute:
        # stroke-width in mm as resolved by the frontend
        self.stroke_width_scale: float = view_box_width / page.width_in_mm
        self.min_lineweight = 0.05  # in mm, set by configure()

        # StrokeWidthPolicy.relative:
        # max_stroke_width is determined as a certain percentage of MAX_VIEW_BOX_COORDS
        self.max_stroke_width: int = int(
            MAX_VIEW_BOX_COORDS * settings.max_stroke_width
        )
        # min_stroke_width is determined as a certain percentage of max_stroke_width
        self.min_stroke_width: int = int(
            self.max_stroke_width * settings.min_stroke_width
        )
        # StrokeWidthPolicy.fixed_1:
        # all strokes have a fixed stroke-width as a certain percentage of max_stroke_width
        self.fixed_stroke_width: int = int(
            self.max_stroke_width * settings.fixed_stroke_width
        )
        self.root = ET.Element(
            "svg",
            xmlns="http://www.w3.org/2000/svg",
            width=f"{page.width:g}{page.units.name[:2]}",
            height=f"{page.height:g}{page.units.name[:2]}",
            viewBox=f"0 0 {view_box_width} {view_box_height}",
        )
        self.styles = Styles(ET.SubElement(self.root, "def"))
        self.background = ET.SubElement(
            self.root,
            "rect",
            fill="white",
            x="0",
            y="0",
            width=str(view_box_width),
            height=str(view_box_height),
        )
        self.entities = ET.SubElement(self.root, "g")
        self.entities.set("stroke-linecap", "round")
        self.entities.set("stroke-linejoin", "round")
        self.entities.set("fill-rule", "evenodd")

    def get_xml_root_element(self) -> ET.Element:
        return self.root

    def add_strokes(self, d: str, properties: BackendProperties):
        if not d:
            return
        element = ET.SubElement(self.entities, "path", d=d)
        stroke_width = self.resolve_stroke_width(properties.lineweight)
        stroke_color, stroke_opacity = self.resolve_color(properties.color)
        cls = self.styles.get_class(
            stroke=stroke_color,
            stroke_width=stroke_width,
            stroke_opacity=stroke_opacity,
        )
        element.set("class", cls)

    def add_filling(self, d: str, properties: BackendProperties):
        if not d:
            return
        element = ET.SubElement(self.entities, "path", d=d)
        fill_color, fill_opacity = self.resolve_color(properties.color)
        cls = self.styles.get_class(fill=fill_color, fill_opacity=fill_opacity)
        element.set("class", cls)

    def resolve_color(self, color: Color) -> tuple[Color, float]:
        return color[:7], alpha_to_opacity(color[7:9])

    def resolve_stroke_width(self, width: float) -> int:
        try:
            return self._stroke_width_cache[width]
        except KeyError:
            pass
        stroke_width = self.fixed_stroke_width
        policy = self.settings.stroke_width_policy
        if policy == StrokeWidthPolicy.ABSOLUTE:
            width = max(self.min_lineweight, width)
            stroke_width = round(width * self.stroke_width_scale)
        elif policy == StrokeWidthPolicy.RELATIVE:
            stroke_width = map_lineweight_to_stroke_width(
                width, self.min_stroke_width, self.max_stroke_width
            )
        self._stroke_width_cache[width] = stroke_width
        return stroke_width

    def set_background(self, color: Color) -> None:
        # Do not alter the background color here!
        color_str = color[:7]
        opacity = alpha_to_opacity(color[7:9])
        self.background.set("fill", color_str)
        self.background.set("fill-opacity", str(opacity))

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

    @staticmethod
    def make_polyline_str(points: Sequence[Vec2], close=False) -> str:
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

    @staticmethod
    def make_multi_line_str(lines: Sequence[tuple[Vec2, Vec2]]) -> str:
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

    @staticmethod
    @no_type_check
    def make_path_str(path: Path | Path2d, close=False) -> str:
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
        if config.min_lineweight:
            # config.min_lineweight in 1/300 inch!
            min_lineweight_mm = config.min_lineweight * 25.4 / 300
            self.min_lineweight = max(0.05, min_lineweight_mm)

    def clear(self) -> None:
        pass

    def finalize(self) -> None:
        pass

    def enter_entity(self, entity, properties) -> None:
        pass

    def exit_entity(self, entity) -> None:
        pass


def alpha_to_opacity(alpha: str) -> float:
    # stroke-opacity: 0.0 = transparent; 1.0 = opaque
    # alpha: "00" = transparent; "ff" = opaque
    if len(alpha):
        try:
            return int(alpha, 16) / 255
        except ValueError:
            pass
    return 1.0


def map_lineweight_to_stroke_width(
    lineweight: float,
    min_stroke_width: int,
    max_stroke_width: int,
    min_lineweight=0.05,  # defined by DXF
    max_lineweight=2.11,  # defined by DXF
) -> int:
    """Map the DXF lineweight in mm to stroke-width in viewBox coordinates."""
    lineweight = max(min(lineweight, max_lineweight), min_lineweight) - min_lineweight
    factor = (max_stroke_width - min_stroke_width) / (max_lineweight - min_lineweight)
    return min_stroke_width + round(lineweight * factor)
