
.. module:: ezdxf.select

Selection Tools
===============


The :mod:`ezdxf.select` module provides entity selection capabilities, allowing users to 
select entities based on various shapes such as windows, points, circles, polygons, and 
fences.

The selection functions :func:`bbox_inside` and :func:`bbox_outside` work similarly to the 
inside and outside selection tools in CAD applications but the selection is based on the 
bounding box of the DXF entities rather than their actual geometry.

The :func:`bbox_overlap` function works similarly to crossing selection in CAD applications. 
Entities that are outside the selection shape but whose bounding box overlapps the 
selection shape are included in the selection. This is not the case with crossing 
selection in CAD applications.

The selection functions accept any iterable of DXF entities as input and return an 
:class:`ezdxf.query.EntityQuery` container, that provides further selection tools 
based on entity type and DXF attributes.

Usage
-----

Select all entities from the modelspace inside a window defined by two opposite vertices:

.. code-block:: Python

    import ezdxf
    from ezdxf import select

    doc = ezdxf.readfile("your.dxf")
    msp = doc.modelspace()

    # Define a window for selection
    window = select.Window((0, 0), (10, 10))

    # Select entities inside the window from modelspace
    selected_entities = select.bbox_inside(window, msp)

    # Iterate over selected entities
    for entity in selected_entities:
        print(entity)

.. seealso::

    - :ref:`tut_entity_selection`

Selection Functions
-------------------

The following selection functions are implemented:

    - :func:`bbox_inside`
    - :func:`bbox_outside`
    - :func:`bbox_overlap`
    - :func:`bbox_chained`
    - :func:`bbox_crosses_fence`
    - :func:`point_in_bbox`


.. autofunction:: bbox_inside

.. autofunction:: bbox_outside

.. autofunction:: bbox_overlap

.. autofunction:: bbox_chained

.. autofunction:: bbox_crosses_fence

.. autofunction:: point_in_bbox


Selection Shapes
----------------

The following selection shapes are implemented:

- :class:`Window`
- :class:`Circle`
- :class:`Polygon`


.. autoclass:: Window

.. autoclass:: Circle

.. autoclass:: Polygon

Planar Search Index
-------------------

.. versionadded:: 1.4
    
.. autoclass:: PlanarSearchIndex

    .. automethod:: detection_point_in_circle

    .. automethod:: detection_point_in_rect

    .. automethod:: detection_points