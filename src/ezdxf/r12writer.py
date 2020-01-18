# Purpose: fast & simple but restricted DXF R12 writer, with no in-memory drawing, and without dependencies to other
# ezdxf modules. The created DXF file contains no HEADER, TABLES or BLOCKS section only the ENTITIES section is present.
# Created: 14.04.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License
from typing import TextIO, Union, Sequence, Iterable
from contextlib import contextmanager

# types
Vertex = Sequence[float]


def rnd(x: float) -> float:  # adjust output precision of floats by changing 'ndigits'
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
def r12writer(stream: Union[TextIO, str], fixed_tables: bool=False) -> 'R12FastStreamWriter':
    """
    Context manager for writing DXF entities to a stream/file. `stream` can be any file like object
    with a :func:`write` method or just a string for writing DXF entities to the file system.
    If `fixed_tables` is ``True``, a standard TABLES section is written in front of the ENTITIES
    section and some predefined text styles and line types can be used.

    """
    if hasattr(stream, 'write'):
        writer = R12FastStreamWriter(stream, fixed_tables)
        try:
            yield writer
        finally:
            writer.close()
    else:
        with open(stream, 'wt') as stream:
            writer = R12FastStreamWriter(stream, fixed_tables)
            try:
                yield writer
            finally:
                writer.close()


