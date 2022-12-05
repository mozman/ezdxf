Arc
===

.. module:: ezdxf.entities
    :noindex:

ARC (`DXF Reference`_) center at location :attr:`dxf.center` and radius of
:attr:`dxf.radius` from :attr:`dxf.start_angle` to :attr:`dxf.end_angle`.
ARC goes always from :attr:`dxf.start_angle` to :attr:`dxf.end_angle` in counter-clockwise
orientation around the :attr:`dxf.extrusion` vector, which is (0, 0, 1)
by default and the usual case for 2D arcs. The ARC entity has :ref:`OCS`
coordinates.

The helper tool :class:`ezdxf.math.ConstructionArc` supports creating arcs from
various scenarios, like from 3 points or 2 points and an angle or 2 points and
a radius and the :mod:`~ezdxf.upright` module can convert inverted extrusion vectors
from (0, 0, -1) to (0, 0, 1) without changing the curve.

.. seealso::

    - :ref:`tut_dxf_primitives`, section :ref:`tut_dxf_primitives_arc`
    - :class:`ezdxf.math.ConstructionArc`
    - :ref:`Object Coordinate System`
    - :mod:`ezdxf.upright` module

======================== ==========================================
Subclass of              :class:`ezdxf.entities.Circle`
DXF type                 ``'ARC'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_arc`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided
    factory functions!

.. class:: Arc

    .. attribute:: dxf.center

        Center point of arc (2D/3D Point in :ref:`OCS`)

    .. attribute:: dxf.radius

        Radius of arc (float)

    .. attribute:: dxf.start_angle

        Start angle in degrees (float)

    .. attribute:: dxf.end_angle

        End angle in degrees (float)

    .. autoattribute:: start_point

    .. autoattribute:: end_point

    .. automethod:: angles

    .. automethod:: flattening

    .. automethod:: transform

    .. automethod:: to_ellipse

    .. automethod:: to_spline

    .. automethod:: construction_tool

    .. automethod:: apply_construction_tool

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-0B14D8F1-0EBA-44BF-9108-57D8CE614BC8
