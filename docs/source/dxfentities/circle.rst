Circle
======

.. module:: ezdxf.entities

CIRCLE center at location :attr:`dxf.center` and radius of :attr:`dxf.radius`.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'CIRCLE'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_circle`
Inherited DXF Attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Circle

    .. attribute:: dxf.center

    Center point of circle (2D/3D Point in :ref:`OCS`)

    .. attribute:: dxf.radius

    Radius of circle (float)
