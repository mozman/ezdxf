Add DXF Entities
================

Layout Factory Methods
----------------------

Recommended way to create DXF entities.

For all supported entities exist at least one factory method in the
:class:`ezdxf.layouts.BaseLayout` class.
All factory methods have the prefix: ``add_...``

.. code-block:: Python

    import ezdxf

    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_line((0, 0, 0), (3, 0, 0), dxfattribs={"color": 2})

.. _thematic_factory_method_index:

Thematic Index of Layout Factory Methods
----------------------------------------

DXF Primitives
++++++++++++++

- :meth:`~ezdxf.layouts.BaseLayout.add_3dface`
- :meth:`~ezdxf.layouts.BaseLayout.add_arc`
- :meth:`~ezdxf.layouts.BaseLayout.add_circle`
- :meth:`~ezdxf.layouts.BaseLayout.add_ellipse`
- :meth:`~ezdxf.layouts.BaseLayout.add_hatch`
- :meth:`~ezdxf.layouts.BaseLayout.add_helix`
- :meth:`~ezdxf.layouts.BaseLayout.add_image`
- :meth:`~ezdxf.layouts.BaseLayout.add_leader`
- :meth:`~ezdxf.layouts.BaseLayout.add_line`
- :meth:`~ezdxf.layouts.BaseLayout.add_lwpolyline`
- :meth:`~ezdxf.layouts.BaseLayout.add_mesh`
- :meth:`~ezdxf.layouts.BaseLayout.add_mline`
- :meth:`~ezdxf.layouts.BaseLayout.add_mpolygon`
- :meth:`~ezdxf.layouts.BaseLayout.add_multileader_mtext`
- :meth:`~ezdxf.layouts.BaseLayout.add_multileader_block`
- :meth:`~ezdxf.layouts.BaseLayout.add_point`
- :meth:`~ezdxf.layouts.BaseLayout.add_polyface`
- :meth:`~ezdxf.layouts.BaseLayout.add_polyline2d`
- :meth:`~ezdxf.layouts.BaseLayout.add_polyline3d`
- :meth:`~ezdxf.layouts.BaseLayout.add_polymesh`
- :meth:`~ezdxf.layouts.BaseLayout.add_ray`
- :meth:`~ezdxf.layouts.BaseLayout.add_shape`
- :meth:`~ezdxf.layouts.BaseLayout.add_solid`
- :meth:`~ezdxf.layouts.BaseLayout.add_trace`
- :meth:`~ezdxf.layouts.BaseLayout.add_wipeout`
- :meth:`~ezdxf.layouts.BaseLayout.add_xline`

Text Entities
+++++++++++++

- :meth:`~ezdxf.layouts.BaseLayout.add_attdef`
- :meth:`~ezdxf.layouts.BaseLayout.add_mtext_dynamic_auto_height_columns`
- :meth:`~ezdxf.layouts.BaseLayout.add_mtext_dynamic_manual_height_columns`
- :meth:`~ezdxf.layouts.BaseLayout.add_mtext_static_columns`
- :meth:`~ezdxf.layouts.BaseLayout.add_mtext`
- :meth:`~ezdxf.layouts.BaseLayout.add_text`

Spline Entity
+++++++++++++

- :meth:`~ezdxf.layouts.BaseLayout.add_cad_spline_control_frame`
- :meth:`~ezdxf.layouts.BaseLayout.add_open_spline`
- :meth:`~ezdxf.layouts.BaseLayout.add_rational_spline`
- :meth:`~ezdxf.layouts.BaseLayout.add_spline_control_frame`
- :meth:`~ezdxf.layouts.BaseLayout.add_spline`

Block References and Underlays
++++++++++++++++++++++++++++++

- :meth:`~ezdxf.layouts.BaseLayout.add_arrow_blockref`
- :meth:`~ezdxf.layouts.BaseLayout.add_auto_blockref`
- :meth:`~ezdxf.layouts.BaseLayout.add_blockref`
- :meth:`~ezdxf.layouts.BaseLayout.add_underlay`

Viewport Entity
+++++++++++++++

Only available in paper space layouts.

- :meth:`~ezdxf.layouts.BaseLayout.add_viewport`

Dimension Entities
++++++++++++++++++

Linear Dimension

- :meth:`~ezdxf.layouts.BaseLayout.add_aligned_dim`
- :meth:`~ezdxf.layouts.BaseLayout.add_linear_dim`
- :meth:`~ezdxf.layouts.BaseLayout.add_multi_point_linear_dim`

