Mesh
====

.. module:: ezdxf.entities
    :noindex:

The :class:`~ezdxf.entities.Mesh` entity is a 3D surface mesh build up
from vertices and faces.

The MESH entity (`DXF Reference`_) is a 3D object in :ref:`WCS` build up
from vertices and faces similar to the :class:`Polyface` entity.

All vertices in :ref:`WCS` as (x, y, z) tuples


======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'MESH'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_mesh`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. seealso::

    :ref:`tut_mesh` and helper classes: :class:`~ezdxf.render.MeshBuilder`,
    :class:`~ezdxf.render.MeshVertexMerger`

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-4B9ADA67-87C8-4673-A579-6E4C76FF7025

.. class:: Mesh

    .. attribute:: dxf.version

    .. attribute:: dxf.blend_crease

        ``0`` = off, ``1`` = on

    .. attribute:: dxf.subdivision_levels

        ``0`` for no smoothing else integer greater than ``0``.

    .. autoattribute:: vertices

    .. autoattribute:: edges

    .. autoattribute:: faces

    .. autoattribute:: creases

    .. automethod:: edit_data

    .. automethod:: transform

MeshData
--------

.. class:: MeshData

    .. attribute:: vertices

        A standard Python list with (x, y, z) tuples (read/write)

    .. attribute:: faces

        A standard Python list with (v1, v2, v3,...) tuples (read/write)

        Each face consist of a list of vertex indices (= index in :attr:`vertices`).

    .. attribute:: edges

        A Python list with (v1, v2) tuples (read/write). This list
        represents the edges to which the :attr:`edge_crease_values` values
        will be applied. Each edge consist of exact two vertex indices
        (= index in :attr:`vertices`).

    .. attribute:: edge_crease_values

        A Python list of float values, one value for each edge. (read/write)

    .. automethod:: add_face

    .. automethod:: add_edge_crease

    .. automethod:: optimize


