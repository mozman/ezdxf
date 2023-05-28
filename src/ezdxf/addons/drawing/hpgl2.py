#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable, Sequence, no_type_check

import copy
import itertools

from ezdxf import colors
from ezdxf.math import AnyVec
from ezdxf.path import Path, Path2d, Command

from .type_hints import Color
from .backend import BackendInterface
from .config import Configuration, LineweightPolicy
from .properties import BackendProperties
from . import layout, recorder


__all__ = ["PlotterBackend"]

SEMICOLON = ord(";")
PRELUDE = b"%0B;IN;BP;"
EPILOG = b"PU;PA0,0;"
FLATTEN_MAX = 10  # plot units
MM_TO_PLU = 40  # 40 plu = 1mm
DEFAULT_PEN = 0
WHITE = colors.RGB(255, 255, 255)
BLACK = colors.RGB(0, 0, 0)


class PlotterBackend(recorder.Recorder):
    def __init__(self) -> None:
        super().__init__()

    def get_bytes(
        self,
        page: layout.Page,
        settings: layout.Settings = layout.Settings(),
    ) -> bytes:
        """Returns the HPGL/2 data as bytes.

        Args:
            page: page definition
            settings: layout settings
        """
        settings = copy.copy(settings)
        # This player changes the original recordings!
        player = self.player()

        output_layout = layout.Layout(player.bbox(), flip_y=False)
        page = output_layout.get_final_page(page, settings)
        # The DXF coordinates are mapped to integer coordinates (plu) in the first
        # quadrant: 40 plu = 1mm
        settings.output_coordinate_space = (
            max(page.width_in_mm, page.height_in_mm) * MM_TO_PLU
        )
        m = output_layout.get_placement_matrix(page, settings)
        player.transform(m)
        backend = _RenderBackend(page, settings)
        player.replay(backend)
        return backend.get_bytes()


class PenTable:
    def __init__(self, max_pens: int = 64) -> None:
        self.pens: dict[int, colors.RGB] = dict()
        self.max_pens = int(max_pens)

    def __contains__(self, index: int) -> bool:
        return index in self.pens

    def __getitem__(self, index: int) -> colors.RGB:
        return self.pens[index]

    def add_pen(self, index: int, color: colors.RGB):
        self.pens[index] = color

    def to_bytes(self) -> bytes:
        command: list[bytes] = [f"NP{self.max_pens-1};".encode()]
        pens: list[tuple[int, colors.RGB]] = [
            (index, rgb) for index, rgb in self.pens.items()
        ]
        pens.sort()
        for index, rgb in pens:
            command.append(make_pc(index, rgb))
        return b"".join(command)


def make_pc(pen: int, rgb: colors.RGB) -> bytes:
    # pen color
    return f"PC{pen},{rgb.r},{rgb.g},{rgb.b};".encode()


