XLine
=====

.. module:: ezdxf.entities

Introduced in DXF R13 (``'AC1012'``).

A construction line that extents to infinity in both directions.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'XLINE'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_xline`
Inherited DXF Attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. class:: XLine

    .. attribute:: dxf.start

    Location point of line as (3D Point in :ref:`WCS`)

    .. attribute:: dxf.unit_vector

    Unit direction vector as (3D Point in :ref:`WCS`)

