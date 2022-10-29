.. _tut_simple_drawings:

Tutorial for creating DXF drawings
==================================

Create a new DXF document by the :func:`ezdxf.new` function:

.. code-block:: Python

    import ezdxf

    # create a new DXF R2010 document
    doc = ezdxf.new("R2010")

    # add new entities to the modelspace
    msp = doc.modelspace()
    # add a LINE entity
    msp.add_line((0, 0), (10, 0))
    # save the DXF document
    doc.saveas("line.dxf")

New entities are always added to layouts, a layout can be the modelspace, a
paperspace layout or a block layout.

.. seealso::

    :ref:`thematic_factory_method_index`

Predefined Resources
--------------------

`Ezdxf` creates new DXF documents with the least possible content, this means
only resources which are absolutely necessary will be created.
The :func:`ezdxf.new` function can create some standard resources, such as
linetypes and text styles, by setting the argument `setup` to ``True``.

.. code-block:: Python

    import ezdxf

    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()
    msp.add_line((0, 0), (10, 0), dxfattribs={"linetype": "DASHED"})

The defined standard linetypes are shown in the basic concept section for
:ref:`linetypes` and the available text styles are shown in the :ref:`tut_text`.

.. important::

    To see the defined text styles in a DXF viewer or CAD application, the
    applications have to know where the referenced TTF fonts can be found.
    This configuration is not possible by `ezdxf` and has to be done for each
    application as described in their documentation.

    See also: :ref:`font resources`

Simple DXF R12 drawings
-----------------------

The :ref:`r12writer` add-on creates simple DXF R12 drawings with a restricted
set of DXF types: LINE, CIRCLE, ARC, TEXT, POINT, SOLID, 3DFACE and POLYLINE.

The advantage of the :ref:`r12writer` is the speed and the small memory
footprint, all entities are written directly to a file or stream without
creating a document structure in memory.

.. seealso::

    :ref:`r12writer`
