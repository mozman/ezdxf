.. _tut_simple_drawings:

Tutorial for creating DXF drawings
==================================

Create a new DXF document by the :func:`ezdxf.new` function:

.. code-block:: Python

    import ezdxf

    # create a new DXF R2010 document
    doc = ezdxf.new('R2010')

    # add new entities to the modelspace
    msp = doc.modelspace()
    # add a LINE entity
    msp.add_line((0, 0), (10, 0))
    # save the DXF document
    doc.saveas('line.dxf')

New entities are always added to layouts, a layout can be the modelspace, a
paperspace layout or a block layout.

.. seealso::

    :ref:`thematic_factory_method_index`

Simple DXF R12 drawings
-----------------------

The :ref:`r12writer` add-on creates simple DXF R12 drawings with a restricted
set of DXF types: LINE, CIRCLE, ARC, TEXT, POINT, SOLID, 3DFACE and POLYLINE.

The advantage of the :ref:`r12writer` is the speed and the small memory
footprint, all entities are written directly to a file or stream without
creating a document structure in memory.

.. seealso::

    :ref:`r12writer`
