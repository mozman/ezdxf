XLine
=====

.. class:: XLine(GraphicEntity)

Introduced in DXF version R13 (AC1012), dxftype is XLINE.

A line that extents to infinity in both directions, used as construction line. Create :class:`XLine` in layouts and
blocks by factory function :meth:`~ezdxf.modern.layouts.Layout.add_xline`.

DXF Attributes for XLine
------------------------

:ref:`Common DXF attributes for DXF R13 or later`

.. attribute:: XLine.dxf.start

Location point of line as (3D Point in :ref:`WCS`)

.. attribute:: XLine.dxf.unit_vector

Unit direction vector as (3D Point in :ref:`WCS`)