class _RenderBackend(BackendInterface):
    """Creates the HPGL/2 output.

    This backend requires some preliminary work, record the frontend output via the
    Recorder backend to accomplish the following requirements:

    - Move content in the first quadrant of the coordinate system.
    - The output coordinates are integer values, scale the content appropriately:
        - 1 plot unit (plu) = 0.025mm
        - 40 plu = 1mm
        - 1016 plu = 1 inch
        - 3.39 plu = 1 dot @300 dpi
    - Replay the recorded output on this backend.

    """

    def __init__(
        self, page: layout.Page, settings: layout.Settings, decimal_places: int = 2
    ) -> None:
        self.settings = settings
        self.decimal_places = decimal_places
        self.header: list[bytes] = []
        self.data: list[bytes] = []
        self.pen_table = PenTable(max_pens=256)
        self.current_pen: int = 0
        self.current_pen_width: float = 0.0
        self.setup(page)

        self._stroke_width_cache: dict[float, float] = dict()
        # StrokeWidthPolicy.absolute:
        # pen width in mm as resolved by the frontend
        self.min_lineweight = 0.05  # in mm, set by configure()
        self.lineweight_scaling = 1.0  # set by configure()
        self.lineweight_policy = LineweightPolicy.ABSOLUTE  # set by configure()
        # fixed lineweight for all strokes in ABSOLUTE mode:
        # set Configuration.min_lineweight to the desired lineweight in 1/300 inch!
        # set Configuration.lineweight_scaling to 0

        # LineweightPolicy.RELATIVE:
        # max_stroke_width is determined as a certain percentage of max(width, height)
        max_size = max(page.width_in_mm, page.height_in_mm)
        self.max_stroke_width: float = round(max_size * settings.max_stroke_width, 2)
        # min_stroke_width is determined as a certain percentage of max_stroke_width
        self.min_stroke_width: float = round(
            self.max_stroke_width * settings.min_stroke_width, 2
        )
        # LineweightPolicy.RELATIVE_FIXED:
        # all strokes have a fixed stroke-width as a certain percentage of max_stroke_width
        self.fixed_stroke_width: float = round(
            self.max_stroke_width * settings.fixed_stroke_width, 2
        )

    def setup(self, page: layout.Page) -> None:
        cmd = f"PS{page.width_in_mm*MM_TO_PLU:.0f},{page.height_in_mm*MM_TO_PLU:.0f};"
        self.header.append(cmd.encode())
        self.header.append(b"FT1;PA;")  # solid fill; plot absolute;

    def get_bytes(self) -> bytes:
        header: list[bytes] = list(self.header)
        header.append(self.pen_table.to_bytes())
        return compile_hpgl2(header, self.data)

    def switch_current_pen(self, pen_number: int, rgb: colors.RGB) -> int:
        if pen_number in self.pen_table:
            pen_color = self.pen_table[pen_number]
            if rgb != pen_color:
                self.data.append(make_pc(DEFAULT_PEN, rgb))
                pen_number = DEFAULT_PEN
        else:
            self.pen_table.add_pen(pen_number, rgb)
        return pen_number

    def set_pen(self, pen_number: int) -> None:
        if self.current_pen == pen_number:
            return
        self.data.append(f"SP{pen_number};".encode())
        self.current_pen = pen_number

    def set_pen_width(self, width: float) -> None:
        if self.current_pen_width == width:
            return
        self.data.append(f"PW{width:g};".encode())  # pen width in mm
        self.current_pen_width = width

    def enter_polygon_mode(self, start_point: AnyVec) -> None:
        self.data.append(f"PA;PU{start_point.x},{start_point.y};PM;".encode())

    def close_current_polygon(self) -> None:
        self.data.append(b"PM1;")

    def fill_polygon(self) -> None:
        self.data.append(b"PM2;FP;")  # even/odd fill method

    def set_properties(self, properties: BackendProperties) -> None:
        pen_number = properties.pen
        pen_color, opacity = self.resolve_pen_color(properties.color)
        pen_width = self.resolve_pen_width(properties.lineweight)
        pen_number = self.switch_current_pen(pen_number, pen_color)
        self.set_pen(pen_number)
        self.set_pen_width(pen_width)

    def add_polyline_encoded(
        self, vertices: Iterable[AnyVec], properties: BackendProperties
    ):
        self.set_properties(properties)
        self.data.append(polyline_encode(vertices))

    def add_path(self, path: Path | Path2d, properties: BackendProperties):
        self.set_properties(properties)
        self.data.append(path_ascii(path, decimal_places=self.decimal_places))

    @staticmethod
    def resolve_pen_color(color: Color) -> tuple[colors.RGB, float]:
        rgb = colors.RGB.from_hex(color)
        if rgb == WHITE:
            rgb = BLACK
        return rgb, alpha_to_opacity(color[7:9])

    def resolve_pen_width(self, width: float) -> float:
        try:
            return self._stroke_width_cache[width]
        except KeyError:
            pass
            stroke_width = self.fixed_stroke_width
        policy = self.lineweight_policy
        if policy == LineweightPolicy.ABSOLUTE:
            if self.lineweight_scaling:
                width = max(self.min_lineweight, width) * self.lineweight_scaling
            else:
                width = self.min_lineweight
            stroke_width = round(width, 2)  # in mm
        elif policy == LineweightPolicy.RELATIVE:
            stroke_width = round(
                map_lineweight_to_stroke_width(
                    width, self.min_stroke_width, self.max_stroke_width
                ),
                2,
            )
        self._stroke_width_cache[width] = stroke_width
        return stroke_width

    def set_background(self, color: Color) -> None:
        # background is always a white paper
        pass

    def draw_point(self, pos: AnyVec, properties: BackendProperties) -> None:
        self.add_polyline_encoded([pos], properties)

    def draw_line(
        self, start: AnyVec, end: AnyVec, properties: BackendProperties
    ) -> None:
        self.add_polyline_encoded([start, end], properties)

    def draw_solid_lines(
        self, lines: Iterable[tuple[AnyVec, AnyVec]], properties: BackendProperties
    ) -> None:
        lines = list(lines)
        if len(lines) == 0:
            return
        for line in lines:
            self.add_polyline_encoded(line, properties)

    def draw_path(self, path: Path | Path2d, properties: BackendProperties) -> None:
        for sub_path in path.sub_paths():
            if len(sub_path) == 0:
                continue
            self.add_path(sub_path, properties)

    def draw_filled_paths(
        self,
        paths: Iterable[Path | Path2d],
        holes: Iterable[Path | Path2d],
        properties: BackendProperties,
    ) -> None:
        all_paths = list(itertools.chain(paths, holes))
        if len(all_paths) == 0:
            return
        self.enter_polygon_mode(all_paths[0].start)
        for p in all_paths:
            for sub_path in p.sub_paths():
                if len(sub_path) == 0:
                    continue
                self.add_path(sub_path, properties)
                self.close_current_polygon()
        self.fill_polygon()

    def draw_filled_polygon(
        self, points: Iterable[AnyVec], properties: BackendProperties
    ) -> None:
        points = list(points)
        if points:
            self.enter_polygon_mode(points[0])
            self.add_polyline_encoded(points, properties)
            self.fill_polygon()

    def configure(self, config: Configuration) -> None:
        self.lineweight_policy = config.lineweight_policy
        if config.min_lineweight:
            # config.min_lineweight in 1/300 inch!
            min_lineweight_mm = config.min_lineweight * 25.4 / 300
            self.min_lineweight = max(0.05, min_lineweight_mm)
        self.lineweight_scaling = config.lineweight_scaling

    def clear(self) -> None:
        pass

    def finalize(self) -> None:
        pass

    def enter_entity(self, entity, properties) -> None:
        pass

    def exit_entity(self, entity) -> None:
        pass


