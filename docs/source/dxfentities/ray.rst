Ray
===

.. module:: ezdxf.entities

Introduced in DXF R13 (``'AC1012'``).

A :class:`Ray` starts at :attr:`Ray.dxf.point` and continues to infinity (construction line).

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'RAY'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_ray`
Inherited DXF Attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. class:: Ray

    .. attribute:: dxf.start

    Start point as (3D Point in :ref:`WCS`)

    .. attribute:: dxf.unit_vector

    Unit direction vector as (3D Point in :ref:`WCS`)

