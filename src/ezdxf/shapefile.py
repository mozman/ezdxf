#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

"""
This module provides support for fonts stored as SHX and SHP files.
(SHP is not the GIS file format!)

The documentation about the SHP file format can be found at Autodesk:
https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-DE941DB5-7044-433C-AA68-2A9AE98A5713

"""
import math
from typing import Dict, Sequence, Iterable, Iterator, Callable, List, Tuple
import enum
from ezdxf import path
from ezdxf.math import UVec, Vec2, Vec3, ConstructionEllipse, bulge_to_arc


class ShapeFileException(Exception):
    pass


class UnsupportedShapeFile(ShapeFileException):
    pass


class InvalidFontDefinition(ShapeFileException):
    pass


class InvalidFontParameters(ShapeFileException):
    pass


class InvalidShapeRecord(ShapeFileException):
    pass


class FileStructureError(ShapeFileException):
    pass


class StackUnderflow(ShapeFileException):
    pass


class FontEmbedding(enum.IntEnum):
    ALLOWED = 0
    DISALLOWED = 1
    READONLY = 2


class FontEncoding(enum.IntEnum):
    UNICODE = 0
    PACKED_MULTIBYTE_1 = 1
    SHAPE_FILE = 2


class FontMode(enum.IntEnum):
    HORIZONTAL = 0
    BIDIRECT = 2


class Symbol:
    def __init__(self, number: int, name: str):
        self.number = number
        self.name = name
        self.data: Sequence[int] = []


class ShapeFile:
    def __init__(
        self,
        name: str,
        above: int,
        below: int,
        mode=FontMode.HORIZONTAL,
        encoding=FontEncoding.UNICODE,
        embed=FontEmbedding.ALLOWED,
    ):
        self.symbols: Dict[int, Symbol] = dict()
        self.name = name
        self.above = above
        self.below = below
        self.mode = mode
        self.encoding = encoding
        self.embed = embed

    @property
    def cap_height(self) -> float:
        return float(self.above)

    @property
    def descender(self) -> float:
        return float(self.below)

    @staticmethod
    def from_str_record(record: Sequence[str]):
        if len(record) == 2:
            header, params = record
            try:
                # ignore second value: defbytes
                spec, _, name = header.split(",", maxsplit=2)
            except ValueError:
                raise InvalidFontDefinition()
            if spec == "*UNIFONT":
                try:
                    above, below, mode, encoding, embed, end = params.split(",")
                except ValueError:
                    raise InvalidFontParameters(params)
            elif spec == "*0":
                try:
                    above, below, mode, end = params.split(",")
                    encoding = FontEncoding.UNICODE
                    embed = FontEmbedding.ALLOWED
                except ValueError:
                    raise InvalidFontParameters(params)
            else:
                raise InvalidFontDefinition(header)

            assert int(end) == 0

            return ShapeFile(
                name.strip(),
                int(above),
                int(below),
                FontMode(int(mode)),
                FontEncoding(int(encoding)),
                FontEmbedding(int(embed)),
            )

    def parse_str_records(self, records: Iterable[Sequence[str]]) -> None:
        for record in records:
            if len(record) < 2:
                raise InvalidShapeRecord()
            # ignore second value: defbytes
            number, _, name = split_record(record[0])
            int_num = int(number[1:], 16)
            symbol = Symbol(int_num, name)
            data = "".join(record[1:])
            symbol.data = tuple(parse_codes(split_record(data)))
            if symbol.data[-1] == 0:
                self.symbols[int_num] = symbol
            else:
                raise FileStructureError(
                    f"file structure error at symbol <{record[0]}>"
                )

    def get_codes(self, number: int) -> Sequence[int]:
        symbol = self.symbols.get(number)
        if symbol is None:
            return tuple()  # return codes for non-printable chars
        return symbol.data

    def render_shape(self, number: int, stacked=False) -> path.Path:
        return render_shapes([number], self.get_codes, stacked=stacked)

    def render_shapes(self, numbers: Sequence[int], stacked=False) -> path.Path:
        return render_shapes(numbers, self.get_codes, stacked=stacked)

    def render_text(self, text: str, stacked=False) -> path.Path:
        numbers = [ord(char) for char in text]
        return render_shapes(numbers, self.get_codes, stacked=stacked)


def split_record(record: str) -> Sequence[str]:
    return tuple(s.strip() for s in record.split(","))


def parse_codes(codes: Iterable[str]) -> Iterator[int]:
    for code in codes:
        code = code.strip("()")
        if code[0] == "0":
            yield int(code, 16)
        elif code[0] == "-" and code[1] == "0":
            yield int(code, 16)
        else:
            yield int(code, 10)


