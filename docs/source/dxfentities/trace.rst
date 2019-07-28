Trace
=====

.. module:: ezdxf.entities
    :noindex:

TRACE entity (`DXF Reference`_) is solid filled triangle or quadrilateral. Access vertices by name
(:code:`entity.dxf.vtx0 = (1.7, 2.3)`) or by index (:code:`entity[0] = (1.7, 2.3)`).
I don't know the difference between SOLID and TRACE.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'TRACE'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_trace`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!


.. class:: Trace

    .. attribute:: dxf.vtx0

        Location of 1. vertex (2D/3D Point in :ref:`OCS`)

    .. attribute:: dxf.vtx1

        Location of 2. vertex (2D/3D Point in :ref:`OCS`)

    .. attribute:: dxf.vtx2

        Location of 3. vertex (2D/3D Point in :ref:`OCS`)

    .. attribute:: dxf.vtx3

        Location of 4. vertex (2D/3D Point in :ref:`OCS`)

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-EA6FBCA8-1AD6-4FB2-B149-770313E93511