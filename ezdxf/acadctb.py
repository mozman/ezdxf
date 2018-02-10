#!/usr/bin/env python
# coding:utf-8
# Purpose: read, create and write acad ctb files
# Created: 23.03.2010 for dxfwrite, added to ezdxf package on 2016-03-06
# Copyright (C) 2010, Manfred Moitzi
# License: MIT License

# IMPORTANT: use only standard 7-Bit ascii code

__author__ = "mozman <me@mozman.at>"

import sys

PYTHON3 = sys.version_info[0] > 2
if PYTHON3:
    from io import StringIO

    unicode = str
    basestring = str
else:
    from StringIO import StringIO

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


def color_name(index):
    return 'Color_%d' % (index + 1)


def get_bool(value):
    if isinstance(value, basestring):
        upperstr = value.upper()
        if upperstr == 'TRUE':
            value = True
        elif upperstr == 'FALSE':
            value = False
        else:
            raise ValueError("Unknown bool value '%s'." % str(value))
    return value


class UserStyle(object):
    def __init__(self, index, init_dict=None, parent=None):
        if init_dict is None:
            init_dict = {}
        self.parent = parent
        self.index = int(index)
        self.description = unicode(init_dict.get('description', ""))
        # do not set _color, _mode_color or _color_policy directly
        # use set_color() method, and the properties dithering and grayscale
        self._color = int(init_dict.get('color', OBJECT_COLOR))
        if self._color != OBJECT_COLOR:
            self._mode_color = int(init_dict.get('mode_color', self._color))
        self._color_policy = int(init_dict.get('color_policy', DITHERING_ON))
        self.physical_pen_number = int(init_dict.get('physical_pen_number', AUTOMATIC))
        self.virtual_pen_number = int(init_dict.get('virtual_pen_number', AUTOMATIC))
        self.screen = int(init_dict.get('screen', 100))
        self.linepattern_size = float(init_dict.get('linepattern_size', 0.5))
        self.linetype = int(init_dict.get('linetype', OBJECT_LINETYPE))  # 0 .. 30
        self.adaptive_linetype = get_bool(init_dict.get('adaptive_linetype', True))
        self.lineweight = int(init_dict.get('lineweight', OBJECT_LINEWEIGHT))
        self.end_style = int(init_dict.get('end_style', ENDSTYLE_OBJECT))
        self.join_style = int(init_dict.get('join_style', JOINSTYLE_OBJECT))
        self.fill_style = int(init_dict.get('fill_style', FILL_STYLE_OBJECT))

    def set_color(self, red, green, blue):
        """Set color as rgb-tuple."""
        self._mode_color = mode_color2int(red, green, blue)
        # when defining a user-color, <mode_color> represents the real truecolor
        # as rgb-tuple with the magic number 0xC2 as highest byte, the <color>
        # value calculated for a user-color is not a rgb-tuple and has the magic
        # number 0xC3 (sometimes), I set for <color> the same value a for
        # <mode_color>, because Autocad corrects the <color> value by itself.
        self._color = self._mode_color

    def set_object_color(self):
        """Set color to object color."""
        self._color = OBJECT_COLOR
        self._mode_color = OBJECT_COLOR

    def set_lineweight(self, lineweight):
        """Set lightweight. Use 0.0 to set lightweight by object.

        lightweight in mm! not the lightweight index
        """
        self.lineweight = self.parent.get_lineweight_index(lineweight)

    def get_lineweight(self):
        """Returns the lightweight in millimeters.

        returns 0.0 for: use object lineweight
        """
        return self.parent.lineweights[self.lineweight]

    def has_object_color(self):
        """True if style has object color."""
        return self._color == OBJECT_COLOR or \
               self._color == OBJECT_COLOR2

    def get_color(self):
        """Get style color as rgb-tuple or None if style has object color."""
        if self.has_object_color():
            return None  # object color
        else:
            return int2color(self._mode_color)[:3]

    def get_dxf_color_index(self):
        return self.index + 1

    def get_dithering(self):
        return bool(self._color_policy & DITHERING_ON)

    def set_dithering(self, status):
        if status:
            self._color_policy |= DITHERING_ON
        else:
            self._color_policy &= ~DITHERING_ON

    dithering = property(get_dithering, set_dithering)

    def get_grayscale(self):
        return bool(self._color_policy & GRAYSCALE_ON)

    def set_grayscale(self, status):
        if status:
            self._color_policy |= GRAYSCALE_ON
        else:
            self._color_policy &= ~GRAYSCALE_ON

    grayscale = property(get_grayscale, set_grayscale)

    def write(self, fileobj):
        """Write style data to file-like object <fileobj>."""
        index = self.index
        fileobj.write(' %d{\n' % index)
        fileobj.write('  name="%s\n' % color_name(index))
        fileobj.write('  localized_name="%s\n' % color_name(index))
        fileobj.write('  description="%s\n' % self.description)
        fileobj.write('  color=%d\n' % self._color)
        if self._color != OBJECT_COLOR:
            fileobj.write('  mode_color=%d\n' % self._mode_color)
        fileobj.write('  color_policy=%d\n' % self._color_policy)
        fileobj.write('  physical_pen_number=%d\n' % self.physical_pen_number)
        fileobj.write('  virtual_pen_number=%d\n' % self.virtual_pen_number)
        fileobj.write('  screen=%d\n' % self.screen)
        fileobj.write('  linepattern_size=%s\n' % str(self.linepattern_size))
        fileobj.write('  linetype=%d\n' % self.linetype)
        fileobj.write('  adaptive_linetype=%s\n' % str(bool(self.adaptive_linetype)).upper())
        fileobj.write('  lineweight=%s\n' % str(self.lineweight))
        fileobj.write('  fill_style=%d\n' % self.fill_style)
        fileobj.write('  end_style=%d\n' % self.end_style)
        fileobj.write('  join_style=%d\n' % self.join_style)
        fileobj.write(' }\n')


