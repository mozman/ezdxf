Spline
======

.. module:: ezdxf.entities
    :noindex:

SPLINE curve (`DXF Reference`_), all coordinates have to be 3D coordinates even
the spline is only a 2D planar curve.

The spline curve is defined by control points, knot values and weights. The
control points establish the spline, the various types of knot vector determines
the shape of the curve and the weights of rational splines define how
strong a control point influences the shape.

To create a :class:`Spline` curve you just need a bunch of fit points - knot
values and weights are optional (tested with AutoCAD 2010). If you add
additional data, be sure that you know what you do.

.. versionadded:: 0.16

    The function :func:`ezdxf.math.fit_points_to_cad_cv` calculates control
    vertices from given fit points. This control vertices define a cubic
    B-spline which matches visually the SPLINE entities created by BricsCAD and
    AutoCAD from fit points.

.. seealso::

    - `Wikipedia`_ article about B_splines
    - Department of Computer Science and Technology at the `Cambridge`_ University
    - :ref:`tut_spline`


======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'SPLINE'``
Factory function         see table below
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

Factory Functions
-----------------

=========================================== ==========================================
Basic spline entity                         :meth:`~ezdxf.layouts.BaseLayout.add_spline`
Spline control frame from fit points        :meth:`~ezdxf.layouts.BaseLayout.add_spline_control_frame`
Open uniform spline                         :meth:`~ezdxf.layouts.BaseLayout.add_open_spline`
Closed uniform spline                       :meth:`~ezdxf.layouts.BaseLayout.add_closed_spline`
Open rational uniform spline                :meth:`~ezdxf.layouts.BaseLayout.add_rational_spline`
Closed rational uniform spline              :meth:`~ezdxf.layouts.BaseLayout.add_closed_rational_spline`
=========================================== ==========================================

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-E1F884F8-AA90-4864-A215-3182D47A9C74

.. class:: Spline

    All points in :ref:`WCS` as (x, y, z) tuples

    .. attribute:: dxf.degree

        Degree of the spline curve (int).

    .. attribute:: dxf.flags

        Bit coded option flags, constants defined in :mod:`ezdxf.lldxf.const`:

        =================== ======= ===========
        dxf.flags           Value   Description
        =================== ======= ===========
        CLOSED_SPLINE       1       Spline is closed
        PERIODIC_SPLINE     2
        RATIONAL_SPLINE     4
        PLANAR_SPLINE       8
        LINEAR_SPLINE       16      planar bit is also set
        =================== ======= ===========

    .. attribute:: dxf.n_knots

        Count of knot values (int), automatically set by `ezdxf` (read only)

    .. attribute:: dxf.n_fit_points

        Count of fit points (int), automatically set by ezdxf (read only)

    .. attribute:: dxf.n_control_points

        Count of control points (int), automatically set by ezdxf (read only)

    .. attribute:: dxf.knot_tolerance

        Knot tolerance (float); default = ``1e-10``

    .. attribute:: dxf.fit_tolerance

        Fit tolerance (float); default = ``1e-10``

    .. attribute:: dxf.control_point_tolerance

        Control point tolerance (float); default = ``1e-10``

    .. attribute:: dxf.start_tangent

        Start tangent vector as (3D vector in :ref:`WCS`)

    .. attribute:: dxf.end_tangent

        End tangent vector as (3D vector in :ref:`WCS`)

    .. autoattribute:: closed

    .. autoattribute:: control_points

    .. autoattribute:: fit_points

    .. autoattribute:: knots

    .. autoattribute:: weights

    .. automethod:: control_point_count

    .. automethod:: fit_point_count

    .. automethod:: knot_count

    .. automethod:: construction_tool

    .. automethod:: apply_construction_tool

    .. automethod:: flattening

    .. automethod:: set_open_uniform

    .. automethod:: set_uniform

    .. automethod:: set_closed

    .. automethod:: set_open_rational

    .. automethod:: set_uniform_rational

    .. automethod:: set_closed_rational

    .. automethod:: transform

    .. automethod:: from_arc

.. _Cambridge: https://www.cl.cam.ac.uk/teaching/2000/AGraphHCI/SMEG/node4.html

.. _Wikipedia: https://en.wikipedia.org/wiki/Spline_%28mathematics%29
