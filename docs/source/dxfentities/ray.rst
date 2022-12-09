Ray
===

.. module:: ezdxf.entities
    :noindex:

The RAY entity (`DXF Reference`_) starts at :attr:`Ray.dxf.point` and continues to
infinity (construction line).

======================== ==========================================
Subclass of              :class:`ezdxf.entities.XLine`
DXF type                 ``'RAY'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_ray`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-638B9F01-5D86-408E-A2DE-FA5D6ADBD415

.. class:: Ray

    .. attribute:: dxf.start

    Start point as (3D Point in :ref:`WCS`)

    .. attribute:: dxf.unit_vector

    Unit direction vector as (3D Point in :ref:`WCS`)

    .. automethod:: transform

    .. automethod:: translate
