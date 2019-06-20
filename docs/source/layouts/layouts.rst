.. _layout:

Layout Types
============

.. module:: ezdxf.layouts

A Layout represents and manages DXF entities, there are three different layout objects:

- :class:`Modelspace` is the common working space, containing basic drawing entities.
- :class:`Paperspace` is arrangement of objects for printing and plotting, this layout contains basic drawing entities
  and viewports to the :class:`Modelspace`.
- :class:`BlockLayout` works on an associated :class:`~ezdxf.entities.block.Block`, Blocks are collections of drawing
  entities for reusing by block references.

.. warning::

    Do not instantiate layout classes by yourself - always use the provided factory functions!

BaseLayout
==========

.. class:: BaseLayout

    :class:`BaseLayout` is the common base class for :class:`Layout` and :class:`BlockLayout`.

    .. automethod:: add_point

    .. automethod:: add_line

    .. automethod:: add_circle

    .. automethod:: add_ellipse

    .. automethod:: add_arc

    .. automethod:: add_solid

    .. automethod:: add_trace

    .. automethod:: add_3dface

    .. automethod:: add_text

    .. automethod:: add_blockref

    .. automethod:: add_auto_blockref

    .. automethod:: add_attrib

    .. automethod:: add_attdef

    .. automethod:: add_polyline2d

    .. automethod:: add_polyline3d

    .. automethod:: add_polymesh

    .. automethod:: add_polyface

    .. automethod:: add_shape

    .. automethod:: add_lwpolyline

    .. automethod:: add_mtext

    .. automethod:: add_ray

    .. automethod:: add_xline

    .. automethod:: add_spline

    .. automethod:: add_spline_control_frame

    .. automethod:: add_spline_approx

    .. automethod:: add_open_spline

    .. automethod:: add_closed_spline

    .. automethod:: add_rational_spline

    .. automethod:: add_closed_rational_spline

    .. automethod:: add_hatch

    .. automethod:: add_mesh

    .. automethod:: add_image

    .. automethod:: add_underlay

    .. automethod:: add_linear_dim

    .. automethod:: add_multi_point_linear_dim

    .. automethod:: add_aligned_dim

    .. automethod:: add_leader

    .. automethod:: add_body

    .. automethod:: add_region

    .. automethod:: add_3dsolid

    .. automethod:: add_surface

    .. automethod:: add_extruded_surface

    .. automethod:: add_lofted_surface

    .. automethod:: add_revolved_surface

    .. automethod:: add_swept_surface

Layout
======

.. class:: Layout

    :class:`Layout` is a subclass of :class:`BaseLayout`.

    .. automethod:: Layout.__iter__

    .. automethod:: __len__

    .. automethod:: __contains__

    .. automethod:: query

    .. automethod:: groupby

    .. automethod:: add_entity

    .. automethod:: unlink_entity

    .. automethod:: delete_entity

    .. automethod:: page_setup

    .. automethod:: reset_viewports

    .. automethod:: reset_extends

    .. automethod:: reset_paper_limits

    .. automethod:: get_paper_limits

    .. automethod:: set_plot_type

    .. automethod:: set_plot_style

    .. automethod:: set_plot_window

    .. automethod:: set_redraw_order

    .. automethod:: get_redraw_order

    .. automethod:: Layout.new_geodata

    .. automethod:: Layout.get_geodata


.. _model space:

Model Space
===========

   At this time the :class:`Modelspace` class is the :class:`Layout` class.


.. _paper space:

Paper Space
===========

   At this time the :class:`Paperspace` class is the :class:`Layout` class.

.. _block layout:

BlockLayout
===========

.. class:: BlockLayout

    :class:`BlockLayout` is a subclass of :class:`BaseLayout`.

    .. attribute:: name

       The name of the associated block element. (read/write)

    .. attribute:: block

       Get the associated DXF *BLOCK* entity.

    .. attribute:: is_layout_block

        True if block is a model space or paper space block definition.

    .. automethod:: attdefs

    .. automethod:: has_attdef

    .. automethod:: get_attdef

    .. automethod:: get_attdef_text
