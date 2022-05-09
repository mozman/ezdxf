Line
====

.. module:: ezdxf.entities
    :noindex:

LINE (`DXF Reference`_) entity is a 3D line from :attr:`Line.dxf.start` to :attr:`Line.dxf.end`.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'LINE'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_line`
Inherited DXF Attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Line


    .. attribute:: dxf.start

        start point of line (2D/3D Point in :ref:`WCS`)

    .. attribute:: dxf.end

        end point of line (2D/3D Point in :ref:`WCS`)

    .. attribute:: dxf.thickness

        Line thickness in 3D space in direction :attr:`extrusion`, default value is ``0``. This value should not be
        confused with the :attr:`~ezdxf.entities.DXFGraphic.dxf.lineweight` value.

    .. attribute:: dxf.extrusion

        extrusion vector, default value is ``(0, 0, 1)``

    .. automethod:: transform

    .. automethod:: translate

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-FCEF5726-53AE-4C43-B4EA-C84EB8686A66