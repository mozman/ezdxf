Ellipse
=======

.. module:: ezdxf.entities
    :noindex:

The ELLIPSE (`DXF Reference`_) entity is a 3D curve defined by the
:attr:`dxf.center`, the :attr:`dxf.major_axis` vector and the
:attr:`dxf.extrusion` vector.

The :attr:`dxf.ratio` attribute is the ratio of minor axis to major axis and has
to be smaller or equal 1.  The :attr:`dxf.start_param` and :attr:`dxf.end_param`
attributes defines the starting- and the end point of the ellipse, a full
ellipse goes from 0 to 2*pi.  The curve always goes from start- to end
param in counter clockwise orientation.

The :attr:`dxf.extrusion` vector defines the normal vector of the ellipse plan.
The minor axis direction is calculated by :attr:`dxf.extrusion` cross
:attr:`dxf.major_axis`. The default extrusion vector (0, 0, 1) defines an ellipse
plane parallel to xy-plane of the :ref:`WCS`.

All coordinates and vectors in :ref:`WCS`.

.. seealso::

    - :ref:`tut_dxf_primitives`, section :ref:`tut_dxf_primitives_ellipse`
    - :class:`ezdxf.math.ConstructionEllipse`

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

        Endpoint of major axis, relative to the :attr:`dxf.center` (Vec3),
        default value is (1, 0, 0).

    .. attribute:: dxf.ratio

        Ratio of minor axis to major axis (float), has to be in range from
        0.000001 to 1.0, default value is 1.

    .. attribute:: dxf.start_param

        Start parameter (float), default value is 0.

    .. attribute:: dxf.end_param

        End parameter (float), default value is 2*pi.

    .. attribute:: start_point

        Returns the start point of the ellipse in WCS.

    .. attribute:: end_point

        Returns the end point of the ellipse in WCS.

    .. attribute:: minor_axis

        Returns the minor axis of the ellipse as :class:`Vec3` in WCS.

    .. automethod:: construction_tool

    .. automethod:: apply_construction_tool

    .. automethod:: vertices

    .. automethod:: flattening

    .. automethod:: params

    .. automethod:: transform

    .. automethod:: translate

    .. automethod:: to_spline

    .. automethod:: from_arc

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-107CB04F-AD4D-4D2F-8EC9-AC90888063AB