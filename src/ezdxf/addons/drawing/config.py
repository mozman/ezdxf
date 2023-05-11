# Copyright (c) 2021-2022, Matthew Broadway
# License: MIT License
from __future__ import annotations
from typing import Optional
import dataclasses
from dataclasses import dataclass
from enum import Enum, auto

from ezdxf import disassemble
from ezdxf.enums import Measurement
from .type_hints import Color

class LinePolicy(Enum):
    """
    Attributes:
        SOLID: draw all lines as solid regardless of the linetype style
        APPROXIMATE: use the closest approximation available to the
            backend for rendering styled lines
        ACCURATE: analyse and render styled lines as accurately as
            possible. This approach is slower and is not well suited
            to interactive applications.
    """

    SOLID = auto()
    APPROXIMATE = auto()  # ignored since v0.18.1 => ACCURATE
    ACCURATE = auto()


class ProxyGraphicPolicy(Enum):
    """The action to take when an entity with a proxy graphic is encountered

    .. note::

        To get proxy graphics support proxy graphics have to be loaded:
        Set the global option :attr:`ezdxf.options.load_proxy_graphics` to
        ``True``, which is the default value.

        This can not prevent drawing proxy graphic inside of blocks,
        because this is outside of the domain of the drawing add-on!

    Attributes:
        IGNORE: do not display proxy graphics (skip_entity will be called instead)
        SHOW: if the entity cannot be rendered directly (eg if not implemented)
            but a proxy is present: display the proxy
        PREFER: display proxy graphics even for entities where direct rendering
            is available
    """

    IGNORE = auto()
    SHOW = auto()
    PREFER = auto()


class HatchPolicy(Enum):
    """The action to take when a HATCH entity is encountered

    Attributes:
        IGNORE: do not show HATCH entities at all
        SHOW_OUTLINE: show only the outline of HATCH entities
        SHOW_SOLID: show HATCH entities but draw with solid fill
            regardless of the pattern
    """

    IGNORE = auto()
    SHOW_OUTLINE = auto()
    SHOW_SOLID = auto()
    SHOW_APPROXIMATE_PATTERN = auto()  # ignored since v0.18.1


class ColorPolicy(Enum):
    """This enum is used to define how to determine the line/fill color.

    Attributes:
        COLOR: as resolved by the :class:`Frontend` class
        COLOR_SWAP_BW: as resolved by the :class:`Frontend` class but swaps black and white
        COLOR_NEGATIVE: invert colors
        MONOCHROME_BLACK_BG: all colors to gray scale for black background
        MONOCHROME_WHITE_BG:  all colors to gray scale for white background
        BLACK: all colors to black
        WHITE: all colors to white
        CUSTOM: all colors to custom color by :attr:`Configuration.custom_fg_color`

    """
    COLOR = auto()
    COLOR_SWAP_BW = auto()
    COLOR_NEGATIVE = auto()
    MONOCHROME_BLACK_BG = auto()
    MONOCHROME_WHITE_BG = auto()
    BLACK = auto()
    WHITE = auto()
    CUSTOM = auto()


class BackgroundPolicy(Enum):
    """This enum is used to define the background color.

    Attributes:
        DEFAULT: as resolved by the :class:`Frontend` class
        WHITE: white background
        BLACK: black background
        OFF: fully transparent background
        CUSTOM: custom background color by :attr:`Configuration.custom_bg_color`

    """
    DEFAULT = auto()
    WHITE = auto()
    BLACK = auto()
    OFF = auto()
    CUSTOM = auto()


@dataclass(frozen=True)
class Configuration:
    """Configuration options for the :mod:`drawing` add-on.

    Attributes:
        pdsize: the size to draw POINT entities (in drawing units)
            set to None to use the $PDSIZE value from the dxf document header

            ======= ====================================================
            0       5% of draw area height
            <0      Specifies a percentage of the viewport size
            >0      Specifies an absolute size
            None    use the $PDMODE value from the dxf document header
            ======= ====================================================

        pdmode: point styling mode (see POINT documentation)

            see :class:`~ezdxf.entities.Point` class documentation

        measurement: whether to use metric or imperial units as enum :class:`ezdxf.enums.Measurement`

            ======= ======================================================
            0       use imperial units (in, ft, yd, ...)
            1       use metric units (ISO meters)
            None    use the $MEASUREMENT value from the dxf document header
            ======= ======================================================

        show_defpoints: whether to show or filter out POINT entities on the defpoints layer
        proxy_graphic_policy: the action to take when a proxy graphic is encountered
        line_policy: the method to use when drawing styled lines (eg dashed,
            dotted etc)
        hatch_policy: the method to use when drawing HATCH entities
        infinite_line_length: the length to use when drawing infinite lines
        lineweight_scaling:
            multiplies every lineweight by this factor; set this factor to 0.0 for a
            constant minimum line width defined by the :attr:`min_lineweight` setting
            for all lineweights;
            the correct DXF lineweight often looks too thick in SVG, so setting a
            factor < 1 can improve the visual appearance
        min_lineweight: the minimum line width in 1/300 inch; set to ``None`` for
            let the backend choose.
        min_dash_length: the minimum length for a dash when drawing a styled line
            (default value is arbitrary)
        max_flattening_distance: Max flattening distance in drawing units
            see Path.flattening documentation.
            The backend implementation should calculate an appropriate value,
            like 1 screen- or paper pixel on the output medium, but converted
            into drawing units. Sets Path() approximation accuracy
        circle_approximation_count: Approximate a full circle by `n` segments, arcs
            have proportional less segments. Only used for approximation of arcs
            in banded polylines.
        hatching_timeout: hatching timeout for a single entity, very dense
            hatching patterns can cause a very long execution time, the default
            timeout for a single entity is 30 seconds.
        color_policy:
        custom_fg_color: Used for :class:`ColorPolicy.custom` policy, custom foreground
            color as "#RRGGBBAA" color string (RGB+alpha)
        background_policy:
        custom_bg_color: Used for :class:`BackgroundPolicy.custom` policy, custom
            background color as "#RRGGBBAA" color string (RGB+alpha)

    """

    pdsize: Optional[int] = None  # use $PDSIZE from HEADER section
    pdmode: Optional[int] = None  # use $PDMODE from HEADER section
    measurement: Optional[Measurement] = None
    show_defpoints: bool = False
    proxy_graphic_policy: ProxyGraphicPolicy = ProxyGraphicPolicy.SHOW
    line_policy: LinePolicy = LinePolicy.APPROXIMATE
    hatch_policy: HatchPolicy = HatchPolicy.SHOW_APPROXIMATE_PATTERN
    infinite_line_length: float = 20
    lineweight_scaling: float = 1.0
    min_lineweight: Optional[float] = None
    min_dash_length: float = 0.1
    max_flattening_distance: float = disassemble.Primitive.max_flattening_distance
    circle_approximation_count: int = 128
    hatching_timeout: float = 30.0
    color_policy: ColorPolicy = ColorPolicy.COLOR
    custom_fg_color: Color = "#000000"
    background_policy: BackgroundPolicy = BackgroundPolicy.DEFAULT
    custom_bg_color: Color = "#ffffff"

    @staticmethod
    def defaults() -> Configuration:
        return Configuration()

    def with_changes(self, **kwargs) -> Configuration:
        params = dataclasses.asdict(self)
        for k, v in kwargs.items():
            params[k] = v
        return Configuration(**params)
