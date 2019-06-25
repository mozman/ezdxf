Solid
=====

.. module:: ezdxf.entities


A SOLID (`DXF Reference`_) is a filled triangle or quadrilateral. Access vertices by name
(:code:`entity.dxf.vtx0 = (1.7, 2.3)`) or by index (:code:`entity[0] = (1.7, 2.3)`).

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'SOLID'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_solid`
Inherited DXF Attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Solid

    .. attribute:: dxf.vtx0

        Location of 1. vertex (2D/3D Point in :ref:`OCS`)

    .. attribute:: dxf.vtx1

        Location of 2. vertex (2D/3D Point in :ref:`OCS`)

    .. attribute:: dxf.vtx2

        Location of 3. vertex (2D/3D Point in :ref:`OCS`)

    .. attribute:: dxf.vtx3

        Location of 4. vertex (2D/3D Point in :ref:`OCS`)


.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-E0C5F04E-D0C5-48F5-AC09-32733E8848F2
