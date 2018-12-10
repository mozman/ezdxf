#!/usr/bin/env python
# coding:utf-8
# Purpose: read, create and write acad ctb files
# Created: 23.03.2010 for dxfwrite, added to ezdxf package on 2016-03-06
# Copyright (C) 2010, Manfred Moitzi
# License: MIT License
# IMPORTANT: use only standard 7-Bit ascii code
from typing import Union, Tuple, Optional, BinaryIO, TextIO, Iterable, List, Any
from io import StringIO
from array import array
from struct import pack
import zlib

ENDSTYLE_BUTT = 0
ENDSTYLE_SQUARE = 1
ENDSTYLE_ROUND = 2
ENDSTYLE_DIAMOND = 3
ENDSTYLE_OBJECT = 4

JOINSTYLE_MITER = 0
JOINSTYLE_BEVEL = 1
JOINSTYLE_ROUND = 2
JOINSTYLE_DIAMOND = 3
JOINSTYLE_OBJECT = 5

FILL_STYLE_SOLID = 64
FILL_STYLE_CHECKERBOARD = 65
FILL_STYLE_CROSSHATCH = 66
FILL_STYLE_DIAMONDS = 67
FILL_STYLE_HORIZONTAL_BARS = 68
FILL_STYLE_SLANT_LEFT = 69
FILL_STYLE_SLANT_RIGHT = 70
FILL_STYLE_SQUARE_DOTS = 71
FILL_STYLE_VERICAL_BARS = 72
FILL_STYLE_OBJECT = 73

DITHERING_ON = 1  # bit coded color_policy
GRAYSCALE_ON = 2  # bit coded color_policy

AUTOMATIC = 0
OBJECT_LINEWEIGHT = 0
OBJECT_LINETYPE = 31
OBJECT_COLOR = -1
OBJECT_COLOR2 = -1006632961

STYLE_COUNT = 255

DEFAULT_LINE_WEIGHTS = [
    0.00,  # 0
    0.05,  # 1
    0.09,  # 2
    0.10,  # 3
    0.13,  # 4
    0.15,  # 5
    0.18,  # 6
    0.20,  # 7
    0.25,  # 8
    0.30,  # 9
    0.35,  # 10
    0.40,  # 11
    0.45,  # 12
    0.50,  # 13
    0.53,  # 14
    0.60,  # 15
    0.65,  # 16
    0.70,  # 17
    0.80,  # 18
    0.90,  # 19
    1.00,  # 20
    1.06,  # 21
    1.20,  # 22
    1.40,  # 23
    1.58,  # 24
    2.00,  # 25
    2.11,  # 26
]


def color_name(index: int) -> str:
    return 'Color_%d' % (index + 1)


def get_bool(value: Union[str, bool]) -> bool:
    if isinstance(value, str):
        upperstr = value.upper()
        if upperstr == 'TRUE':
            value = True
        elif upperstr == 'FALSE':
            value = False
        else:
            raise ValueError("Unknown bool value '%s'." % str(value))
    return value


