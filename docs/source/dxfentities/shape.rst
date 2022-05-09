Shape
=====

.. module:: ezdxf.entities
    :noindex:

SHAPES  (`DXF Reference`_) are objects that are used like block references, each SHAPE reference can be scaled and
rotated individually.
The SHAPE definitions are stored in external shape files (\*.SHX), and `ezdxf` can not create this shape files.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'SHAPE'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_shape`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Shape

    .. attribute:: dxf.insert

        Insertion location as (2D/3D Point in :ref:`WCS`)

    .. attribute:: dxf.name

        Shape name (str)

    .. attribute:: dxf.size

        Shape size (float)

    .. attribute:: dxf.rotation

        Rotation angle in degrees; default value is 0

    .. attribute:: dxf.xscale

        Relative X scale factor (float); default value is 1

    .. attribute:: dxf.oblique

        Oblique angle in degrees (float); default value is 0

    .. automethod:: transform

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-0988D755-9AAB-4D6C-8E26-EC636F507F2C
