#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Tuple
from ezdxf.math import Vec3
import abc


class FontMeasurements:
    def __init__(self, baseline: float, cap_height: float, x_height: float,
                 descender_height: float):
        self.baseline = baseline
        self.cap_height = cap_height
        self.x_height = x_height
        self.descender_height = descender_height

    def __eq__(self, other):
        return (isinstance(other, FontMeasurements) and
                self.baseline == other.baseline and
                self.cap_height == other.cap_height and
                self.x_height == other.x_height and
                self.descender_height == other.descender_height)

    def scale(self, factor: float = 1.0) -> 'FontMeasurements':
        return FontMeasurements(
            self.baseline,
            self.cap_height * factor,
            self.x_height * factor,
            self.descender_height * factor
        )

    def shift(self, distance: float = 0.0) -> 'FontMeasurements':
        return FontMeasurements(
            self.baseline + distance,
            self.cap_height,
            self.x_height,
            self.descender_height
        )

    def scale_from_baseline(
            self, desired_cap_height: float) -> 'FontMeasurements':
        return self.scale(desired_cap_height / self.cap_height)

    @property
    def cap_top(self) -> float:
        return self.baseline + self.cap_height

    @property
    def x_top(self) -> float:
        return self.baseline + self.x_height

    @property
    def bottom(self) -> float:
        return self.baseline - self.descender_height

    @property
    def total_height(self) -> float:
        return self.cap_height + self.descender_height


class AbstractFont:
    def __init__(self, measurements: FontMeasurements):
        self.measurements = measurements

    @abc.abstractmethod
    def text_width(self, text: str) -> float:
        pass


DESCENDER_FACTOR = 0.333  # from TXT SHX font - just guessing
X_HEIGHT_FACTOR = 0.666  # from TXT SHX font - just guessing


class MonospaceFont(AbstractFont):
    def __init__(self, height: float, width_factor: float = 1.0,
                 baseline: float = 0):
        super().__init__(FontMeasurements(
            baseline=baseline,
            cap_height=height,
            x_height=height * X_HEIGHT_FACTOR,
            descender_height=height * DESCENDER_FACTOR,
        ))
        self.width_factor = width_factor

    def text_width(self, text: str) -> float:
        return len(text) * self.measurements.cap_height * self.width_factor


class TextLine:
    def __init__(self, text: str, font: 'AbstractFont'):
        self._font = font
        self._text_width = font.text_width(text)
        self._stretch_x = 1.0
        self._stretch_y = 1.0

    def stretch(self, alignment: str, p1: Vec3, p2: Vec3) -> None:
        sx = 1.0
        sy = 1.0
        if alignment in ('FIT', 'ALIGNED'):
            defined_length = (p2 - p1).magnitude
            if self._text_width > 1e-9:
                sx = defined_length / self._text_width
                if alignment == 'ALIGNED':
                    sy = sx
        self._stretch_x = sx
        self._stretch_y = sy

    @property
    def width(self) -> float:
        return self._text_width * self._stretch_x

    @property
    def height(self) -> float:
        return self._font.measurements.total_height * self._stretch_y

    def font_measurements(self) -> FontMeasurements:
        return self._font.measurements.scale(self._stretch_y)