class UserStyles(object):
    """UserStyle container"""

    def __init__(self, description="", scale_factor=1.0, apply_factor=False):
        self.description = description
        self.scale_factor = scale_factor
        self.apply_factor = apply_factor

        # set custom_line... to 1 for showing lineweights in inch in the Autocad
        # ctb editor window, but lineweights are always defined in mm
        self.custom_lineweight_display_units = 0
        self.styles = [None] * (STYLE_COUNT + 1)
        self.lineweights = array('f', DEFAULT_LINE_WEIGHTS)
        self.set_default_styles()

    def set_default_styles(self):
        for index in range(STYLE_COUNT):
            self._set_style(UserStyle(index))

    @staticmethod
    def check_color_index(dxf_color_index):
        if 0 < dxf_color_index < 256:
            return dxf_color_index
        raise IndexError('color index has to be in the range [1 .. 255].')

    def iter_styles(self):
        return (style for style in self.styles[1:])

    def _set_style(self, style):
        style.parent = self
        self.styles[style.get_dxf_color_index()] = style

    def set_style(self, dxf_color_index, init_dict=None):
        """Set <dxf_color_index> to new attributes defined in init_dict.
        """
        dxf_color_index = self.check_color_index(dxf_color_index)
        # ctb table index is dxf_color_index - 1
        # ctb table starts with index 0, where dxf_color_index=0 means BYBLOCK
        style = UserStyle(dxf_color_index - 1, init_dict)
        self._set_style(style)
        return style

    def get_style(self, dxf_color_index):
        """Get style for <dxf_color_index>.
        """
        dxf_color_index = self.check_color_index(dxf_color_index)
        return self.styles[dxf_color_index]

    # interface for dxfwrite.std.DXFColorIndex
    def get_color(self, dxf_color_index):
        """Get rgb-color-tuple for <dxf_color_index> or None if not specified.
        """
        style = self.get_style(dxf_color_index)
        return style.get_color()

    # interface for dxfwrite.std.DXFLineweight
    def get_lineweight(self, dxf_color_index):
        """Returns the assigned lineweight for <dxf_color_index> in mm."""
        style = self.get_style(dxf_color_index)
        lineweight = style.get_lineweight()
        if lineweight == 0.0:
            return None
        else:
            return lineweight

    def get_lineweight_index(self, lineweight):
        """Get index of lineweight in the lineweight table or append lineweight
        to lineweight table.
        """
        try:
            return self.lineweights.index(lineweight)
        except ValueError:
            self.lineweights.append(lineweight)
            return len(self.lineweights) - 1

    def set_table_lineweight(self, index, weight):
        """Index is the lineweight table index, not the dxf color index.

        :param int index: lineweight table index = UserStyle.lineweight
        :param float weight: in millimeters
        """
        try:
            self.lineweights[index] = weight
            return index
        except IndexError:
            self.lineweights.append(weight)
            return len(self.lineweights) - 1

    def get_table_lineweight(self, index):
        """Returns lineweight in millimeters.

        returns 0.0 for: use object lineweight

        :param int index: lineweight table index = UserStyle.lineweight
        """
        return self.lineweights[index]

    def save(self, filename):
        """Save ctb-file to <filename>."""
        fileobj = open(filename, 'wb')
        self.write(fileobj)
        fileobj.close()

    def write(self, fileobj):
        """Create and compress the ctb-file to <fileobj>."""
        memfile = StringIO()
        self.write_content(memfile)
        memfile.write(chr(0))  # end of file
        body = memfile.getvalue()
        memfile.close()
        self._compress(fileobj, body)

    def write_content(self, fileobj):
        """Write the ctb-file to <fileobj>."""
        self._write_header(fileobj)
        self._write_aci_table(fileobj)
        self._write_ctb_plot_styles(fileobj)
        self._write_lineweights(fileobj)

    def _write_header(self, fileobj):
        """Write header values of ctb-file to <fileobj>."""
        fileobj.write('description="%s\n' % self.description)
        fileobj.write('aci_table_available=TRUE\n')
        fileobj.write('scale_factor=%.1f\n' % self.scale_factor)
        fileobj.write('apply_factor=%s\n' % str(self.apply_factor).upper())
        fileobj.write('custom_lineweight_display_units=%s\n' % str(
            self.custom_lineweight_display_units))

    def _write_aci_table(self, fileobj):
        """Write autocad color index table to ctb-file <fileobj>."""
        fileobj.write('aci_table{\n')
        for style in self.iter_styles():
            index = style.index
            fileobj.write(' %d="%s\n' % (index, color_name(index)))
        fileobj.write('}\n')

    def _write_ctb_plot_styles(self, fileobj):
        """Write user styles to ctb-file <fileobj>."""
        fileobj.write('plot_style{\n')
        for style in self.iter_styles():
            style.write(fileobj)
        fileobj.write('}\n')

    def _write_lineweights(self, fileobj):
        """Write custom lineweights table to ctb-file <fileobj>."""
        fileobj.write('custom_lineweight_table{\n')
        for index, weight in enumerate(self.lineweights):
            fileobj.write(' %d=%.2f\n' % (index, weight))
        fileobj.write('}\n')

    def parse(self, text):
        """Parse and get values of plot styles from <text>."""

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

    def _compress(self, fileobj, body):
        """Compress ctb-file-body and write it to <fileobj>."""

        def writestr(s):
            if PYTHON3:
                fileobj.write(s.encode())
            else:
                fileobj.write(s)

        if PYTHON3:
            body = body.encode()
        comp_body = zlib.compress(body)
        adler_chksum = zlib.adler32(comp_body)
        writestr('PIAFILEVERSION_2.0,CTBVER1,compress\r\npmzlibcodec')
        fileobj.write(pack('LLL', adler_chksum, len(body), len(comp_body)))
        fileobj.write(comp_body)


