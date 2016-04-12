# Purpose: simple but restricted direct DXF R12 writer - no in-memory drawing - no dependencies to other ezdxf modules
# Created: 14.04.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from contextlib import contextmanager

PRECISION = 6

TEXT_ALIGN_FLAGS = {
    'LEFT': (0, 0),
    'CENTER': (1, 0),
    'RIGHT': (2, 0),
    'BOTTOM_LEFT': (0, 1),
    'BOTTOM_CENTER': (1, 1),
    'BOTTOM_RIGHT': (2, 1),
    'MIDDLE_LEFT': (0, 2),
    'MIDDLE_CENTER': (1, 2),
    'MIDDLE_RIGHT': (2, 2),
    'TOP_LEFT': (0, 3),
    'TOP_CENTER': (1, 3),
    'TOP_RIGHT': (2, 3),
}
@contextmanager
def fast_stream_writer(stream):
    writer = StreamWriter(stream)
    yield writer
    writer.close()


@contextmanager
def fast_file_writer(filename):
    with open(filename, 'wt') as stream:
        writer = StreamWriter(stream)
        yield writer
        writer.close()


class StreamWriter(object):
    def __init__(self, stream):
        self.stream = stream
        stream.write("0\nSECTION\n2\nENTITIES\n")  # write header

    def close(self):
        self.stream.write("0\nENDSEC\n0\nEOF\n")  # write tail

    def add_line(self, start, end, layer="0", color=None, linetype=None):
        dxf = ["0\nLINE\n"]
        dxf.append(attribs(layer, color, linetype))
        dxf.append(coord(start, code=10))
        dxf.append(coord(end, code=11))
        self.stream.write(''.join(dxf))

    def add_circle(self, center, radius, layer="0", color=None, linetype=None):
        dxf = ["0\nCIRCLE\n"]
        dxf.append(attribs(layer, color, linetype))
        dxf.append(coord(center))
        dxf.append(dxftag(40, str(round(radius, PRECISION))))
        self.stream.write(''.join(dxf))

    def add_arc(self, center, radius, start=0, end=360, layer="0", color=None, linetype=None):
        dxf = ["0\nARC\n"]
        dxf.append(attribs(layer, color, linetype))
        dxf.append(coord(center))
        dxf.append(dxftag(40, str(round(radius, PRECISION))))
        dxf.append(dxftag(50, str(round(start, PRECISION))))
        dxf.append(dxftag(51, str(round(end, PRECISION))))
        self.stream.write(''.join(dxf))

    def add_point(self, location, layer="0", color=None, linetype=None):
        dxf = ["0\nPOINT\n"]
        dxf.append(attribs(layer, color, linetype))
        dxf.append(coord(location))
        self.stream.write(''.join(dxf))

    def add_3dface(self, vertices, layer="0", color=None, linetype=None):
        self._add_quadrilian('3DFACE', vertices, layer, color, linetype)

    def add_solid(self, vertices, layer="0", color=None, linetype=None):
        self._add_quadrilian('SOLID', vertices, layer, color, linetype)

    def _add_quadrilian(self, dxftype, vertices, layer, color, linetype):
        dxf = ["0\n%s\n" % dxftype]
        dxf.append(attribs(layer, color, linetype))
        vertices = list(vertices)
        if len(vertices) < 3:
            raise ValueError("%s needs 3 ot 4 vertices." % dxftype)
        elif len(vertices) == 3:
            vertices.append(vertices[-1])  # double last vertex
        dxf.extend(coord(vertex, code) for code, vertex in enumerate(vertices, start=10))
        self.stream.write(''.join(dxf))

    def add_polyline(self, vertices, layer="0", color=None, linetype=None):
        vertices = list(vertices)
        if len(vertices):
            if len(vertices[0]) == 3:
                pflags = 8
                vflags = 32
            else:
                pflags = 0
                vflags = 0
        else:
            return
        dxf = ["0\nPOLYLINE\n"]
        dxf.append(attribs(layer, color, linetype))
        dxf.append(dxftag(66, "1"))  # entities follow
        dxf.append(dxftag(70, str(pflags)))
        for vertex in vertices:
            dxf.append("0\nVERTEX\n")
            dxf.append(attribs(layer))
            dxf.append(dxftag(70, str(vflags)))
            dxf.append(coord(vertex))
        dxf.append("0\nSEQEND\n")
        self.stream.write(''.join(dxf))

    def add_text(self, text, insert=(0, 0), height=1., width=1., align="LEFT", rotation=0., oblique=0.,
                 layer="0", color=None):
        # text style is always STANDARD without a TABLES section
        dxf = ["0\nTEXT\n"]
        dxf.append(attribs(layer, color))
        dxf.append(coord(insert, code=10))
        dxf.append(dxftag(1, str(text)))
        dxf.append(dxftag(40, str(round(height, PRECISION))))
        if width != 1.:
            dxf.append(dxftag(41, str(round(width, PRECISION))))
        if rotation != 0.:
            dxf.append(dxftag(50, str(round(rotation, PRECISION))))
        if oblique != 0.:
            dxf.append(dxftag(51, str(round(oblique, PRECISION))))
        halign, valign = TEXT_ALIGN_FLAGS[align.upper()]
        dxf.append(dxftag(72, str(halign)))
        dxf.append(dxftag(73, str(valign)))
        dxf.append(coord(insert, code=11))  # align point
        self.stream.write(''.join(dxf))


def attribs(layer, color=None, linetype=None):
    dxf = ["8\n%s\n" % layer]  # layer is required
    if linetype is not None:
        dxf.append("6\n%s\n" % linetype)
    if color is not None:
        dxf.append("62\n%d\n" % color)
    return "".join(dxf)


def coord(vertex, code=10):
    dxf = []
    for c in vertex:
        c = round(c, PRECISION)
        dxf.append("%d\n%s\n" % (code, str(c)))
        code += 10
    return "".join(dxf)


def dxftag(code, value):
    return "%d\n%s\n" % (code, value)
