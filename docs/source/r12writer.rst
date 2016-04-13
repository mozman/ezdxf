Introduction
------------

The fast file/stream writer creates simple DXF R12 drawings with just an ENTITIES section. The HEADER, TABLES and BLOCKS
sections are not present except *FIXED-TABLES* are written. Only LINE, CIRCLE, ARC, TEXT, POINT, SOLID, 3DFACE and POLYLINE
entities are supported. *FIXED-TABLES* is a predefined TABLES section, which is written if the init argument
*fixed_tables* of :class:``R12FastStreamWriter`` is *True*.


The :class:`R12FastStreamWriter` writes the DXF entities as strings direct to the stream without creating an
in-memory drawing and therefore the processing is very fast.

Because of the lack of a BLOCKS section, BLOCK/INSERT can not be used. Layers can be used, but this layers have a
default setting *color=7 (white/black)* and *linetype='Continuous'*. If writing the *FIXED-TABLES* some text styles and
line types are supported, else text style is always *'STANDARD'* and line type is always *'ByLayer'*

If using FIXED-TABLES, following additional line types are supported:

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

If using FIXED-TABLES, following additional text styles are supported:

- ARIAL
- ARIAL_BOLD
- ARIAL_ITALIC
- ARIAL_BOLD_ITALIC
- ARIAL_BLACK
- ARIAL_NARROW
- ARIAL_NARROW_BOLD
- ARIAL_NARROW_ITALIC
- ARIAL_NARROW_BOLD_ITALIC
- ISOCPEUR
- ISOCPEUR_ITALIC
- TIMES
- TIMES_BOLD
- TIMES_ITALIC
- TIMES_BOLD_ITALIC

Tutorial
--------

A simple example with different DXF entities::

    from random import random
    import ezdxf

    with ezdxf.fast_file_writer("quick_and_dirty_dxf_r12.dxf") as dxf:
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
    import ezdxf

    MAX_X_COORD = 1000.0
    MAX_Y_COORD = 1000.0
    CIRCLE_COUNT = 1000000

    with ezdxf.fast_file_writer("many_circles.dxf") as dxf:
        for i in range(CIRCLE_COUNT):
            dxf.add_circle((MAX_X_COORD*random(), MAX_Y_COORD*random()), radius=2)

Reference
---------

.. function:: fast_stream_writer(stream, fixed_tables=False)

    Context manager for writing DXF entities to a stream. *stream* can be any file like object with a *write* method.

.. function:: fast_file_writer(filename, fixed_tables=False)

    Context manager for writing DXF entities direct to the the file system.

.. class:: R12FastStreamWriter

.. method:: StreamWriter.__init__(stream, fixed_tables=False)

    Constructor, *stream* should be a file like object with a *write* method. If *fixed_tables* is *True*, a standard
    TABLES section is written in front of the ENTITIES section and some predefined text styles and line types can be
    used.

.. method:: StreamWriter.close()

    Writes the DXF tail. Call is not necessary when you use the context managers :func:`fast_file_writer` or
    :func:`fast_stream_writer`

.. method:: StreamWriter.add_line(start, end, layer="0", color=None, linetype=None)

.. method:: StreamWriter.add_circle(center, radius, layer="0", color=None, linetype=None)

.. method:: StreamWriter.add_arc(center, radius, start=0, end=360, layer="0", color=None, linetype=None)

.. method:: StreamWriter.add_point(location, layer="0", color=None, linetype=None)

.. method:: StreamWriter.add_3dface(vertices, layer="0", color=None, linetype=None)

.. method:: StreamWriter.add_solid(vertices, layer="0", color=None, linetype=None)

.. method:: StreamWriter.add_polyline(vertices, layer="0", color=None, linetype=None)

.. method:: StreamWriter.add_text(text, insert=(0, 0), height=1., width=1., align="LEFT", rotation=0., oblique=0., style='STANDARD', layer="0", color=None)
