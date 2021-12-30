#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from enum import IntEnum
from ezdxf.lldxf import const
from ezdxf.lldxf.const import (
    TextEntityAlignment,
    MTextFlowDirection,
    MTextLineAlignment,
    MTextStroke,
    MTextLineSpacing,
    MTextBackgroundColor,
)


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
