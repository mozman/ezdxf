#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

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
