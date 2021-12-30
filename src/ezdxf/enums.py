#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from enum import IntEnum, IntFlag
from ezdxf.lldxf import const
from ezdxf.lldxf.const import TextEntityAlignment


class MTextEntityAlignment(IntEnum):
    """Text alignment enum for the :class:`~ezdxf.entities.MText` entity."""

    TOP_LEFT = const.MTEXT_TOP_LEFT
    TOP_CENTER = const.MTEXT_TOP_CENTER
    TOP_RIGHT = const.MTEXT_TOP_RIGHT
    MIDDLE_LEFT = const.MTEXT_MIDDLE_LEFT
    MIDDLE_CENTER = const.MTEXT_MIDDLE_CENTER
    MIDDLE_RIGHT = const.MTEXT_MIDDLE_RIGHT
    BOTTOM_LEFT = const.MTEXT_BOTTOM_LEFT
    BOTTOM_CENTER = const.MTEXT_BOTTOM_CENTER
    BOTTOM_RIGHT = const.MTEXT_BOTTOM_RIGHT


class MTextParagraphAlignment(IntEnum):
    DEFAULT = 0
    LEFT = 1
    RIGHT = 2
    CENTER = 3
    JUSTIFIED = 4
    DISTRIBUTED = 5


class MTextFlowDirection(IntEnum):
    LEFT_TO_RIGHT = const.MTEXT_LEFT_TO_RIGHT
    TOP_TO_BOTTOM = const.MTEXT_TOP_TO_BOTTOM
    BY_STYLE = const.MTEXT_BY_STYLE


class MTextLineAlignment(IntEnum):  # exclusive state
    BOTTOM = 0
    MIDDLE = 1
    TOP = 2


class MTextStroke(IntFlag):  # Combination of flags is possible
    UNDERLINE = 1
    STRIKE_THROUGH = 2
    OVERLINE = 4


class MTextLineSpacing(IntEnum):
    AT_LEAST = const.MTEXT_AT_LEAST
    EXACT = const.MTEXT_EXACT


class MTextBackgroundColor(IntEnum):
    OFF = const.MTEXT_BG_OFF
    COLOR = const.MTEXT_BG_COLOR
    WINDOW = const.MTEXT_BG_WINDOW_COLOR
    CANVAS = const.MTEXT_BG_CANVAS_COLOR


class InsertUnits(IntEnum):
    Unitless = 0
    Inches = 1
    Feet = 2
    Miles = 3
    Millimeters = 4
    Centimeters = 5
    Meters = 6
    Kilometers = 7
    Microinches = 8
    Mils = 9
    Yards = 10
    Angstroms = 11
    Nanometers = 12
    Microns = 13
    Decimeters = 14
    Decameters = 15
    Hectometers = 16
    Gigameters = 17
    AstronomicalUnits = 18
    Lightyears = 19
    Parsecs = 20
    USSurveyFeet = 21
    USSurveyInch = 22
    USSurveyYard = 23
    USSurveyMile = 24


class Measurement(IntEnum):
    Imperial = 0
    Metric = 1