def alpha_to_opacity(alpha: str) -> float:
    # stroke-opacity: 0.0 = transparent; 1.0 = opaque
    # alpha: "00" = transparent; "ff" = opaque
    if len(alpha):
        try:
            return int(alpha, 16) / 255
        except ValueError:
            pass
    return 1.0


def map_lineweight_to_stroke_width(
    lineweight: float,
    min_stroke_width: float,
    max_stroke_width: float,
    min_lineweight=0.05,  # defined by DXF
    max_lineweight=2.11,  # defined by DXF
) -> float:
    lineweight = max(min(lineweight, max_lineweight), min_lineweight) - min_lineweight
    factor = (max_stroke_width - min_stroke_width) / (max_lineweight - min_lineweight)
    return round(min_stroke_width + round(lineweight * factor), 2)


def flatten_path(path: Path | Path2d) -> Sequence[AnyVec]:
    points = list(path.flattening(distance=FLATTEN_MAX))
    return points


def compile_hpgl2(header: Sequence[bytes], commands: Sequence[bytes]) -> bytes:
    output = bytearray(PRELUDE)
    output.extend(b"".join(header))
    output.extend(b"".join(commands))
    output.extend(EPILOG)
    return bytes(output)


def encode_number(value: float, decimal_places: int = 0, base: int = 64) -> bytes:
    if decimal_places:
        n = round(decimal_places * 3.33)
        value *= 2 << n
        x = round(value)
    else:
        x = round(value)
    if x >= 0:
        x *= 2
    else:
        x = abs(x) * 2 + 1

    chars = bytearray()
    while x >= base:
        x, r = divmod(x, base)
        chars.append(63 + r)
    if base == 64:
        chars.append(191 + x)
    else:
        chars.append(95 + x)
    return bytes(chars)


def polyline_encode(vertices: Iterable[AnyVec]) -> bytes:
    data = [b"PE7<="]
    vertices = list(vertices)
    # first point as absolute coordinates
    current = vertices[0]
    data.append(encode_number(current.x, base=32))
    data.append(encode_number(current.y, base=32))
    for vertex in vertices[1:]:
        # remaining points as relative coordinates
        delta = vertex - current
        data.append(encode_number(delta.x, base=32))
        data.append(encode_number(delta.y, base=32))
        current = vertex
    data.append(b";")
    return b"".join(data)


@no_type_check
def path_ascii(path: Path2d, decimal_places=2) -> bytes:
    data = [b"PU;"]
    # first point as absolute coordinates
    current = path.start
    x = round(current.x, decimal_places)
    y = round(current.y, decimal_places)
    data.append(f"PA{x:g},{y:g};PD;".encode())
    if len(path):
        commands: list[bytes] = []
        for cmd in path.commands():
            delta = cmd.end - current
            xe = round(delta.x, decimal_places)
            ye = round(delta.y, decimal_places)
            if cmd.type == Command.LINE_TO:
                commands.append(f"PR{xe:g},{ye:g};".encode())
            else:
                if cmd.type == Command.CURVE3_TO:
                    control = cmd.ctrl - current
                    end = cmd.end - current
                    control_1 = 2.0 * control / 3.0
                    control_2 = end + 2.0 * (control - end) / 3.0
                elif cmd.type == Command.CURVE4_TO:
                    control_1 = cmd.ctrl1 - current
                    control_2 = cmd.ctrl2 - current
                else:
                    raise ValueError("internal error: MOVE_TO command is illegal here")
                x1 = round(control_1.x, decimal_places)
                y1 = round(control_1.y, decimal_places)
                x2 = round(control_2.x, decimal_places)
                y2 = round(control_2.y, decimal_places)
                commands.append(
                    f"BR{x1:g},{y1:g},{x2:g},{y2:g},{xe:g},{ye:g};".encode()
                )
            current = cmd.end
        data.append(b"".join(commands))
    data.append(b"PU;")
    return b"".join(data)