def read(fileobj):
    """Read a ctb-file from the file-like object <fileobj>.
    Returns a UserStyle object.
    """
    content = _decompress(fileobj)
    if PYTHON3:
        content = content.decode()
    styles = UserStyles()
    styles.parse(content)
    return styles


def load(filename):
    """Load the ctb-file <filename>."""
    fileobj = open(filename, 'rb')
    ctbfile = read(fileobj)
    fileobj.close()
    return ctbfile


def _decompress(fileobj):
    """Read and decompress the file content of the file-like object <fileobj>."""
    content = fileobj.read()
    text = zlib.decompress(content[60:])
    return text[:-1]  # truncate trailing \nul


class CtbParser(object):
    """A very simple ctb-file parser. Ctb-files are created by programs, so the
    file structure should be correct in the most cases.
    """

    def __init__(self, text):
        """Construtor

        text -- ctb content as string
        """
        self.data = {}
        for element, value in CtbParser.iteritems(text):
            self.data[element] = value

    @staticmethod
    def iteritems(text):
        """iterate over all first level (start at col 0) elements"""

        def get_name(line_index):
            """Get element name of line <line_index>.
            """
            line = lines[line_index]
            if line.endswith('{'):  # start of a list like 'plot_style{'
                name = line[:-1]
            else:  # simple name=value line
                name = line.split('=', 1)[0]
            return name.strip()

        def get_list(line_index):
            """Get list of elements enclosed by { }.

            lineweigths, plot_styles, aci_table
            """

            def end_of_list():
                return lines[line_index].endswith('}')

            data = dict()
            while not end_of_list():
                name = get_name(line_index)
                line_index, value = get_value(line_index)  # get value or sub-list
                data[name] = value
            return line_index + 1, data  # skip '}' - end of list

        def get_value(line_index):
            """Get value of line <line_index> or the list that starts in line
            <line_index>.
            """
            line = lines[line_index]
            if line.endswith('{'):  # start of a list
                line_index, value = get_list(line_index + 1)
            else:  # it's a simple name=value line
                value = line.split('=', 1)[1]
                value = value.lstrip('"')  # strings look like this: name="value
                line_index += 1
            return line_index, value

        def skip_empty_lines(line_index):
            while line_index < len(lines) and len(lines[line_index]) == 0:
                line_index += 1
            return line_index

        lines = text.split('\n')
        line_index = 0
        while line_index < len(lines):
            name = get_name(line_index)
            line_index, value = get_value(line_index)
            yield (name, value)
            line_index = skip_empty_lines(line_index)

    def get(self, name, default):
        return self.data.get(name, default)

# Magic Number: (thx to Rammi)
# Take color from layer, ignore other bytes.
COLOR_BY_LAYER = 0xc0
# Take color from insertion, ignore other bytes
COLOR_BY_BLOCK = 0xc1
# RGB value, other bytes are R,G,B.
COLOR_RGB = 0xc2
# ACI, AutoCAD color index, other bytes are 0,0,index
COLOR_ACI = 0xc3


def int2color(color):
    """Convert color integer value from ctb-file to rgb-tuple plus a magic number.
    """
    # Take color from layer, ignore other bytes.
    magic = (color & 0xff000000) >> 24
    red = (color & 0xff0000) >> 16
    green = (color & 0xff00) >> 8
    blue = color & 0xff
    return (red, green, blue, magic)


def mode_color2int(red, green, blue, magic=0xc2):
    """Convert rgb-tuple to an int value."""
    return -color2int(red, green, blue, magic)


def color2int(red, green, blue, magic):
    """Convert rgb-tuple to an int value."""
    return -((magic << 24) + (red << 16) + (green << 8) + blue) & 0xffffffff
