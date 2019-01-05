# Created: 2019-01-05
# Copyright (c) 2019 Manfred Moitzi
# License: MIT License

MSP_METRIC_UNITS_FACTORS = {
    'km': .001,
    'm': 1.0,
    'dm': 10.,
    'cm': 100.,
    'mm': 1000.,
    'µm': 1000000.,
    'yd': 1.093613298,
    'ft': 3.280839895,
    'in': 39.37007874,
    'mi': 0.00062137119,
}


class DrawingUnits:
    def __init__(self, base: float = 1., unit: str = 'm'):
        self.base = float(base)
        self.unit = unit.lower()
        self._units = MSP_METRIC_UNITS_FACTORS
        self._msp_factor = base * self._units[self.unit]

    def factor(self, unit: str = 'm') -> float:
        return self._msp_factor / self._units[unit.lower()]

    def __call__(self, unit: str) -> float:
        return self.factor(unit)


class PaperSpaceUnits:
    def __init__(self, msp=DrawingUnits(), unit: str = 'mm', scale: float = 1):
        self.unit = unit.lower()
        self.scale = scale
        self._msp = msp
        self._psp = DrawingUnits(1, self.unit)

    def msp_to_psp(self, value: float, unit: str):
        drawing_units = value * self._msp(unit.lower())
        return drawing_units / (self._msp(self.unit) * self.scale)

    def psp_to_msp(self, value: float, unit: str):
        paper_space_units = value * self.scale * self._psp.factor(unit)
        model_space_units = paper_space_units * self._msp.factor(self.unit)
        return model_space_units
