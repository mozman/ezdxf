#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import NamedTuple, TYPE_CHECKING
from typing_extensions import Self

import math
import enum
import dataclasses
from ezdxf.math import Vec2, BoundingBox2d, Matrix44

if TYPE_CHECKING:
    from ezdxf.layouts.layout import Layout as DXFLayout


class Units(enum.IntEnum):
    """Page units as enum.

    Attributes:
        inch: 25.4 mm
        px: 1/96 inch
        pt: 1/72 inch
        mm:
        cm:

    """

    # equivalent to ezdxf.units if possible
    inch = 1
    px = 2  # no equivalent DXF unit
    pt = 3  # no equivalent DXF unit
    mm = 4
    cm = 5


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


UNITS_TO_MM = {
    Units.mm: 1.0,
    Units.cm: 10.0,
    Units.inch: 25.4,
    Units.px: 25.4 / 96.0,
    Units.pt: 25.4 / 72.0,
}


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
        max_width: limit width for auto-detection, 0 for unlimited
        max_height: limit height for auto-detection, 0 for unlimited

    """

    width: float
    height: float
    units: Units = Units.mm
    margins: Margins = Margins.all(0)
    max_width: float = 0.0
    max_height: float = 0.0

    def __post_init__(self):
        assert isinstance(self.units, Units), "units require type <Units>"
        assert isinstance(self.margins, Margins), "margins require type <Margins>"

    @property
    def to_mm_factor(self) -> float:
        return UNITS_TO_MM[self.units]

    @property
    def width_in_mm(self) -> float:
        """Returns the page width in mm."""
        return round(self.width * self.to_mm_factor, 1)

    @property
    def max_width_in_mm(self) -> float:
        """Returns max page width in mm."""
        return round(self.max_width * self.to_mm_factor, 1)

    @property
    def height_in_mm(self) -> float:
        """Returns the page height in mm."""
        return round(self.height * self.to_mm_factor, 1)

    @property
    def max_height_in_mm(self) -> float:
        """Returns max page height in mm."""
        return round(self.max_height * self.to_mm_factor, 1)

    @property
    def margins_in_mm(self) -> Margins:
        """Returns the page margins in mm."""
        return self.margins.scale(self.to_mm_factor)

    @property
    def is_landscape(self) -> bool:
        """Returns ``True`` if the page has landscape orientation."""
        return self.width > self.height

    @property
    def is_portrait(self) -> bool:
        """Returns ``True`` if the page has portrait orientation. (square is portrait)"""
        return self.width <= self.height

    def to_landscape(self) -> None:
        """Converts the page to landscape orientation."""
        if self.is_portrait:
            self.width, self.height = self.height, self.width

    def to_portrait(self) -> None:
        """Converts the page to portrait orientation."""
        if self.is_landscape:
            self.width, self.height = self.height, self.width

    @classmethod
    def from_dxf_layout(cls, layout: DXFLayout) -> Self:
        # all layout measurements in mm
        width = round(layout.dxf.paper_width, 1)
        height = round(layout.dxf.paper_height, 1)
        top = round(layout.dxf.top_margin, 1)
        right = round(layout.dxf.right_margin, 1)
        bottom = round(layout.dxf.bottom_margin, 1)
        left = round(layout.dxf.left_margin, 1)

        rotation = layout.dxf.plot_rotation
        if rotation == 1:  # 90 degrees
            return cls(
                height,
                width,
                Units.mm,
                margins=Margins(top=right, right=bottom, bottom=left, left=top),
            )
        elif rotation == 2:  # 180 degrees
            return cls(
                width,
                height,
                Units.mm,
                margins=Margins(top=bottom, right=left, bottom=top, left=right),
            )
        elif rotation == 3:  # 270 degrees
            return cls(
                height,
                width,
                Units.mm,
                margins=Margins(top=left, right=top, bottom=right, left=bottom),
            )
        return cls(  # 0 degrees
            width,
            height,
            Units.mm,
            margins=Margins(top=top, right=right, bottom=bottom, left=left),
        )


@dataclasses.dataclass
class Settings:
    """The Layout settings.

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
        max_stroke_width: Used for :class:`LineweightPolicy.RELATIVE` policy,
            :attr:`max_stroke_width` is defined as percentage of the content extents,
            e.g. 0.001 is 0.1% of max(page-width, page-height)
        min_stroke_width: Used for :class:`LineweightPolicy.RELATIVE` policy,
            :attr:`min_stroke_width` is defined as percentage of :attr:`max_stroke_width`,
            e.g. 0.05 is 5% of :attr:`max_stroke_width`
        fixed_stroke_width: Used for :class:`LineweightPolicy.RELATIVE_FIXED` policy,
            :attr:`fixed_stroke_width` is defined as percentage of :attr:`max_stroke_width`,
            e.g. 0.15 is 15% of :attr:`max_stroke_width`
        output_coordinate_space: expert feature to map the DXF coordinates to the
            output coordinate system [0, output_coordinate_space]

    """

    content_rotation: int = 0
    fit_page: bool = True
    scale: float = 1.0
    # for LineweightPolicy.RELATIVE
    # max_stroke_width is defined as percentage of the content extents
    max_stroke_width: float = 0.001  # 0.1% of max(width, height) in viewBox coords
    # min_stroke_width is defined as percentage of max_stroke_width
    min_stroke_width: float = 0.05  # 5% of max_stroke_width
    # StrokeWidthPolicy.fixed_1
    # fixed_stroke_width is defined as percentage of max_stroke_width
    fixed_stroke_width: float = 0.15  # 15% of max_stroke_width

    # PDF, HPGL expect the coordinates in the first quadrant and SVG has an inverted
    # y-axis, so transformation from DXF to the output coordinate system is required.
    # The output_coordinate_space defines the space into which the DXF coordinates are
    # mapped, the range is [0, output_coordinate_space] for the larger page
    # dimension - aspect ratio is always preserved - these are CAD drawings!
    # The SVGBackend uses this feature to map all coordinates to integer values:
    output_coordinate_space: float = 1_000_000  # e.g. for SVGBackend

    def __post_init__(self) -> None:
        if self.content_rotation not in (0, 90, 180, 270):
            raise ValueError(
                f"invalid content rotation {self.content_rotation}, "
                f"expected: 0, 90, 180, 270"
            )


class Layout:
    def __init__(self, dxf_bbox: BoundingBox2d, flip_y=False) -> None:
        super().__init__()
        self.flip_y: float = -1.0 if flip_y else 1.0
        self.dxf_bbox = dxf_bbox

    def get_rotation(self, settings: Settings) -> int:
        if settings.content_rotation not in (0, 90, 180, 270):
            raise ValueError("content rotation must be 0, 90, 180 or 270 degrees")
        rotation = settings.content_rotation
        if self.flip_y == -1.0:
            if rotation == 90:
                rotation = 270
            elif rotation == 270:
                rotation = 90
        return rotation

    def get_content_size(self, rotation: int) -> Vec2:
        content_size = self.dxf_bbox.size
        if rotation in (90, 270):
            # swap x, y to apply rotation to content_size
            content_size = Vec2(content_size.y, content_size.x)
        return content_size

    def get_final_page(self, page: Page, settings: Settings) -> Page:
        rotation = self.get_rotation(settings)
        content_size = self.get_content_size(rotation)
        return final_page_size(content_size, page, settings)

    def get_placement_matrix(self, page: Page, settings=Settings()) -> Matrix44:
        # Argument `page` has to be the resolved final page size!

        rotation = self.get_rotation(settings)

        content_size = self.get_content_size(rotation)
        content_size_mm = content_size * settings.scale
        if settings.fit_page:
            content_size_mm *= fit_to_page(content_size_mm, page)
        scale_dxf_to_mm = content_size_mm.x / content_size.x
        # map output coordinates to range [0, output_coordinate_space]
        scale_mm_to_output_space = settings.output_coordinate_space / max(
            page.width_in_mm, page.height_in_mm
        )

        scale = scale_dxf_to_mm * scale_mm_to_output_space
        m = placement_matrix(
            self.dxf_bbox,
            sx=scale,
            sy=scale * self.flip_y,
            rotation=rotation,
            page=page,
            output_coordinate_space=settings.output_coordinate_space,
        )
        return m


def final_page_size(content_size: Vec2, page: Page, settings: Settings) -> Page:
    scale = settings.scale
    width = page.width_in_mm
    height = page.height_in_mm
    margins = page.margins_in_mm
    if width == 0.0:
        width = scale * content_size.x + margins.left + margins.right
    if height == 0.0:
        height = scale * content_size.y + margins.top + margins.bottom

    width, height = limit_page_size(
        width, height, page.max_width_in_mm, page.max_height_in_mm
    )
    return Page(round(width, 1), round(height, 1), Units.mm, margins)


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


def placement_matrix(
    bbox: BoundingBox2d,
    sx: float,
    sy: float,
    rotation: float,
    page: Page,
    output_coordinate_space: float,
) -> Matrix44:
    """Returns a matrix to place the bbox in the first quadrant of the coordinate
    system (+x, +y).
    """
    scale_mm_to_vb = output_coordinate_space / max(page.width_in_mm, page.height_in_mm)
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
