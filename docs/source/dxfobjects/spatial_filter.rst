SpatialFilter
=============

.. module:: ezdxf.entities
    :noindex:

The `SPATIAL_FILTER`_ object stores the clipping path for external references and block 
references.  For more information about getting, setting and removing clippings paths 
read the docs for the :class:`ezdxf.xclip.XClip` class.

.. seealso::

    - :mod:`ezdxf.xclip`
    - Knowledge Graph: https://ezdxf.mozman.at/notes/#/page/spatial_filter

======================== =============================================================
Subclass of              :class:`ezdxf.entities.DXFObject`
DXF type                 ``'SPATIAL_FILTER'``
Factory function         internal data structure
======================== =============================================================

.. class:: SpatialFilter

    .. autoproperty:: boundary_vertices

    .. autoproperty:: inverse_insert_matrix

    .. autoproperty:: transform_matrix

    .. automethod:: set_boundary_vertices

    .. automethod:: set_inverse_insert_matrix

    .. automethod:: set_transform_matrix

.. _SPATIAL_FILTER: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-34F179D8-2030-47E4-8D49-F87B6538A05A
