# Created: 2019-01-05
# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
from typing import Optional

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

    def from_msp(self, value: float, unit: str):
        drawing_units = value * self._msp(unit.lower())
        return drawing_units / (self._msp(self.unit) * self.scale)

    def to_msp(self, value: float, unit: str):
        paper_space_units = value * self.scale * self._psp.factor(unit)
        model_space_units = paper_space_units * self._msp.factor(self.unit)
        return model_space_units


# Layout units are stored as enum in the associated BLOCK_RECORD: BlockRecord.dxf.units
# or as  optional XDATA for all DXF versions
# 1000: "ACAD"
# 1001: "DesignCenter Data" (optional)
# 1002: "{"
# 1070: Autodesk Design Center version number
# 1070: Insert units: like 'units'
# 1002: "}"
# The model space units are also stored as enum in the header var $INSUNITS

# units stored as enum in BlockRecord.dxf.units
# 0 = Unitless
# 1 = Inches
# 2 = Feet
# 3 = Miles
# 4 = Millimeters
# 5 = Centimeters
# 6 = Meters
# 7 = Kilometers
# 8 = Microinches = 1e-6 in
# 9 = Mils = 0.001 in
# 10 = Yards
# 11 = Angstroms = 1e-10m
# 12 = Nanometers = 1e-9m
# 13 = Microns = 1e-6m
# 14 = Decimeters = 0.1m
# 15 = Decameters = 10m
# 16 = Hectometers = 100m
# 17 = Gigameters = 1e+9 m
# 18 = Astronomical units = 149597870700m = 1.58125074e−5 ly =  4.84813681e−6 Parsec
# 19 = Light years = 9.46e15 m
# 20 = Parsecs =  3.09e16 m
# 21 = US Survey Feet
# 22 = US Survey Inch
# 23 = US Survey Yard
# 24 = US Survey Mile
_unit_spec = [
    None, 'in', 'ft', 'mi', 'mm', 'cm', 'm', 'km',
    'µin', 'mil', 'yd', 'Å', 'nm', 'µm', 'dm', 'dam', 'hm', 'gm',
    'au', 'ly', 'pc',
    None, None, None, None,
]


def decode(enum: int) -> Optional[str]:
    return _unit_spec[int(enum)]
