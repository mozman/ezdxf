.. _r12writer:

Fast DXF R12 File/Stream Writer
===============================

.. module:: ezdxf.addons.r12writer

The fast file/stream writer creates simple DXF R12 drawings with just an ENTITIES section. The HEADER, TABLES and BLOCKS
sections are not present except FIXED-TABLES are written. Only LINE, CIRCLE, ARC, TEXT, POINT, SOLID, 3DFACE and POLYLINE
entities are supported. FIXED-TABLES is a predefined TABLES section, which will be written, if the init argument
`fixed_tables` of :class:`R12FastStreamWriter` is ``True``.


The :class:`R12FastStreamWriter` writes the DXF entities as strings direct to the stream without creating an
in-memory drawing and therefore the processing is very fast.

Because of the lack of a BLOCKS section, BLOCK/INSERT can not be used. Layers can be used, but this layers have a
default setting color = ``7`` (black/white) and linetype = ``'Continuous'``. If writing the FIXED-TABLES,
some predefined text styles and line types are available, else text style is always ``'STANDARD'`` and line type
is always ``'ByLayer'``.

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

- OpenSans
- OpenSansCondensed-Light

Tutorial
--------

A simple example with different DXF entities::

    from random import random
    from ezdxf.addons import r12writer

    with r12writer("quick_and_dirty_dxf_r12.dxf") as dxf:
        dxf.add_line((0, 0), (17, 23))
        dxf.add_circle((0, 0), radius=2)
        dxf.add_arc((0, 0), radius=3, start=0, end=175)
        dxf.add_solid([(0, 0), (1, 0), (0, 1), (1, 1)])
        dxf.add_point((1.5, 1.5))

        # 2d polyline, new in v0.11.2
        dxf.add_polyline_2d([(5, 5), (7, 3), (7, 6)])

        # 2d polyline with bulge value, new in v0.11.2
        dxf.add_polyline_2d([(5, 5), (7, 3, 0.5), (7, 6)], format='xyb')

        # 3d polyline only, changed in v0.11.2
        dxf.add_polyline([(4, 3, 2), (8, 5, 0), (2, 4, 9)])

        dxf.add_text("test the text entity", align="MIDDLE_CENTER")

A simple example of writing really many entities in a short time::

    from random import random
    from ezdxf.addons import r12writer

    MAX_X_COORD = 1000.0
    MAX_Y_COORD = 1000.0
    CIRCLE_COUNT = 1000000

    with r12writer("many_circles.dxf") as dxf:
        for i in range(CIRCLE_COUNT):
            dxf.add_circle((MAX_X_COORD*random(), MAX_Y_COORD*random()), radius=2)


Show all available line types::

    import ezdxf

    LINETYPES = [
        'CONTINUOUS', 'CENTER', 'CENTERX2', 'CENTER2',
        'DASHED', 'DASHEDX2', 'DASHED2', 'PHANTOM', 'PHANTOMX2',
        'PHANTOM2', 'DASHDOT', 'DASHDOTX2', 'DASHDOT2', 'DOT',
        'DOTX2', 'DOT2', 'DIVIDE', 'DIVIDEX2', 'DIVIDE2',
    ]

    with r12writer('r12_linetypes.dxf', fixed_tables=True) as dxf:
        for n, ltype in enumerate(LINETYPES):
            dxf.add_line((0, n), (10, n), linetype=ltype)
            dxf.add_text(ltype, (0, n+0.1), height=0.25, style='OpenSansCondensed-Light')

Reference
---------

.. autofunction:: r12writer

.. autoclass:: R12FastStreamWriter

    .. automethod:: close

    .. automethod:: add_line

    .. automethod:: add_circle

    .. automethod:: add_arc

    .. automethod:: add_point

    .. automethod:: add_3dface

    .. automethod:: add_solid

    .. automethod:: add_polyline_2d

    .. automethod:: add_polyline

    .. automethod:: add_polyface

    .. automethod:: add_polymesh

    .. automethod:: add_text

