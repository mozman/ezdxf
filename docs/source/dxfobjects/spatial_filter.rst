SpatialFilter
=============

.. module:: ezdxf.entities
    :noindex:

The `SPATIAL_FILTER`_ object stores the clipping path for external references and block 
references.  For more information about getting, setting and removing clippings paths 
read the docs for the :class:`ezdxf.xclip.XClip` class.

The HEADER variable $XCLIPFRAME determines if the clipping path is displayed and 
plotted:

=== ===========================
0   not displayed, not plotted
1   displayed, not plotted
2   displayed and plotted
=== ===========================

.. seealso::

    - :mod:`ezdxf.xclip`
    - Knowledge Graph: https://ezdxf.mozman.at/notes/#/page/spatial_filter

======================== =============================================================
Subclass of              :class:`ezdxf.entities.DXFObject`
DXF type                 ``'SPATIAL_FILTER'``
Factory function         internal data structure
======================== =============================================================

.. class:: SpatialFilter

    .. attribute:: dxf.back_clipping_plane_distance

        Defines the distance of the back clipping plane from the origin in direction of 
        the extrusion vector.

    .. attribute:: dxf.is_clipping_enabled

        Block reference clipping is enabled when 1 and disabled when 0.


    .. attribute:: dxf.extrusion

        Defines the orientation of the OCS

    .. attribute:: dxf.front_clipping_plane_distance

        Defines the distance of the front clipping plane from the origin in direction of 
        the extrusion vector.

    .. attribute:: dxf.has_back_clipping_plane

    .. attribute:: dxf.has_front_clipping_plane

    .. attribute:: dxf.origin

        Defines the origin of the OCS

    .. autoproperty:: boundary_vertices

    .. autoproperty:: inverse_insert_matrix

    .. autoproperty:: transform_matrix

    .. automethod:: set_boundary_vertices

    .. automethod:: set_inverse_insert_matrix

    .. automethod:: set_transform_matrix

.. _SPATIAL_FILTER: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-34F179D8-2030-47E4-8D49-F87B6538A05A
