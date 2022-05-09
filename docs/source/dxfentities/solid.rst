Solid
=====

.. module:: ezdxf.entities
    :noindex:

SOLID (`DXF Reference`_) is a filled triangle or quadrilateral.
Access vertices by name (:code:`entity.dxf.vtx0 = (1.7, 2.3)`) or by index
(:code:`entity[0] = (1.7, 2.3)`). If only 3 vertices are provided the
last (3rd) vertex will be repeated in the DXF file.

The SOLID entity stores the vertices in an unusual way, the last two vertices
are reversed. The coordinates [(0, 0), (1, 0), (1, 1), (0, 1)] do not create
a square as you would expect:

.. image:: gfx/solid0.png
    :align: center

Reverse the last two vertices to get the `expected` square:
[(0, 0), (1, 0), (0, 1), (1, 1)]

.. image:: gfx/solid1.png
    :align: center

.. note::

    The :meth:`Solid.vertices` and :meth:`Solid.wcs_vertices` methods return the
    vertices in the `expected` (reversed) order.


======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'SOLID'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_solid`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided
    factory functions!

.. class:: Solid

    .. attribute:: dxf.vtx0

        Location of 1. vertex (2D/3D Point in :ref:`OCS`)

    .. attribute:: dxf.vtx1

        Location of 2. vertex (2D/3D Point in :ref:`OCS`)

    .. attribute:: dxf.vtx2

        Location of 3. vertex (2D/3D Point in :ref:`OCS`)

    .. attribute:: dxf.vtx3

        Location of 4. vertex (2D/3D Point in :ref:`OCS`)

    .. automethod:: transform

    .. automethod:: vertices

    .. automethod:: wcs_vertices

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-E0C5F04E-D0C5-48F5-AC09-32733E8848F2
