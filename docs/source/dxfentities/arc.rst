Arc
===

.. module:: ezdxf.entities
    :noindex:

ARC (`DXF Reference`_) center at location :attr:`dxf.center` and radius of :attr:`dxf.radius` from :attr:`dxf.start_angle` to
:attr:`dxf.end_angle`. ARC goes always from :attr:`dxf.start_angle` to :attr:`dxf.end_angle` in counter clockwise
orientation around the :attr:`dxf.extrusion` vector, which is ``(0, 0, 1)`` by default and the usual case for 2D
arcs.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.Circle`
DXF type                 ``'ARC'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_arc`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
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

    .. autoattribute:: start_point

    .. autoattribute:: end_point

    .. automethod:: angles

    .. automethod:: flattening(sagitta: float) -> Iterable[Vector]

    .. automethod:: transform(m: Matrix44) -> Arc

    .. automethod:: to_ellipse(replace=True) -> Ellipse

    .. automethod:: to_spline(replace=True) -> Spline

    .. automethod:: construction_tool() -> ConstructionArc

    .. automethod:: apply_construction_tool(arc: ConstructionArc) -> Arc

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-0B14D8F1-0EBA-44BF-9108-57D8CE614BC8