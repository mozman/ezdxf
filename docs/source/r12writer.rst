Introduction
------------

The fast file/stream writer creates simple DXF R12 drawings with just an ENTITIES section. The HEADER, TABLES and BLOCKS
sections are not present. Only LINE, CIRCLE, ARC, TEXT, POINT, SOLID, 3DFACE and POLYLINE entities are supported.

The :class:`StreamWriter` writes the DXF entities as strings direct to the stream without creating an in-memory drawing,
and therefore the processing is very fast.

Because of the lack of a BLOCKS section, BLOCK/INSERT can not be used. Layers can be used, but this layers have a
default setting *color=7 (white/black)* and *linetype='Continuous'*. Text style is always *'STANDARD'*. Only line type
*'CONTINUOUS'* is supported, therefore :class:`StreamWriter` do not set any line type, which means *'ByLayer'*, and this
layer line type can be modified in the CAD application later.

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

.. function:: fast_stream_writer(stream)

    Context manager for writing DXF entities to a stream. *stream* can be any file like object with a *write* method.

.. function:: fast_file_writer(filename)

    Context manager for writing DXF entities direct to the the file system.

.. class:: StreamWriter

.. method:: StreamWriter.__init__(stream)

    Constructor, *stream* should be a file like object with a *write* method.

.. method:: StreamWriter.close()

    Writes the DXF tail. Call is not necessary when you use the context managers :func:`fast_file_writer` or
    :func:`fast_stream_writer`

.. method:: StreamWriter.add_line(start, end, layer="0", color=None)

.. method:: StreamWriter.add_circle(center, radius, layer="0", color=None)

.. method:: StreamWriter.add_arc(center, radius, start=0, end=360, layer="0", color=None)

.. method:: StreamWriter.add_point(location, layer="0", color=None)

.. method:: StreamWriter.add_3dface(vertices, layer="0", color=None)

.. method:: StreamWriter.add_solid(vertices, layer="0", color=None)

.. method:: StreamWriter.add_polyline(vertices, layer="0", color=None)

.. method:: StreamWriter.add_text(text, insert=(0, 0), height=1., width=1., align="LEFT", rotation=0., oblique=0., layer="0", color=None)
