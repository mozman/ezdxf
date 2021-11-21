ArcDimension
============

.. module:: ezdxf.entities
    :noindex:

The ARC_DIMENSION entity was introduced in DXF R2004 and is **not** documented
in the DXF reference.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.Dimension`
DXF type                 ``'ARC_DIMENSION'``
factory function         - :meth:`~ezdxf.layouts.BaseLayout.add_arc_dim_3p`
                         - :meth:`~ezdxf.layouts.BaseLayout.add_arc_dim_cra`
                         - :meth:`~ezdxf.layouts.BaseLayout.add_arc_dim_arc`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2004 (``'AC1018'``)
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided
    factory functions!

.. class:: ArcDimension

    .. attribute:: dxf.ext_line1_point

    .. attribute:: dxf.ext_line2_point

    .. attribute:: dxf.arc_center

    .. attribute:: dxf.start_angle

    .. attribute:: dxf.end_angle

    .. attribute:: dxf.is_partial

    .. attribute:: dxf.has_leader

    .. attribute:: dxf.leader_point1

    .. attribute:: dxf.leader_point2

    .. attribute:: dimtype

        Returns always ``8``.