def shp_loads(data: str) -> ShapeFile:
    records = _parse_string_records(data)
    if "*UNIFONT" in records:
        font_definition = records.pop("*UNIFONT")
    elif "*0" in records:
        font_definition = records.pop("*0")
    else:
        raise UnsupportedShapeFile()
    shp = ShapeFile.from_str_record(font_definition)
    shp.parse_str_records(records.values())
    return shp


def shp_dumps(shapefile: ShapeFile) -> str:
    return ""


def shx_loadb(data: bytes) -> ShapeFile:
    return ShapeFile("", 0, 0)


def shx_dumpb(shapefile: ShapeFile) -> bytes:
    return b""


def _parse_string_records(data: str) -> Dict[str, Sequence[str]]:
    records: Dict[str, Sequence[str]] = dict()
    name = None
    lines = []
    for line in _filter_comments(data.split("\n")):
        if line.startswith("*"):
            if name is not None:
                records[name] = tuple(lines)
            name = line.split(",")[0].strip()
            lines = [line]
        else:
            lines.append(line)

    if name is not None:
        records[name] = tuple(lines)
    return records


def _filter_comments(lines: Iterable[str]) -> Iterator[str]:
    for line in lines:
        line = line.strip()
        line = line.split(";")[0]
        if line:
            yield line


def render_shapes(
    shape_numbers: Sequence[int],
    get_codes: Callable[[int], Sequence[int]],
    stacked: bool,
    start: UVec = (0, 0),
) -> path.Path:
    ctx = ShapeRenderer(
        path.Path(start),
        pen=True,
        stacked=stacked,
        get_codes=get_codes,
    )
    for shape_number in shape_numbers:
        codes = get_codes(shape_number)
        try:
            ctx.render(codes)
        except StackUnderflow:
            raise StackUnderflow(
                f"stack underflow while rendering shape number {shape_number}"
            )
        # move cursor to the start of the next char???
    return ctx.p


#        0, 1, 2,   3, 4,    5,  6,  7,  8,  9,  A,    B, C,   D, E, F
VEC_X = [1, 1, 1, 0.5, 0, -0.5, -1, -1, -1, -1, -1, -0.5, 0, 0.5, 1, 1]
#        0,   1, 2, 3, 4, 5, 6,   7, 8,    9,  A,  B,  C,  D,  E,    F
VEC_Y = [0, 0.5, 1, 1, 1, 1, 1, 0.5, 0, -0.5, -1, -1, -1, -1, -1, -0.5]


