Point
=====

.. module:: ezdxf.entities
    :noindex:

POINT (`DXF Reference`_) at location :attr:`dxf.point`.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'POINT'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_point`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Point

    .. attribute:: dxf.location

        Location of the point (2D/3D Point in :ref:`WCS`)

    .. attribute:: dxf.angle

        Angle in degrees of the x-axis for the UCS in effect when POINT was drawn (float); used when PDMODE is nonzero.

    .. automethod:: transform(m: Matrix44) -> Point

    .. automethod:: translate(dx: float, dy: float, dz: float) -> Point

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-9C6AD32D-769D-4213-85A4-CA9CCB5C5317