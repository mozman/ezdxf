XLine
=====

.. module:: ezdxf.entities
    :noindex:

XLINE entity (`DXF Reference`_) is a construction line that extents to infinity in both directions.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'XLINE'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_xline`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-55080553-34B6-40AA-9EE2-3F3A3A2A5C0A

.. class:: XLine

    .. attribute:: dxf.start

    Location point of line as (3D Point in :ref:`WCS`)

    .. attribute:: dxf.unit_vector

    Unit direction vector as (3D Point in :ref:`WCS`)

    .. automethod:: transform_to_wcs(ucs: UCS)

