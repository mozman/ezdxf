.. _tut_simple_drawings:

Tutorial for Creating Simple DXF Drawings
=========================================

:ref:`r12writer` - create simple DXF R12 drawings with a restricted entities set: LINE, CIRCLE, ARC, TEXT, POINT,
SOLID, 3DFACE and POLYLINE. Advantage of the *r12writer* is the speed and the low memory footprint, all entities are
written direct to the file/stream without building a drawing data structure in memory.

.. seealso::

    :ref:`r12writer`

Create a new DXF drawing with :func:`ezdxf.new` to use all available DXF entities::

    import ezdxf

    dwg = ezdxf.new('R2010')  # create a new DXF R2010 drawing, official DXF version name: 'AC1024'

    msp = dwg.modelspace()  # add new entities to the model space
    msp.add_line((0, 0), (10, 0))  # add a LINE entity
    dwg.saveas('line.dxf')

New entities are always added to layouts, a layout can be the model space, a paper space layout or a block layout.

.. seealso::

    Look at the :ref:`layout` factory methods to see all the available DXF entities.