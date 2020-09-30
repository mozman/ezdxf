# Copyright (c) 2015-2020, Manfred Moitzi
# License: MIT License
from typing import Dict, List
from ezdxf.math import Vec2
from ._iso_pattern import ISO_PATTERN

# Predefined hatch pattern prior to ezdxf v0.11 were scaled for imperial units,
# and were too small for ISO units by a factor of 1/25.4, to replicate this
# pattern scaling use load(measurement=0).

__all__ = [
    'load', 'scale_pattern', 'scale_all', 'parse', 'ISO_PATTERN',
    'IMPERIAL_PATTERN'
]
IMPERIAL_SCALE_FACTOR = 1.0 / 25.4


def load(measurement: int = 1, factor: float = None):
    """ Load hatch pattern definition, default scaling is like the iso.pat of
    BricsCAD, set `measurement` to 0 to use the imperial (US) scaled pattern,
    which has a scaling factor of 1/25.4 = ~0.03937.

    Args:
        measurement: like the $MEASUREMENT header variable, 0 to user imperial
            scaled pattern, 1 to use ISO scaled pattern.
        factor: hatch pattern scaling factor, overrides `measurement`

    Returns: hatch pattern dict of scaled pattern

    """
    if factor is None:
        factor = 1.0 if measurement == 1 else IMPERIAL_SCALE_FACTOR
    pattern = ISO_PATTERN
    if factor != 1.0:
        pattern = scale_all(pattern, factor=factor)
    return pattern


def scale_pattern(pattern, factor: float = 1, angle: float = 0,
                  ndigits: int = 4):
    def _scale(iterable):
        return [round(i * factor, ndigits) for i in iterable]

    def _scale_line(line):
        angle0, base_point, offset, dash_length_items = line
        if angle:
            base_point = Vec2(base_point).rotate_deg(angle)
            offset = Vec2(offset).rotate_deg(angle)
            angle0 = (angle0 + angle) % 360.0

        return [
            round(angle0, ndigits),
            tuple(_scale(base_point)),
            tuple(_scale(offset)),
            _scale(dash_length_items)
        ]

    return [_scale_line(line) for line in pattern]


def scale_all(pattern: dict, factor: float = 1, angle: float = 0,
              ndigits: int = 4):
    return {name: scale_pattern(p, factor, angle, ndigits) for name, p in
            pattern.items()}


def parse(pattern: str) -> Dict:
    try:
        comp = PatternFileCompiler(pattern)
        return comp.compile_pattern()
    except Exception:
        raise ValueError('Incompatible pattern definition.')


def _tokenize_pattern_line(line: str) -> List:
    return line.split(',', maxsplit=1 if line.startswith('*') else -1)


class PatternFileCompiler:
    def __init__(self, content: str):
        self._lines = [
            _tokenize_pattern_line(line) for line in (
                line.strip() for line in content.split('\n')
            )
            if line and line[0] != ';'
        ]

    def _parse_pattern(self):
        pattern = []
        for line in self._lines:
            if line[0].startswith('*'):
                if pattern:
                    yield pattern
                pattern = [[line[0][1:], line[1]]]  # name, description
            else:
                pattern.append([float(e) for e in line])  # List[floats]

        if pattern:
            yield pattern

    def compile_pattern(self, ndigits: int = 10) -> Dict:
        pattern = dict()
        for p in self._parse_pattern():
            pat = []
            for line in p[1:]:
                # offset before rounding:
                offset = Vec2(line[3], line[4])

                # round all values:
                line = [round(e, ndigits) for e in line]
                pat_line = []

                angle = line[0]
                pat_line.append(angle)

                # base point:
                pat_line.append((line[1], line[2]))

                # rotate offset:
                offset = offset.rotate_deg(angle)
                pat_line.append((
                    round(offset.x, ndigits), round(offset.y, ndigits)
                ))

                # line dash pattern
                pat_line.append(line[5:])
                pat.append(pat_line)
            pattern[p[0][0]] = pat
        return pattern


IMPERIAL_PATTERN = load(measurement=0)
