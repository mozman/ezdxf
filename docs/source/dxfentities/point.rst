Point
=====

.. module:: ezdxf.entities

POINT at location :attr:`dxf.point`.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'POINT'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_point`
Inherited DXF Attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Point

    .. attribute:: dxf.location

        Location of the point (2D/3D Point in :ref:`WCS`)

    .. attribute:: dxf.angle

        Angle in degrees of the x-axis for the UCS in effect when POINT was drawn (float); used when PDMODE is nonzero.
