#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing_extensions import TypeAlias
import abc

from ezdxf.path import Path2d
from .font_measurements import FontMeasurements

GlyphPath: TypeAlias = Path2d


class Glyphs(abc.ABC):
    font_measurements: FontMeasurements
    space_width: float

    @abc.abstractmethod
    def get_scaling_factor(self, cap_height: float) -> float:
        ...

    @abc.abstractmethod
    def get_text_length(
        self, text: str, cap_height: float, width_factor: float = 1.0
    ) -> float:
        ...

    @abc.abstractmethod
    def get_text_path(
        self, text: str, cap_height: float, width_factor: float = 1.0
    ) -> GlyphPath:
        ...
