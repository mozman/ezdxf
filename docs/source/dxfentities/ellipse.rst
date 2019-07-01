Ellipse
=======

.. module:: ezdxf.entities

ELLIPSE (`DXF Reference`_) with center point at location :attr:`dxf.center` and a major axis :attr:`dxf.major_axis` as vector.
:attr:`dxf.ratio` is the ratio of minor axis to major axis. :attr:`dxf.start_param` and :attr:`dxf.end_param`
defines the starting- and the end point of the ellipse, a full ellipse goes from ``0`` to ``2*pi``.
The ellipse goes from starting- to end param in counter clockwise direction.

:attr:`dxf.extrusion` is supported, but does not establish an :ref:`OCS`, but creates an 3D entity by
extruding the base ellipse in direction of the :attr:`dxf.extrusion` vector.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'ELLIPSE'``
factory function         :meth:`~ezdxf.layouts.BaseLayout.add_ellipse`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. class:: Ellipse

    .. attribute:: dxf.center

        Center point of circle (2D/3D Point in :ref:`WCS`)

    .. attribute:: dxf.major_axis

        Endpoint of major axis, relative to the :attr:`dxf.center` (Vector), default value is ``(1, 0, 0)``.

    .. attribute:: dxf.ratio

        Ratio of minor axis to major axis (float), default value is ``1``.

    .. attribute:: dxf.start_param

        Start parameter (float), default value is ``0``.

    .. attribute:: dxf.end_param

        End parameter (float), default value is ``2*pi``.

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-107CB04F-AD4D-4D2F-8EC9-AC90888063AB