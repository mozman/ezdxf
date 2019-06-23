Arc
===

.. module:: ezdxf.entities

ARC center at location :attr:`dxf.center` and radius of :attr:`dxf.radius` from :attr:`dxf.start_angle` to
:attr:`dxf.end_angle`. ARC goes always from :attr:`dxf.start_angle` to :attr:`dxf.end_angle` in counter clockwise
orientation around the :attr:`dxf.extrusion` vector, which is ``(0, 0, 1)`` by default and the usual case for 2D
arcs.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.Circle`
DXF type                 ``'ARC'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_arc`
Inherited DXF Attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Arc

    .. attribute:: dxf.center

        Center point of arc (2D/3D Point in :ref:`OCS`)

    .. attribute:: dxf.radius

        Radius of arc (float)

    .. attribute:: dxf.start_angle

        Start angle in degrees (float)

    .. attribute:: dxf.end_angle

        End angle in degrees (float)