class UserStyle:
    def __init__(self, index: int, data: dict = None, parent: 'UserStyles' = None):
        data = data or {}
        self.parent = parent
        self.index = int(index)
        self.description = str(data.get('description', ""))
        # do not set _color, _mode_color or _color_policy directly
        # use set_color() method, and the properties dithering and grayscale
        self._color = int(data.get('color', OBJECT_COLOR))
        if self._color != OBJECT_COLOR:
            self._mode_color = int(data.get('mode_color', self._color))
        self._color_policy = int(data.get('color_policy', DITHERING_ON))
        self.physical_pen_number = int(data.get('physical_pen_number', AUTOMATIC))
        self.virtual_pen_number = int(data.get('virtual_pen_number', AUTOMATIC))
        self.screen = int(data.get('screen', 100))
        self.linepattern_size = float(data.get('linepattern_size', 0.5))
        self.linetype = int(data.get('linetype', OBJECT_LINETYPE))  # 0 .. 30
        self.adaptive_linetype = get_bool(data.get('adaptive_linetype', True))
        self.lineweight = int(data.get('lineweight', OBJECT_LINEWEIGHT))
        self.end_style = int(data.get('end_style', ENDSTYLE_OBJECT))
        self.join_style = int(data.get('join_style', JOINSTYLE_OBJECT))
        self.fill_style = int(data.get('fill_style', FILL_STYLE_OBJECT))

    def set_color(self, red: int, green: int, blue: int) -> None:
        """
        Set color as rgb-tuple.

        """
        self._mode_color = mode_color2int(red, green, blue)
        # when defining a user-color, <mode_color> represents the real truecolor
        # as rgb-tuple with the magic number 0xC2 as highest byte, the <color>
        # value calculated for a user-color is not a rgb-tuple and has the magic
        # number 0xC3 (sometimes), I set for <color> the same value a for
        # <mode_color>, because Autocad corrects the <color> value by itself.
        self._color = self._mode_color

    def set_object_color(self) -> None:
        """
        Set color to object color.

        """
        self._color = OBJECT_COLOR
        self._mode_color = OBJECT_COLOR

    def set_lineweight(self, lineweight: float) -> None:
        """Set lineweight. Use 0.0 to set lineweight by object.

        lineweight in mm! not the lineweight index

        """
        self.lineweight = self.parent.get_lineweight_index(lineweight)

    def get_lineweight(self) -> float:
        """
        Returns the lineweight in millimeters.

        :returns: lineweight in mm or 0.0 for use entity lineweight

        """
        return self.parent.lineweights[self.lineweight]

    def has_object_color(self) -> bool:
        """
        True if style has object color.

        """
        return self._color == OBJECT_COLOR or \
               self._color == OBJECT_COLOR2

    def get_color(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Get style color as rgb-tuple or None if style has object color.

        """
        if self.has_object_color():
            return None  # object color
        else:
            return int2color(self._mode_color)[:3]

    def get_dxf_color_index(self) -> int:
        return self.index + 1

    def get_dithering(self) -> bool:
        return bool(self._color_policy & DITHERING_ON)

    def set_dithering(self, status: bool) -> None:
        if status:
            self._color_policy |= DITHERING_ON
        else:
            self._color_policy &= ~DITHERING_ON

    dithering = property(get_dithering, set_dithering)

    def get_grayscale(self) -> bool:
        return bool(self._color_policy & GRAYSCALE_ON)

    def set_grayscale(self, status: bool) -> None:
        if status:
            self._color_policy |= GRAYSCALE_ON
        else:
            self._color_policy &= ~GRAYSCALE_ON

    grayscale = property(get_grayscale, set_grayscale)

    def write(self, stream: TextIO) -> None:
        """
        Write style data to file-like object <stream>.

        """
        index = self.index
        stream.write(' %d{\n' % index)
        stream.write('  name="%s\n' % color_name(index))
        stream.write('  localized_name="%s\n' % color_name(index))
        stream.write('  description="%s\n' % self.description)
        stream.write('  color=%d\n' % self._color)
        if self._color != OBJECT_COLOR:
            stream.write('  mode_color=%d\n' % self._mode_color)
        stream.write('  color_policy=%d\n' % self._color_policy)
        stream.write('  physical_pen_number=%d\n' % self.physical_pen_number)
        stream.write('  virtual_pen_number=%d\n' % self.virtual_pen_number)
        stream.write('  screen=%d\n' % self.screen)
        stream.write('  linepattern_size=%s\n' % str(self.linepattern_size))
        stream.write('  linetype=%d\n' % self.linetype)
        stream.write('  adaptive_linetype=%s\n' % str(bool(self.adaptive_linetype)).upper())
        stream.write('  lineweight=%s\n' % str(self.lineweight))
        stream.write('  fill_style=%d\n' % self.fill_style)
        stream.write('  end_style=%d\n' % self.end_style)
        stream.write('  join_style=%d\n' % self.join_style)
        stream.write(' }\n')


class UserStyles:
    """
    UserStyle container

    """

    def __init__(self, description: str = "", scale_factor: float = 1.0, apply_factor: bool = False):
        self.description = description
        self.scale_factor = scale_factor
        self.apply_factor = apply_factor

        # set custom_line... to 1 for showing lineweights in inch in the Autocad
        # ctb editor window, but lineweights are always defined in mm
        self.custom_lineweight_display_units = 0
        self.styles = [None] * (STYLE_COUNT + 1)  # type: List[UserStyle]
        self.lineweights = array('f', DEFAULT_LINE_WEIGHTS)
        self.set_default_styles()

    def set_default_styles(self) -> None:
        for index in range(STYLE_COUNT):
            self._set_style(UserStyle(index))

    @staticmethod
    def check_color_index(dxf_color_index: int) -> int:
        if 0 < dxf_color_index < 256:
            return dxf_color_index
        raise IndexError('color index has to be in the range [1 .. 255].')

    def iter_styles(self) -> Iterable[UserStyle]:
        return (style for style in self.styles[1:])

    def _set_style(self, style: UserStyle) -> None:
        style.parent = self
        self.styles[style.get_dxf_color_index()] = style

    def set_style(self, dxf_color_index: int, data: dict = None) -> UserStyle:
        """
        Set <dxf_color_index> to new attributes defined in init_dict.

        """
        dxf_color_index = self.check_color_index(dxf_color_index)
        # ctb table index is dxf_color_index - 1
        # ctb table starts with index 0, where dxf_color_index=0 means BYBLOCK
        style = UserStyle(dxf_color_index - 1, data)
        self._set_style(style)
        return style

    def get_style(self, dxf_color_index: int) -> UserStyle:
        """
        Get style for <dxf_color_index>.

        """
        dxf_color_index = self.check_color_index(dxf_color_index)
        return self.styles[dxf_color_index]

    def get_color(self, dxf_color_index: int) -> Optional[Tuple[int, int, int, int]]:
        """
        Get rgb-color-tuple for <dxf_color_index> or None if not specified.

        """
        style = self.get_style(dxf_color_index)
        return style.get_color()

    def get_lineweight(self, dxf_color_index: int):
        """
        Returns the assigned lineweight for <dxf_color_index> in mm.

        """
        style = self.get_style(dxf_color_index)
        lineweight = style.get_lineweight()
        if lineweight == 0.0:
            return None
        else:
            return lineweight

    def get_lineweight_index(self, lineweight: float) -> int:
        """
        Get index of lineweight in the lineweight table or append lineweight to lineweight table.

        """
        try:
            return self.lineweights.index(lineweight)
        except ValueError:
            self.lineweights.append(lineweight)
            return len(self.lineweights) - 1

    def set_table_lineweight(self, index: int, weight: float) -> int:
        """
        Index is the lineweight table index, not the dxf color index.

        :param int index: lineweight table index = UserStyle.lineweight
        :param float weight: in millimeters

        """
        try:
            self.lineweights[index] = weight
            return index
        except IndexError:
            self.lineweights.append(weight)
            return len(self.lineweights) - 1

    def get_table_lineweight(self, index: int) -> float:
        """
        Returns lineweight in millimeters.

        :param int index: lineweight table index = UserStyle.lineweight
        :returns: lineweight in mm or 0.0 for use entity lineweight

        """
        return self.lineweights[index]

    def save(self, filename: str) -> None:
        """
        Save ctb-file to <filename>.

        """
        with open(filename, 'wb') as stream:
            self.write(stream)

    def write(self, stream: BinaryIO):
        """
        Create and compress the ctb-file to <stream>.

        """
        memfile = StringIO()
        self.write_content(memfile)
        memfile.write(chr(0))  # end of file
        body = memfile.getvalue()
        memfile.close()
        self._compress(stream, body)

    def write_content(self, stream: TextIO) -> None:
        """
        Write the ctb-file to <fileobj>.

        """
        self._write_header(stream)
        self._write_aci_table(stream)
        self._write_ctb_plot_styles(stream)
        self._write_lineweights(stream)

    def _write_header(self, stream: TextIO) -> None:
        """
        Write header values of ctb-file to <stream>.

        """
        stream.write('description="%s\n' % self.description)
        stream.write('aci_table_available=TRUE\n')
        stream.write('scale_factor=%.1f\n' % self.scale_factor)
        stream.write('apply_factor=%s\n' % str(self.apply_factor).upper())
        stream.write('custom_lineweight_display_units=%s\n' % str(
            self.custom_lineweight_display_units))

    def _write_aci_table(self, stream: TextIO) -> None:
        """
        Write autocad color index table to ctb-file <stream>.

        """
        stream.write('aci_table{\n')
        for style in self.iter_styles():
            index = style.index
            stream.write(' %d="%s\n' % (index, color_name(index)))
        stream.write('}\n')

    def _write_ctb_plot_styles(self, stream: TextIO) -> None:
        """
        Write user styles to ctb-file <stream>.

        """
        stream.write('plot_style{\n')
        for style in self.iter_styles():
            style.write(stream)
        stream.write('}\n')

    def _write_lineweights(self, stream: TextIO) -> None:
        """
        Write custom lineweights table to ctb-file <stream>.

        """
        stream.write('custom_lineweight_table{\n')
        for index, weight in enumerate(self.lineweights):
            stream.write(' %d=%.2f\n' % (index, weight))
        stream.write('}\n')

    def parse(self, text: str) -> None:
        """
        Parse and get values of plot styles from <text>.

        """

        def set_lineweights(lineweights):
            if lineweights is None:
                return
            self.lineweights = array('f', [0.0] * len(lineweights))
            for key, value in lineweights.items():
                self.lineweights[int(key)] = float(value)

        def set_styles(styles):
            for index, style in styles.items():
                style = UserStyle(index, style)
                self._set_style(style)

        parser = CtbParser(text)
        self.description = parser.get('description', "")
        self.scale_factor = float(parser.get('scale_factor', 1.0))
        self.apply_factor = get_bool(parser.get('apply_factor', True))
        self.custom_lineweight_display_units = int(
            parser.get('custom_lineweight_display_units', 0))
        set_lineweights(parser.get('custom_lineweight_table', None))
        set_styles(parser.get('plot_style', {}))

    def _compress(self, stream: BinaryIO, body: str):
        """
        Compress ctb-file-body and write it to <stream>.

        """

        def writestr(s):
            stream.write(s.encode())

        body = body.encode()
        comp_body = zlib.compress(body)
        adler_chksum = zlib.adler32(comp_body)
        writestr('PIAFILEVERSION_2.0,CTBVER1,compress\r\npmzlibcodec')
        stream.write(pack('LLL', adler_chksum, len(body), len(comp_body)))
        stream.write(comp_body)


def read(stream: BinaryIO) -> UserStyles:
    """
    Read a ctb-file from the file-like object <stream>.

    """
    content = _decompress(stream)
    content = content.decode()
    styles = UserStyles()
    styles.parse(content)
    return styles


def load(filename: str) -> UserStyles:
    """
    Load the ctb-file <filename>.

    """
    with open(filename, 'rb') as stream:
        ctbfile = read(stream)
    return ctbfile


def _decompress(stream: BinaryIO) -> bytes:
    """
    Read and decompress the file content of the file-like object <stream>.

    """
    content = stream.read()
    data = zlib.decompress(content[60:])  # type: bytes
    return data[:-1]  # truncate trailing \nul


class CtbParser:
    """
    A very simple ctb-file parser. Ctb-files are created by programs, so the file structure should be correct
    in the most cases.

    """

    def __init__(self, text: str):
        """
        :param str text: ctb content as string

        """
        self.data = {}
        for element, value in CtbParser.iteritems(text):
            self.data[element] = value

    @staticmethod
    def iteritems(text: str):
        """
        iterate over all first level (start at col 0) elements

        """

        def get_name() -> str:
            """
            Get element name of line <line_index>.

            """
            line = lines[line_index]
            if line.endswith('{'):  # start of a list like 'plot_style{'
                name = line[:-1]
            else:  # simple name=value line
                name = line.split('=', 1)[0]
            return name.strip()

        def get_mapping() -> dict:
            """
            Get mapping of elements enclosed by { }.

            e. g. lineweigths, plot_styles, aci_table

            """
            nonlocal line_index

            def end_of_list():
                return lines[line_index].endswith('}')

            data = dict()
            while not end_of_list():
                name = get_name()
                value = get_value()  # get value or sub-list
                data[name] = value
            line_index += 1
            return data  # skip '}' - end of list

        def get_value() -> Union[str, dict]:
            """
            Get value of line <line_index> or the list that starts in line <line_index>.

            """
            nonlocal line_index
            line = lines[line_index]
            if line.endswith('{'):  # start of a list
                line_index += 1
                value = get_mapping()
            else:  # it's a simple name=value line
                value = line.split('=', 1)[1]  # type: str
                value = value.lstrip('"')  # strings look like this: name="value
                line_index += 1
            return value

        def skip_empty_lines():
            nonlocal line_index
            while line_index < len(lines) and len(lines[line_index]) == 0:
                line_index += 1

        lines = text.split('\n')
        line_index = 0
        while line_index < len(lines):
            name = get_name()
            value = get_value()
            yield (name, value)
            skip_empty_lines()

    def get(self, name: str, default: Any) -> Any:
        return self.data.get(name, default)


# color_type: (thx to Rammi)
# Take color from layer, ignore other bytes.
COLOR_BY_LAYER = 0xc0
# Take color from insertion, ignore other bytes
COLOR_BY_BLOCK = 0xc1
# RGB value, other bytes are R,G,B.
COLOR_RGB = 0xc2
# ACI, AutoCAD color index, other bytes are 0,0,index
COLOR_ACI = 0xc3


def int2color(color: int) -> Tuple[int, int, int, int]:
    """
    Convert color integer value from ctb-file to rgb-tuple plus a magic number.

    """
    # Take color from layer, ignore other bytes.
    color_type = (color & 0xff000000) >> 24
    red = (color & 0xff0000) >> 16
    green = (color & 0xff00) >> 8
    blue = color & 0xff
    return red, green, blue, color_type


def mode_color2int(red: int, green: int, blue: int, color_type=COLOR_RGB) -> int:
    """
    Convert rgb-tuple to an int value.

    """
    return -color2int(red, green, blue, color_type)


def color2int(red: int, green: int, blue: int, color_type: int) -> int:
    """
    Convert rgb-tuple to an int value.

    """
    return -((color_type << 24) + (red << 16) + (green << 8) + blue) & 0xffffffff
