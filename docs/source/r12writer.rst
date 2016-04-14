.. _r12writer:

Fast DXF R12 File/Stream Writer
-------------------------------

The fast file/stream writer creates simple DXF R12 drawings with just an ENTITIES section. The HEADER, TABLES and BLOCKS
sections are not present except FIXED-TABLES are written. Only LINE, CIRCLE, ARC, TEXT, POINT, SOLID, 3DFACE and POLYLINE
entities are supported. FIXED-TABLES is a predefined TABLES section, which will be written, if the init argument
*fixed_tables* of :class:`R12FastStreamWriter` is *True*.


The :class:`R12FastStreamWriter` writes the DXF entities as strings direct to the stream without creating an
in-memory drawing and therefore the processing is very fast.

Because of the lack of a BLOCKS section, BLOCK/INSERT can not be used. Layers can be used, but this layers have a
default setting *color=7 (black/white)* and *linetype='Continuous'*. If writing the FIXED-TABLES, some predefined text
styles and line types are available, else text style is always *'STANDARD'* and line type is always *'ByLayer'*.

If using FIXED-TABLES, following predefined line types are available:

- CONTINUOUS
- CENTER ``____ _ ____ _ ____ _ ____ _ ____ _ ____``
- CENTERX2 ``________  __  ________  __  ________``
- CENTER2 ``____ _ ____ _ ____ _ ____ _ ____``
- DASHED ``__ __ __ __ __ __ __ __ __ __ __ __ __ _``
- DASHEDX2 ``____  ____  ____  ____  ____  ____``
- DASHED2 ``_ _ _ _ _ _ _ _ _ _ _ _ _ _``
- PHANTOM ``______  __  __  ______  __  __  ______``
- PHANTOMX2 ``____________    ____    ____    ____________``
- PHANTOM2 ``___ _ _ ___ _ _ ___ _ _ ___ _ _ ___``
- DASHDOT ``__ . __ . __ . __ . __ . __ . __ . __``
- DASHDOTX2 ``____  .  ____  .  ____  .  ____``
- DASHDOT2 ``_ . _ . _ . _ . _ . _ . _ . _``
- DOT ``.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .``
- DOTX2 ``.    .    .    .    .    .    .    .``
- DOT2 ``. . . . . . . . . . . . . . . . . . .``
- DIVIDE ``__ . . __ . . __ . . __ . . __ . . __``
- DIVIDEX2 ``____  . .  ____  . .  ____  . .  ____``
- DIVIDE2 ``_ . _ . _ . _ . _ . _ . _ . _``

If using FIXED-TABLES, following predefined text styles are available:

- ARIAL
- ARIAL_NARROW
- ISOCPEUR
- TIMES

Tutorial
--------

A simple example with different DXF entities::

    from random import random
    from ezdxf.r12writer import r12writer

    with r12writer("quick_and_dirty_dxf_r12.dxf") as dxf:
        dxf.add_line((0, 0), (17, 23))
        dxf.add_circle((0, 0), radius=2)
        dxf.add_arc((0, 0), radius=3, start=0, end=175)
        dxf.add_solid([(0, 0), (1, 0), (0, 1), (1, 1)])
        dxf.add_point((1.5, 1.5))
        dxf.add_polyline([(5, 5), (7, 3), (7, 6)])  # 2d polyline
        dxf.add_polyline([(4, 3, 2), (8, 5, 0), (2, 4, 9)])  # 3d polyline
        dxf.add_text("test the text entity", align="MIDDLE_CENTER")

A simple example of writing really many entities in a short time::

    from random import random
    from ezdxf.r12writer import r12writer

    MAX_X_COORD = 1000.0
    MAX_Y_COORD = 1000.0
    CIRCLE_COUNT = 1000000

    with r12writer("many_circles.dxf") as dxf:
        for i in range(CIRCLE_COUNT):
            dxf.add_circle((MAX_X_COORD*random(), MAX_Y_COORD*random()), radius=2)


Show all available line types::

    import ezdxf

    LINETYPES = [
        'CONTINUOUS', 'CENTER', 'CENTERX2', 'CENTER2', 'DASHED', 'DASHEDX2', 'DASHED2', 'PHANTOM', 'PHANTOMX2',
        'PHANTOM2', 'DASHDOT', 'DASHDOTX2', 'DASHDOT2', 'DOT', 'DOTX2', 'DOT2', 'DIVIDE', 'DIVIDEX2', 'DIVIDE2',
    ]

    with r12writer('r12_linetypes.dxf', fixed_tables=True) as dxf:
        for n, ltype in enumerate(LINETYPES):
            dxf.add_line((0, n), (10, n), linetype=ltype)
            dxf.add_text(ltype, (0, n+0.1), height=0.25, style='ARIAL_NARROW')

Reference
---------

.. function:: r12writer(stream, fixed_tables=False)

    Context manager for writing DXF entities to a stream/file. *stream* can be any file like object with a *write*
    method or just a string for writing DXF entities to the file system. If *fixed_tables* is *True*, a standard
    TABLES section is written in front of the ENTITIES section and some predefined text styles and line types can be
    used.

.. class:: R12FastStreamWriter

    Fast stream writer to create simple DXF R12 drawings.

.. method:: R12FastStreamWriter.__init__(stream, fixed_tables=False)

    Constructor, *stream* should be a file like object with a *write* method. If *fixed_tables* is *True*, a standard
    TABLES section is written in front of the ENTITIES section and some predefined text styles and line types can be
    used.

.. method:: R12FastStreamWriter.close()

    Writes the DXF tail. Call is not necessary when using the context manager :func:`r12writer`.

