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
def r12writer(stream, fixed_tables=False):
    if hasattr(stream, 'write'):
        writer = R12FastStreamWriter(stream, fixed_tables)
        yield writer
        writer.close()
    else:
        with open(stream, 'wt') as stream:
            writer = R12FastStreamWriter(stream, fixed_tables)
            yield writer
            writer.close()


class R12FastStreamWriter(object):
    def __init__(self, stream, fixed_tables=False):
        self.stream = stream
        if fixed_tables:
            stream.write(PREFACE)
        stream.write("0\nSECTION\n2\nENTITIES\n")  # write header

    def close(self):
        self.stream.write("0\nENDSEC\n0\nEOF\n")  # write tail

    def add_line(self, start, end, layer="0", color=None, linetype=None):
        dxf = ["0\nLINE\n"]
        dxf.append(dxf_attribs(layer, color, linetype))
        dxf.append(dxf_vertex(start, code=10))
        dxf.append(dxf_vertex(end, code=11))
        self.stream.write(''.join(dxf))

    def add_circle(self, center, radius, layer="0", color=None, linetype=None):
        dxf = ["0\nCIRCLE\n"]
        dxf.append(dxf_attribs(layer, color, linetype))
        dxf.append(dxf_vertex(center))
        dxf.append(dxf_tag(40, str(rnd(radius))))
        self.stream.write(''.join(dxf))

    def add_arc(self, center, radius, start=0, end=360, layer="0", color=None, linetype=None):
        dxf = ["0\nARC\n"]
        dxf.append(dxf_attribs(layer, color, linetype))
        dxf.append(dxf_vertex(center))
        dxf.append(dxf_tag(40, str(rnd(radius))))
        dxf.append(dxf_tag(50, str(rnd(start))))
        dxf.append(dxf_tag(51, str(rnd(end))))
        self.stream.write(''.join(dxf))

    def add_point(self, location, layer="0", color=None, linetype=None):
        dxf = ["0\nPOINT\n"]
        dxf.append(dxf_attribs(layer, color, linetype))
        dxf.append(dxf_vertex(location))
        self.stream.write(''.join(dxf))

    def add_3dface(self, vertices, invisible=0, layer="0", color=None, linetype=None):
        self._add_quadrilateral('3DFACE', vertices, invisible, layer, color, linetype)

    def add_solid(self, vertices, layer="0", color=None, linetype=None):
        self._add_quadrilateral('SOLID', vertices, 0, layer, color, linetype)

    def _add_quadrilateral(self, dxftype, vertices, flags, layer, color, linetype):
        dxf = ["0\n%s\n" % dxftype]
        dxf.append(dxf_attribs(layer, color, linetype))
        vertices = list(vertices)
        if len(vertices) < 3:
            raise ValueError("%s needs 3 ot 4 vertices." % dxftype)
        elif len(vertices) == 3:
            vertices.append(vertices[-1])  # double last vertex
        dxf.extend(dxf_vertex(vertex, code) for code, vertex in enumerate(vertices, start=10))
        if flags:
            dxf.append(dxf_tag(70, str(flags)))
        self.stream.write(''.join(dxf))

    def add_polyline(self, vertices, layer="0", color=None, linetype=None):
        def write_polyline(flags):
            dxf = ["0\nPOLYLINE\n"]
            dxf.append(dxf_attribs(layer, color, linetype))
            dxf.append(dxf_tag(66, "1"))  # entities follow
            dxf.append(dxf_tag(70, flags))
            self.stream.write(''.join(dxf))

        polyline_flags, vertex_flags = None, None
        for vertex in vertices:
            if polyline_flags is None:  # first vertex
                if len(vertex) == 3:  # 3d polyline
                    polyline_flags, vertex_flags = ('8', '32')
                else:  # 2d polyline
                    polyline_flags, vertex_flags = ('0', '0')
                write_polyline(polyline_flags)

            dxf = ["0\nVERTEX\n"]
            dxf.append(dxf_attribs(layer))
            dxf.append(dxf_tag(70, vertex_flags))
            dxf.append(dxf_vertex(vertex))
            self.stream.write(''.join(dxf))
        if polyline_flags is not None:
            self.stream.write("0\nSEQEND\n")

    def add_text(self, text, insert=(0, 0), height=1., width=1., align="LEFT", rotation=0., oblique=0., style='STANDARD',
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
        if style != "STANDARD":
            dxf.append(dxf_tag(7, str(style)))
        halign, valign = TEXT_ALIGN_FLAGS[align.upper()]
        dxf.append(dxf_tag(72, str(halign)))
        dxf.append(dxf_tag(73, str(valign)))
        dxf.append(dxf_vertex(insert, code=11))  # align point
        self.stream.write(''.join(dxf))


def dxf_attribs(layer, color=None, linetype=None):
    dxf = ["8\n%s\n" % layer]  # layer is required
    if linetype is not None:
        dxf.append("6\n%s\n" % linetype)
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

PREFACE = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1009
  9
$DWGCODEPAGE
  3
ANSI_1252
  0
ENDSEC
  0
SECTION
  2
TABLES
  0
TABLE
  2
LTYPE
  5
431
 70
20
  0
LTYPE
  5
40F
  2
CONTINUOUS
 70
0
  3
Solid line
 72
65
 73
0
 40
0.0
  0
LTYPE
  5
410
  2
CENTER
 70
0
  3
Center ____ _ ____ _ ____ _ ____ _ ____ _ ____
 72
65
 73
4
 40
2.0
 49
1.25
 49
-0.25
 49
0.25
 49
-0.25
  0
LTYPE
  5
411
  2
DASHED
 70
0
  3
Dashed __ __ __ __ __ __ __ __ __ __ __ __ __ _
 72
65
 73
2
 40
0.75
 49
0.5
 49
-0.25
  0
LTYPE
  5
412
  2
PHANTOM
 70
0
  3
Phantom ______  __  __  ______  __  __  ______
 72
65
 73
6
 40
2.5
 49
1.25
 49
-0.25
 49
0.25
 49
-0.25
 49
0.25
 49
-0.25
  0
LTYPE
  5
413
  2
HIDDEN
 70
0
  3
Hidden __ __ __ __ __ __ __ __ __ __ __ __ __ __
 72
65
 73
2
 40
9.525
 49
6.345
 49
-3.175
  0
LTYPE
  5
43B
  2
CENTERX2
 70
0
  3
Center (2x) ________  __  ________  __  ________
 72
65
 73
4
 40
3.5
 49
2.5
 49
-0.25
 49
0.5
 49
-0.25
  0
LTYPE
  5
43C
  2
CENTER2
 70
0
  3
Center (.5x) ____ _ ____ _ ____ _ ____ _ ____
 72
65
 73
4
 40
1.0
 49
0.625
 49
-0.125
 49
0.125
 49
-0.125
  0
LTYPE
  5
43D
  2
DASHEDX2
 70
0
  3
Dashed (2x) ____  ____  ____  ____  ____  ____
 72
65
 73
2
 40
1.2
 49
1.0
 49
-0.2
  0
LTYPE
  5
43E
  2
DASHED2
 70
0
  3
Dashed (.5x) _ _ _ _ _ _ _ _ _ _ _ _ _ _
 72
65
 73
2
 40
0.3
 49
0.25
 49
-0.05
  0
LTYPE
  5
43F
  2
PHANTOMX2
 70
0
  3
Phantom (2x)____________    ____    ____    ____________
 72
65
 73
6
 40
4.25
 49
2.5
 49
-0.25
 49
0.5
 49
-0.25
 49
0.5
 49
-0.25
  0
LTYPE
  5
440
  2
PHANTOM2
 70
0
  3
Phantom (.5x) ___ _ _ ___ _ _ ___ _ _ ___ _ _ ___
 72
65
 73
6
 40
1.25
 49
0.625
 49
-0.125
 49
0.125
 49
-0.125
 49
0.125
 49
-0.125
  0
LTYPE
  5
441
  2
DASHDOT
 70
0
  3
Dash dot __ . __ . __ . __ . __ . __ . __ . __
 72
65
 73
4
 40
1.4
 49
1.0
 49
-0.2
 49
0.0
 49
-0.2
  0
LTYPE
  5
442
  2
DASHDOTX2
 70
0
  3
Dash dot (2x) ____  .  ____  .  ____  .  ____
 72
65
 73
4
 40
2.4
 49
2.0
 49
-0.2
 49
0.0
 49
-0.2
  0
LTYPE
  5
443
  2
DASHDOT2
 70
0
  3
Dash dot (.5x) _ . _ . _ . _ . _ . _ . _ . _
 72
65
 73
4
 40
0.7
 49
0.5
 49
-0.1
 49
0.0
 49
-0.1
  0
LTYPE
  5
444
  2
DOT
 70
0
  3
Dot .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
 72
65
 73
2
 40
0.2
 49
0.0
 49
-0.2
  0
LTYPE
  5
445
  2
DOTX2
 70
0
  3
Dot (2x) .    .    .    .    .    .    .    .
 72
65
 73
2
 40
0.4
 49
0.0
 49
-0.4
  0
LTYPE
  5
446
  2
DOT2
 70
0
  3
Dot (.5) . . . . . . . . . . . . . . . . . . .
 72
65
 73
2
 40
0.1
 49
0.0
 49
-0.1
  0
LTYPE
  5
447
  2
DIVIDE
 70
0
  3
Divide __ . . __ . . __ . . __ . . __ . . __
 72
65
 73
6
 40
1.6
 49
1.0
 49
-0.2
 49
0.0
 49
-0.2
 49
0.0
 49
-0.2
  0
LTYPE
  5
448
  2
DIVIDEX2
 70
0
  3
Divide (2x) ____  . .  ____  . .  ____  . .  ____
 72
65
 73
6
 40
2.6
 49
2.0
 49
-0.2
 49
0.0
 49
-0.2
 49
0.0
 49
-0.2
  0
LTYPE
  5
449
  2
DIVIDE2
 70
0
  3
Divide(.5x) _ . _ . _ . _ . _ . _ . _ . _
 72
65
 73
6
 40
0.8
 49
0.5
 49
-0.1
 49
0.0
 49
-0.1
 49
0.0
 49
-0.1
  0
ENDTAB
  0
TABLE
  2
STYLE
  5
433
 70
18
  0
STYLE
  5
417
  2
STANDARD
 70
0
 40
0.0
 41
1.0
 50
0.0
 71
0
 42
0.2
  3
txt
  4

  0
STYLE
  5
44A
  2
ARIAL
 70
0
 40
0.0
 41
1.0
 50
0.0
 71
0
 42
1.0
  3
arial.ttf
  4

  0
STYLE
  5
44F
  2
ARIAL_NARROW
 70
0
 40
0.0
 41
1.0
 50
0.0
 71
0
 42
1.0
  3
arialn.ttf
  4

  0
STYLE
  5
453
  2
ISOCPEUR
 70
0
 40
0.0
 41
1.0
 50
0.0
 71
0
 42
1.0
  3
isocpeur.ttf
  4

  0
STYLE
  5
455
  2
TIMES
 70
0
 40
0.0
 41
1.0
 50
0.0
 71
0
 42
1.0
  3
times.ttf
  4

  0
ENDTAB
  0
TABLE
  2
VIEW
  5
434
 70
0
  0
ENDTAB
  0
ENDSEC
"""
