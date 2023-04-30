#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Sequence, Iterator, Iterable, Optional
from typing_extensions import TypeAlias

from ezdxf import path

__all__ = ["loads", "LCFont", "Glyph"]


def loads(s: str) -> LCFont:
    lines = s.split("\n")
    name, letter_spacing, word_spacing = parse_properties(lines)
    lcf = LCFont(name, letter_spacing, word_spacing)
    for glyph, parent_code in parse_glyphs(lines):
        lcf.add(glyph, parent_code)
    return lcf


class LCFont:
    def __init__(
        self, name: str = "", letter_spacing: float = 0.0, word_spacing: float = 0.0
    ) -> None:
        self.name: str = name
        self.letter_spacing: float = letter_spacing
        self.word_spacing: float = word_spacing
        self._glyphs: dict[int, Glyph] = dict()

    def __len__(self) -> int:
        return len(self._glyphs)

    def __getitem__(self, item: int) -> Glyph:
        return self._glyphs[item]

    def add(self, glyph: Glyph, parent_code: int = 0) -> None:
        if parent_code:
            try:
                parent_glyph = self._glyphs[parent_code]
            except KeyError:
                return
            glyph = parent_glyph.extend(glyph)
        self._glyphs[glyph.code] = glyph

    def get(self, code: int) -> Optional[Glyph]:
        return self._glyphs.get(code, None)


Polyline: TypeAlias = Sequence[Sequence[float]]


class Glyph:
    __slots__ = ("code", "polylines")

    def __init__(self, code: int, polylines: Sequence[Polyline]):
        self.code: int = code
        self.polylines: Sequence[Polyline] = tuple(polylines)

    def extend(self, glyph: Glyph) -> Glyph:
        polylines = list(self.polylines)
        polylines.extend(glyph.polylines)
        return Glyph(glyph.code, polylines)

    def to_path(self) -> path.Path2d:
        from ezdxf.math import OCS

        p = path.Path()
        ocs = OCS()
        for polyline in self.polylines:
            path.add_2d_polyline(
                p, convert_bulge_values(polyline), close=False, elevation=0, ocs=ocs
            )
        return p.to_2d_path()


def convert_bulge_values(polyline: Polyline) -> Iterator[Sequence[float]]:
    # In DXF the bulge value is always stored at the start vertex of the arc.
    last_index = len(polyline) - 1
    for index, vertex in enumerate(polyline):
        bulge = 0.0
        if index < last_index:
            next_vertex = polyline[index + 1]
            try:
                bulge = next_vertex[2]
            except IndexError:
                pass
        yield vertex[0], vertex[1], bulge


def parse_properties(lines: list[str]) -> tuple[str, float, float]:
    font_name = ""
    letter_spacing = 0.0
    word_spacing = 0.0
    for line in lines:
        line = line.strip()
        if not line.startswith("#"):
            continue
        try:
            name, value = line.split(":")
        except ValueError:
            continue

        name = name[1:].strip()
        if name == "Name":
            font_name = value.strip()
        elif name == "LetterSpacing":
            try:
                letter_spacing = float(value)
            except ValueError:
                continue
        elif name == "WordSpacing":
            try:
                word_spacing = float(value)
            except ValueError:
                continue
    return font_name, letter_spacing, word_spacing


def scan_glyphs(lines: Iterable[str]) -> Iterator[list[str]]:
    glyph: list[str] = []
    for line in lines:
        if line.startswith("["):
            if glyph:
                yield glyph
            glyph.clear()
        if line:
            glyph.append(line)
    if glyph:
        yield glyph


def strip_clutter(lines: list[str]) -> Iterator[str]:
    for line in lines:
        line = line.strip()
        if not line.startswith("#"):
            yield line


def parse_glyphs(lines: list[str]) -> Iterator[tuple[Glyph, int]]:
    parent_code: int = 0
    code: int
    polylines: list[Polyline] = []
    for glyph in scan_glyphs(strip_clutter(lines)):
        polylines.clear()
        line = glyph.pop(0)
        try:
            code = int(line[1 : line.index("]")], 16)
        except ValueError:
            continue
        line = glyph[0]
        if line.startswith("C"):
            glyph.pop(0)
            try:
                parent_code = int(line[1:], 16)
            except ValueError:
                continue
        polylines = list(parse_polylines(glyph))
        yield Glyph(code, polylines), parent_code


def parse_polylines(lines: Iterable[str]) -> Iterator[Polyline]:
    polyline: list[Sequence[float]] = []
    for line in lines:
        polyline.clear()
        for vertex in line.split(";"):
            values = to_floats(vertex.split(","))
            if len(values) > 1:
                polyline.append(values[:3])
        yield tuple(polyline)


def to_floats(values: Iterable[str]) -> Sequence[float]:
    def strip(value: str) -> float:
        if value.startswith("A"):
            value = value[1:]
        try:
            return float(value)
        except ValueError:
            return 0.0

    return tuple(strip(value) for value in values)