.. method:: R12FastStreamWriter.add_line(start, end, layer="0", color=None, linetype=None)

    Add a LINE entity from *start* to *end*.

    :param start: start vertex 2d/3d vertex as (x, y [,z]) tuple
    :param end: end vertex 2d/3d vertex as (x, y [,z]) tuple
    :param layer: layer name as string, without a layer definition the assigned color=7 (black/white) and line type is
        *Continuous*.
    :param color: color as ACI (AutoCAD Color Index) as integer in the range from 0 to 256, 0 is *ByBlock* and 256 is
        *ByLayer*, default is *ByLayer* which is always color=7 (black/white) without a layer definition.
    :param linetype: line type as string, if FIXED-TABLES is written some predefined line types are available, else
        line type is always *ByLayer*, which is always *Continuous* without a LAYERS table.

.. method:: R12FastStreamWriter.add_circle(center, radius, layer="0", color=None, linetype=None)

    Add a CIRCLE entity.

    :param center: circle center point as (x, y) tuple
    :param radius: circle radius as float
    :param layer: layer name as string see :meth:`~R12FastStreamWriter.add_line`
    :param color: color as ACI see :meth:`~R12FastStreamWriter.add_line`
    :param linetype: line type as string see :meth:`~R12FastStreamWriter.add_line`

.. method:: R12FastStreamWriter.add_arc(center, radius, start=0, end=360, layer="0", color=None, linetype=None)

    Add an ARC entity. The arc goes counter clockwise from *start* angle to *end* angle.

    :param center: center point of arc as (x, y) tuple
    :param radius: arc radius as float
    :param start: arc start angle in degrees as float (360 degree = circle)
    :param end: arc end angle in degrees as float
    :param layer: layer name as string, see :meth:`~R12FastStreamWriter.add_line`
    :param color: color as ACI, see :meth:`~R12FastStreamWriter.add_line`
    :param linetype: line type as string, see :meth:`~R12FastStreamWriter.add_line`

.. method:: R12FastStreamWriter.add_point(location, layer="0", color=None, linetype=None)

    Add a POINT entity.

    :param location: point location as (x, y [,z]) tuple
    :param layer: layer name as string, see :meth:`~R12FastStreamWriter.add_line`
    :param color: color as ACI, see :meth:`~R12FastStreamWriter.add_line`
    :param linetype: line type as string, see :meth:`~R12FastStreamWriter.add_line`

.. method:: R12FastStreamWriter.add_3dface(vertices, invisible=0, layer="0", color=None, linetype=None)

    Add a 3DFACE entity. 3DFACE is a spatial area with 3 ot 4 vertices, all vertices have to be in the same plane.

    :param vertices: list of 3 or 4 (x, y, z) vertices.
    :param invisible: bit coded flag to define the invisible edges, 1. edge = 1, 2. edge = 2, 3. edge = 4, 4. edge = 8;
        add edge values to set multiple edges invisible, 1. edge + 3. edge = 1 + 4 = 5, all edges = 15
    :param layer: layer name as string, see :meth:`~R12FastStreamWriter.add_line`
    :param color: color as ACI, see :meth:`~R12FastStreamWriter.add_line`
    :param linetype: line type as string, see :meth:`~R12FastStreamWriter.add_line`

.. method:: R12FastStreamWriter.add_solid(vertices, layer="0", color=None, linetype=None)

    Add a SOLID entity. SOLID is a solid filled area with 3 or 4 edges and SOLID is 2d entity.

    :param vertices: list of 3 or 4 (x, y [,z]) tuples, z axis will be ignored.
    :param layer: layer name as string, see :meth:`~R12FastStreamWriter.add_line`
    :param color: color as ACI, see :meth:`~R12FastStreamWriter.add_line`
    :param linetype: line type as string, see :meth:`~R12FastStreamWriter.add_line`

.. method:: R12FastStreamWriter.add_polyline(vertices, layer="0", color=None, linetype=None)

    Add a POLYLINE entity. The first vertex (axis count) defines, if the POLYLINE is 2d or 3d.

    :param vertices: list of (x, y [,z]) tuples, handles generators without building a temporary lists.
    :param layer: layer name as string, see :meth:`~R12FastStreamWriter.add_line`
    :param color: color as ACI, see :meth:`~R12FastStreamWriter.add_line`
    :param linetype: line type as string, see :meth:`~R12FastStreamWriter.add_line`

.. method:: R12FastStreamWriter.add_text(text, insert=(0, 0), height=1., width=1., align="LEFT", rotation=0., oblique=0., style='STANDARD', layer="0", color=None)

    Add a one line TEXT entity.

    :param text: the text as string
    :param insert: insert point as (x, y) tuple
    :param height: text height in drawing units
    :param width: text width as factor
    :param align: text alignment, see table below
    :param rotation: text rotation in degrees as float (360 degree = circle)
    :param oblique: oblique in degrees as float, vertical=0 (default)
    :param style: text style name as string, if FIXED-TABLES are written some predefined text styles are available, else
        text style is always ``STANDARD``.
    :param layer: layer name as string, see :meth:`~R12FastStreamWriter.add_line`
    :param color: color as ACI, see :meth:`~R12FastStreamWriter.add_line`

============   =============== ================= =====
Vert/Horiz     Left            Center            Right
============   =============== ================= =====
Top            ``TOP_LEFT``    ``TOP_CENTER``    ``TOP_RIGHT``
Middle         ``MIDDLE_LEFT`` ``MIDDLE_CENTER`` ``MIDDLE_RIGHT``
Bottom         ``BOTTOM_LEFT`` ``BOTTOM_CENTER`` ``BOTTOM_RIGHT``
Baseline       ``LEFT``        ``CENTER``         ``RIGHT``
============   =============== ================= =====

The special alignments ``ALIGNED`` and ``FIT`` are not available.