class R12FastStreamWriter:
    """ Fast stream writer to create simple DXF R12 drawings.

    Args:
        stream: a file like object with a :func:`write` method.
        fixed_tables: if `fixed_tables` is ``True``, a standard TABLES section is written in front of the
                      ENTITIES section and some predefined text styles and line types can be used.

    """
    def __init__(self, stream: TextIO, fixed_tables=False):
        self.stream = stream
        if fixed_tables:
            stream.write(PREFACE)
        stream.write("0\nSECTION\n2\nENTITIES\n")  # write header

    def close(self) -> None:
        """ Writes the DXF tail. Call is not necessary when using the context manager :func:`r12writer`. """
        self.stream.write("0\nENDSEC\n0\nEOF\n")  # write tail

    def add_line(self,
                 start: Vertex,
                 end: Vertex,
                 layer: str = "0",
                 color: int = None,
                 linetype: str = None) -> None:
        """
        Add a LINE entity from `start` to `end`.

        Args:
            start: start vertex as ``(x, y[, z])`` tuple
            end: end vertex as  as ``(x, y[, z])`` tuple
            layer: layer name as string, without a layer definition the assigned color = ``7`` (black/white) and
                   line type is ``'Continuous'``.
            color: color as :ref:`ACI` in the range from ``0`` to ``256``,
                   ``0`` is `ByBlock` and ``256`` is `ByLayer`, default is `ByLayer` which is always
                   color = ``7`` (black/white) without a layer definition.
            linetype: line type as string, if FIXED-TABLES are written some predefined line types are available, else
                      line type is always `ByLayer`, which is always ``'Continuous'`` without a LAYERS table.

        """
        dxf = ["0\nLINE\n"]
        dxf.append(dxf_attribs(layer, color, linetype))
        dxf.append(dxf_vertex(start, code=10))
        dxf.append(dxf_vertex(end, code=11))
        self.stream.write(''.join(dxf))

    def add_circle(self,
                   center: Vertex,
                   radius: float,
                   layer: str = "0",
                   color: int = None,
                   linetype: str = None) -> None:
        """
        Add a CIRCLE entity.

        Args:
            center: circle center point as ``(x, y)`` tuple
            radius: circle radius as float
            layer: layer name as string see :meth:`add_line`
            color: color as :ref:`ACI` see :meth:`add_line`
            linetype: line type as string see :meth:`add_line`

        """
        dxf = ["0\nCIRCLE\n"]
        dxf.append(dxf_attribs(layer, color, linetype))
        dxf.append(dxf_vertex(center))
        dxf.append(dxf_tag(40, str(rnd(radius))))
        self.stream.write(''.join(dxf))

    def add_arc(self,
                center: Vertex,
                radius: float,
                start: float = 0,
                end: float = 360,
                layer: str = "0",
                color: int = None,
                linetype: str = None) -> None:
        """
        Add an ARC entity. The arc goes counter clockwise from `start` angle to `end` angle.

        Args:
            center: arc center point as ``(x, y)`` tuple
            radius: arc radius as float
            start: arc start angle in degrees as float
            end: arc end angle in degrees as float
            layer: layer name as string see :meth:`add_line`
            color: color as :ref:`ACI` see :meth:`add_line`
            linetype: line type as string see :meth:`add_line`

        """
        dxf = ["0\nARC\n"]
        dxf.append(dxf_attribs(layer, color, linetype))
        dxf.append(dxf_vertex(center))
        dxf.append(dxf_tag(40, str(rnd(radius))))
        dxf.append(dxf_tag(50, str(rnd(start))))
        dxf.append(dxf_tag(51, str(rnd(end))))
        self.stream.write(''.join(dxf))

    def add_point(self,
                  location: Vertex,
                  layer: str = "0",
                  color: int = None,
                  linetype: str = None) -> None:
        """
        Add a POINT entity.

        Args:
            location: point location as ``(x, y [,z])`` tuple
            layer: layer name as string see :meth:`add_line`
            color: color as :ref:`ACI` see :meth:`add_line`
            linetype: line type as string see :meth:`add_line`

        """
        dxf = ["0\nPOINT\n"]
        dxf.append(dxf_attribs(layer, color, linetype))
        dxf.append(dxf_vertex(location))
        self.stream.write(''.join(dxf))

    def add_3dface(self,
                   vertices: Iterable[Vertex],
                   invisible: int = 0,
                   layer: str = "0",
                   color: int = None,
                   linetype: str = None) -> None:
        """
        Add a 3DFACE entity. 3DFACE is a spatial area with 3 or 4 vertices, all vertices have to be in the same plane.

        Args:
            vertices: iterable of 3 or 4 ``(x, y, z)`` vertices.
            invisible: bit coded flag to define the invisible edges,

                       1. edge = 1
                       2. edge = 2
                       3. edge = 4
                       4. edge = 8

                       Add edge values to set multiple edges invisible, 1. edge + 3. edge = 1 + 4 = 5, all edges = 15

            layer: layer name as string see :meth:`add_line`
            color: color as :ref:`ACI` see :meth:`add_line`
            linetype: line type as string see :meth:`add_line`

        """
        self._add_quadrilateral('3DFACE', vertices, invisible, layer, color, linetype)

    def add_solid(self,
                  vertices: Iterable[Vertex],
                  layer: str = "0",
                  color: int = None,
                  linetype: str = None) -> None:
        """
        Add a SOLID entity. SOLID is a solid filled area with 3 or 4 edges and SOLID is a 2D entity.

        Args:
            vertices: iterable of 3 or 4 ``(x, y[, z])`` tuples, z-axis will be ignored.
            layer: layer name as string see :meth:`add_line`
            color: color as :ref:`ACI` see :meth:`add_line`
            linetype: line type as string see :meth:`add_line`

        """
        self._add_quadrilateral('SOLID', vertices, 0, layer, color, linetype)

    def _add_quadrilateral(self,
                           dxftype: str,
                           vertices: Iterable[Vertex],
                           flags: int,
                           layer: str,
                           color: int,
                           linetype: str) -> None:
        dxf = ["0\n%s\n" % dxftype]
        dxf.append(dxf_attribs(layer, color, linetype))
        vertices = list(vertices)
        if len(vertices) < 3:
            raise ValueError("%s needs 3 or 4 vertices." % dxftype)
        elif len(vertices) == 3:
            vertices.append(vertices[-1])  # double last vertex
        dxf.extend(dxf_vertex(vertex, code) for code, vertex in enumerate(vertices, start=10))
        if flags:
            dxf.append(dxf_tag(70, str(flags)))
        self.stream.write(''.join(dxf))

    def add_polyline(self,
                     vertices: Iterable[Vertex],
                     layer: str = "0",
                     color: int = None,
                     linetype: str = None) -> None:
        """
        Add a POLYLINE entity. The first vertex (axis count) defines, if the POLYLINE is 2D or 3D.

        Args:
            vertices: iterable of ``(x, y[, z])`` tuples
            layer: layer name as string see :meth:`add_line`
            color: color as :ref:`ACI` see :meth:`add_line`
            linetype: line type as string see :meth:`add_line`

        """
        def write_polyline(flags: int) -> None:
            dxf = ["0\nPOLYLINE\n"]
            dxf.append(dxf_attribs(layer, color, linetype))
            dxf.append(dxf_tag(66, 1))  # entities follow
            dxf.append(dxf_tag(70, flags))
            self.stream.write(''.join(dxf))

        polyline_flags, vertex_flags = None, None
        for vertex in vertices:
            if polyline_flags is None:  # first vertex
                if len(vertex) == 3:  # 3d polyline
                    polyline_flags, vertex_flags = (8, 32)
                else:  # 2d polyline
                    polyline_flags, vertex_flags = (0, 0)
                write_polyline(polyline_flags)

            dxf = ["0\nVERTEX\n"]
            dxf.append(dxf_attribs(layer))
            dxf.append(dxf_tag(70, vertex_flags))
            dxf.append(dxf_vertex(vertex))
            self.stream.write(''.join(dxf))
        if polyline_flags is not None:
            self.stream.write("0\nSEQEND\n")

    def add_text(self,
                 text: str,
                 insert: Vertex = (0, 0),
                 height: float = 1.,
                 width: float = 1.,
                 align: str = "LEFT",
                 rotation: float = 0.,
                 oblique: float = 0.,
                 style: str = 'STANDARD',
                 layer: str = "0",
                 color: int = None) -> None:
        """
        Add a one line TEXT entity.

        Args:
            text: the text as string
            insert: insert location as ``(x, y)`` tuple
            height: text height in drawing units
            width: text width as factor
            align: text alignment, see table below
            rotation: text rotation in degrees as float
            oblique: oblique in degrees as float, vertical = ``0`` (default)
            style: text style name as string, if FIXED-TABLES are written some predefined text styles are available,
                   else text style is always ``'STANDARD'``.
            layer: layer name as string see :meth:`add_line`
            color: color as :ref:`ACI` see :meth:`add_line`

        ============   =============== ================= =====
        Vert/Horiz     Left            Center            Right
        ============   =============== ================= =====
        Top            ``TOP_LEFT``    ``TOP_CENTER``    ``TOP_RIGHT``
        Middle         ``MIDDLE_LEFT`` ``MIDDLE_CENTER`` ``MIDDLE_RIGHT``
        Bottom         ``BOTTOM_LEFT`` ``BOTTOM_CENTER`` ``BOTTOM_RIGHT``
        Baseline       ``LEFT``        ``CENTER``         ``RIGHT``
        ============   =============== ================= =====

        The special alignments ``ALIGNED`` and ``FIT`` are not available.

        """
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


def dxf_attribs(layer: str, color: int = None, linetype: str = None) -> str:
    dxf = ["8\n%s\n" % layer]  # layer is required
    if linetype is not None:
        dxf.append("6\n%s\n" % linetype)
    if color is not None:
        if 0 <= int(color) < 257:
            dxf.append("62\n%d\n" % color)
        else:
            raise ValueError("color has to be an integer in the range from 0 to 256.")
    return "".join(dxf)


def dxf_vertex(vertex: Vertex, code=10) -> str:
    dxf = []
    for c in vertex:
        dxf.append("%d\n%s\n" % (code, str(rnd(c))))
        code += 10
    return "".join(dxf)


def dxf_tag(code: int, value) -> str:
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
OpenSans
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
OpenSans-Regular.ttf
  4

  0
STYLE
  5
44F
  2
OpenSansCondensed-Light
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
OpenSansCondensed-Light.ttf
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