Radius and Diameter Dimension

- :meth:`~ezdxf.layouts.BaseLayout.add_diameter_dim_2p`
- :meth:`~ezdxf.layouts.BaseLayout.add_diameter_dim`
- :meth:`~ezdxf.layouts.BaseLayout.add_radius_dim_2p`
- :meth:`~ezdxf.layouts.BaseLayout.add_radius_dim_cra`
- :meth:`~ezdxf.layouts.BaseLayout.add_radius_dim`

Angular Dimension

- :meth:`~ezdxf.layouts.BaseLayout.add_angular_dim_2l`
- :meth:`~ezdxf.layouts.BaseLayout.add_angular_dim_3p`
- :meth:`~ezdxf.layouts.BaseLayout.add_angular_dim_arc`
- :meth:`~ezdxf.layouts.BaseLayout.add_angular_dim_cra`

Arc Dimension

- :meth:`~ezdxf.layouts.BaseLayout.add_arc_dim_3p`
- :meth:`~ezdxf.layouts.BaseLayout.add_arc_dim_arc`
- :meth:`~ezdxf.layouts.BaseLayout.add_arc_dim_cra`

Ordinate Dimension

- :meth:`~ezdxf.layouts.BaseLayout.add_ordinate_dim`
- :meth:`~ezdxf.layouts.BaseLayout.add_ordinate_x_dim`
- :meth:`~ezdxf.layouts.BaseLayout.add_ordinate_y_dim`


Miscellaneous
+++++++++++++

- :meth:`~ezdxf.layouts.BaseLayout.add_entity`
- :meth:`~ezdxf.layouts.BaseLayout.add_foreign_entity`
- :meth:`~ezdxf.layouts.BaseLayout.add_arrow`

ACIS Entities
+++++++++++++

The creation of the required :term:`ACIS` data has do be done by an external library!

- :meth:`~ezdxf.layouts.BaseLayout.add_3dsolid`
- :meth:`~ezdxf.layouts.BaseLayout.add_body`
- :meth:`~ezdxf.layouts.BaseLayout.add_extruded_surface`
- :meth:`~ezdxf.layouts.BaseLayout.add_lofted_surface`
- :meth:`~ezdxf.layouts.BaseLayout.add_region`
- :meth:`~ezdxf.layouts.BaseLayout.add_revolved_surface`
- :meth:`~ezdxf.layouts.BaseLayout.add_surface`
- :meth:`~ezdxf.layouts.BaseLayout.add_swept_surface`

.. seealso::

    Layout base class: :class:`~ezdxf.layouts.BaseLayout`

Factory Functions
-----------------

Alternative way to create DXF entities for advanced `ezdxf` users.

The :mod:`ezdxf.entities.factory` module provides the
:func:`~ezdxf.entities.factory.new` function to create new DXF entities by
their DXF name and a dictionary of DXF attributes. This will bypass the
validity checks in the factory methods of the :class:`~ezdxf.layouts.BaseLayout`
class.

This new created entities are virtual entities which are not assigned to any
DXF document nor to any layout. Add the entity to a layout (and document) by
the layout method :meth:`~ezdxf.layouts.BaseLayout.add_entity`.

.. code-block:: Python

    import ezdxf
    from ezdxf.entities import factory

    doc = ezdxf.new()
    msp = doc.modelspace()
    line = factory.new(
        "LINE",
        dxfattribs={
            "start": (0, 0, 0),
            "end": (3, 0, 0),
            "color": 2,
        },
    )
    msp.add_entity(line)

Direct Object Instantiation
---------------------------

For advanced developers with knowledge about the internal design of `ezdxf`.

Import the entity classes from sub-package :mod:`ezdxf.entities` and instantiate
them. This will bypass the validity checks in the factory methods of the
:class:`~ezdxf.layouts.BaseLayout` class and maybe additional required setup
procedures for some entities - **study the source code!**.

.. warning::

    A refactoring of the internal `ezdxf` structures will break your code.

This new created entities are virtual entities which are not assigned to any
DXF document nor to any layout. Add the entity to a layout (and document) by
the layout method :meth:`~ezdxf.layouts.BaseLayout.add_entity`.

.. code-block:: Python

    import ezdxf
    from ezdxf.entities import Line

    doc = ezdxf.new()
    msp = doc.modelspace()
    line = Line.new(
        dxfattribs={
            "start": (0, 0, 0),
            "end": (3, 0, 0),
            "color": 2,
        }
    )
    msp.add_entity(line)