class ShapeRenderer:
    def __init__(
        self,
        p: path.Path,
        get_codes: Callable[[int], Sequence[int]],
        *,
        vector_length: float = 1.0,
        pen: bool = True,
        stacked: bool = False,
    ):
        self.p = p
        self.vector_length = float(vector_length)  # initial vector length
        self.pen = pen  # pen down =  True, pen up = False
        self.stacked = stacked  # vertical stacked text
        self._location_stack: List[Vec3] = []
        self._get_codes = get_codes

    @property
    def current_location(self) -> Vec3:
        return self.p.end

    def push(self) -> None:
        self._location_stack.append(self.current_location)

    def pop(self) -> None:
        self.p.move_to(self._location_stack.pop())

    def render(
        self,
        codes: Sequence[int],
    ) -> None:
        index = 0
        skip_next = False
        while index < len(codes):
            code = codes[index]
            index += 1
            if code > 15 and not skip_next:
                self.draw_vector(code)
            elif code == 0:
                break
            elif code == 1 and not skip_next:  # pen down
                self.pen = True
            elif code == 2 and not skip_next:  # pen up
                self.pen = False
            elif code == 3 or code == 4:  # scale size
                factor = codes[index]
                index += 1
                if not skip_next:
                    if code == 3 and factor:
                        self.vector_length /= factor
                    elif code == 4:
                        self.vector_length *= factor
            elif code == 5 and not skip_next:  # push location state
                self.push()
            elif code == 6 and not skip_next:  # pop location state
                try:
                    self.pop()
                except IndexError:
                    raise StackUnderflow()
            elif code == 7:  # sub-shape:
                sub_shape_number = codes[index]
                index += 1
                if not skip_next:
                    sub_codes = self._get_codes(sub_shape_number)
                    # Use current state of pen and location!
                    self.render(sub_codes)
                    # resume with current state of pen and location!
            elif code == 8:  # displacement vector
                x = codes[index]
                y = codes[index + 1]
                index += 2
                if not skip_next:
                    self.draw_displacement(x, y)
            elif code == 9:  # multiple displacements vectors
                while True:
                    x = codes[index]
                    y = codes[index + 1]
                    index += 2
                    if x == 0 and y == 0:
                        break
                    if not skip_next:
                        self.draw_displacement(x, y)
            elif code == 0xA:  # octant arc
                radius = codes[index]
                start_octant, octant_span, ccw = decode_octant_specs(
                    codes[index + 1]
                )
                index += 2
                if not skip_next:
                    self.draw_arc_span(
                        radius,
                        math.radians(start_octant * 45),
                        math.radians(octant_span * 45),
                        ccw,
                    )
            elif code == 0xB:  # fractional arc
                start_offset = codes[index]
                span_offset = codes[index + 1]
                radius = codes[index + 2] << 8 + codes[index + 3]
                start_octant, octant_span, ccw = decode_octant_specs(
                    codes[index + 4]
                )
                index += 5
                start_angle = start_octant * 45 + (start_offset * 45 / 256)
                span_angle = octant_span * 45 + (span_offset * 45 / 256)
                if not skip_next:
                    self.draw_arc_span(
                        radius,
                        math.radians(start_angle),
                        math.radians(span_angle),
                        ccw,
                    )
            elif code == 0xC:  # bulge arc
                x = codes[index]
                y = codes[index + 1]
                bulge = codes[index + 2]
                index += 3
                if not skip_next:
                    self.draw_bulge(x, y, bulge)
            elif code == 0xD:  # multiple bulge arcs
                while True:
                    x = codes[index]
                    y = codes[index + 1]
                    if x == 0 and y == 0:
                        index += 2
                        break
                    bulge = codes[index + 2]
                    index += 3
                    if not skip_next:
                        self.draw_bulge(x, y, bulge)
            elif code == 0xE:  # flag vertical text
                if not self.stacked:
                    skip_next = True
                    continue
            skip_next = False

    def draw_vector(self, code: int) -> None:
        angle: int = code & 0xF
        length: int = (code >> 4) & 0xF
        self.draw_displacement(VEC_X[angle] * length, VEC_Y[angle] * length)

    def draw_displacement(self, x: float, y: float):
        vector_length = self.vector_length
        x *= vector_length
        y *= vector_length
        target = self.current_location + Vec2(x, y)
        if self.pen:
            self.p.line_to(target)
        else:
            self.p.move_to(target)

    def draw_arc_span(
        self, radius: float, start_param: float, span: float, ccw: bool
    ):
        end_param = start_param + (span if ccw else -span)
        arc = ConstructionEllipse(
            major_axis=(radius * self.vector_length, 0),
            start_param=start_param,
            end_param=end_param,
            ccw=ccw,
        )
        # move arc start-point to the end-point of current path
        arc.center += self.current_location - (
            arc.start_point if ccw else arc.end_point
        )
        if self.pen:
            path.add_ellipse(self.p, arc, reset=False)
        else:
            self.p.move_to(arc.end_point)

    def draw_arc(
        self,
        center: Vec2,
        radius: float,
        start_param: float,
        end_param: float,
        ccw: bool,
    ):
        arc = ConstructionEllipse(
            center=center,
            major_axis=(radius * self.vector_length, 0),
            start_param=start_param,
            end_param=end_param,
            ccw=ccw,
        )
        if self.pen:
            path.add_ellipse(self.p, arc, reset=False)
        else:
            self.p.move_to(arc.end_point)

    def draw_bulge(self, x: float, y: float, bulge: float):
        if self.pen and bulge:
            start_point = self.current_location
            x *= self.vector_length
            y *= self.vector_length
            ccw = bulge > 0
            end_point = start_point + (x, y)
            bulge = abs(bulge) / 127.0
            if ccw:  # counter-clockwise
                center, start_angle, end_angle, radius = bulge_to_arc(
                    start_point, end_point, bulge
                )
            else:  # clockwise
                center, start_angle, end_angle, radius = bulge_to_arc(
                    end_point, start_point, bulge
                )
            self.draw_arc(center, radius, start_angle, end_angle, ccw=True)
        else:
            self.draw_displacement(x, y)


def decode_octant_specs(specs: int) -> Tuple[int, int, bool]:
    ccw = True
    if specs < 0:
        ccw = False
        specs = -specs
    start_octant = (specs >> 4) & 0xF
    octant_span = specs & 0xF
    return start_octant, octant_span, ccw
