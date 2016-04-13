# Purpose: fast & simple but restricted DXF R12 writer, with no in-memory drawing, and without dependencies to other
# ezdxf modules. The created DXF file contains no HEADER, TABLES or BLOCKS section only the ENTITIES section is present.
# Created: 14.04.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from contextlib import contextmanager


def rnd(x):  # adjust output precision of floats by changing 'ndigits'
    return round(x, ndigits=6)

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

    def add_line(self, start, end, layer="0", color=None):
        dxf = ["0\nLINE\n"]
        dxf.append(dxf_attribs(layer, color))
        dxf.append(dxf_vertex(start, code=10))
        dxf.append(dxf_vertex(end, code=11))
        self.stream.write(''.join(dxf))

    def add_circle(self, center, radius, layer="0", color=None):
        dxf = ["0\nCIRCLE\n"]
        dxf.append(dxf_attribs(layer, color))
        dxf.append(dxf_vertex(center))
        dxf.append(dxf_tag(40, str(rnd(radius))))
        self.stream.write(''.join(dxf))

    def add_arc(self, center, radius, start=0, end=360, layer="0", color=None):
        dxf = ["0\nARC\n"]
        dxf.append(dxf_attribs(layer, color))
        dxf.append(dxf_vertex(center))
        dxf.append(dxf_tag(40, str(rnd(radius))))
        dxf.append(dxf_tag(50, str(rnd(start))))
        dxf.append(dxf_tag(51, str(rnd(end))))
        self.stream.write(''.join(dxf))

    def add_point(self, location, layer="0", color=None):
        dxf = ["0\nPOINT\n"]
        dxf.append(dxf_attribs(layer, color))
        dxf.append(dxf_vertex(location))
        self.stream.write(''.join(dxf))

    def add_3dface(self, vertices, layer="0", color=None):
        self._add_quadrilateral('3DFACE', vertices, layer, color)

    def add_solid(self, vertices, layer="0", color=None):
        self._add_quadrilateral('SOLID', vertices, layer, color)

    def _add_quadrilateral(self, dxftype, vertices, layer, color):
        dxf = ["0\n%s\n" % dxftype]
        dxf.append(dxf_attribs(layer, color))
        vertices = list(vertices)
        if len(vertices) < 3:
            raise ValueError("%s needs 3 ot 4 vertices." % dxftype)
        elif len(vertices) == 3:
            vertices.append(vertices[-1])  # double last vertex
        dxf.extend(dxf_vertex(vertex, code) for code, vertex in enumerate(vertices, start=10))
        self.stream.write(''.join(dxf))

    def add_polyline(self, vertices, layer="0", color=None):
        vertices = list(vertices)
        if len(vertices):
            if len(vertices[0]) == 3:  # 3d polyline
                pflags = 8
                vflags = 32
            else:    # 2d polyline
                pflags = 0
                vflags = 0
        else:
            return
        dxf = ["0\nPOLYLINE\n"]
        dxf.append(dxf_attribs(layer, color))
        dxf.append(dxf_tag(66, "1"))  # entities follow
        dxf.append(dxf_tag(70, str(pflags)))
        for vertex in vertices:
            dxf.append("0\nVERTEX\n")
            dxf.append(dxf_attribs(layer))
            dxf.append(dxf_tag(70, str(vflags)))
            dxf.append(dxf_vertex(vertex))
        dxf.append("0\nSEQEND\n")
        self.stream.write(''.join(dxf))

    def add_text(self, text, insert=(0, 0), height=1., width=1., align="LEFT", rotation=0., oblique=0.,
                 layer="0", color=None):
        # text style is always STANDARD without a TABLES section
        dxf = ["0\nTEXT\n"]
        dxf.append(dxf_attribs(layer, color))
        dxf.append(dxf_vertex(insert, code=10))
        dxf.append(dxf_tag(1, str(text)))
        dxf.append(dxf_tag(40, str(rnd(height))))
        if width != 1.:
            dxf.append(dxf_tag(41, str(rnd(width))))
        if rotation != 0.:
            dxf.append(dxf_tag(50, str(rnd(rotation))))
        if oblique != 0.:
            dxf.append(dxf_tag(51, str(rnd(oblique))))
        halign, valign = TEXT_ALIGN_FLAGS[align.upper()]
        dxf.append(dxf_tag(72, str(halign)))
        dxf.append(dxf_tag(73, str(valign)))
        dxf.append(dxf_vertex(insert, code=11))  # align point
        self.stream.write(''.join(dxf))


def dxf_attribs(layer, color=None):
    dxf = ["8\n%s\n" % layer]  # layer is required
    if color is not None:
        if 0 <= int(color) < 257:
            dxf.append("62\n%d\n" % color)
        else:
            raise ValueError("color has to be an integer in the range from 0 to 256.")
    return "".join(dxf)


def dxf_vertex(vertex, code=10):
    dxf = []
    for c in vertex:
        dxf.append("%d\n%s\n" % (code, str(rnd(c))))
        code += 10
    return "".join(dxf)


def dxf_tag(code, value):
    return "%d\n%s\n" % (code, value)
