.. _tut_simple_drawings:

Tutorial for creating simple DXF drawings
=========================================

:ref:`r12writer` - create simple DXF R12 drawings with a restricted entities
set: LINE, CIRCLE, ARC, TEXT, POINT, SOLID, 3DFACE and POLYLINE.
Advantage of the *r12writer* is the speed and the low memory footprint, all
entities are written direct to the file/stream without building a drawing data
structure in memory.

.. seealso::

    :ref:`r12writer`

Create a new DXF drawing with :func:`ezdxf.new` to use all available DXF
entities:

.. code-block:: Python

    import ezdxf

    # Create a new DXF R2010 drawing, official DXF version name: "AC1024"
    doc = ezdxf.new('R2010')

    # Add new entities to the modelspace:
    msp = doc.modelspace()
    # Add a LINE entity
    msp.add_line((0, 0), (10, 0))
    doc.saveas('line.dxf')

New entities are always added to layouts, a layout can be the model space, a
paper space layout or a block layout.

.. seealso::

    :ref:`thematic_factory_method_index`
