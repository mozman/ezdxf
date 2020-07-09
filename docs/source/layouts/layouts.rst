.. include:: ../spline-links.inc

.. _layout:

Layout Types
============

.. module:: ezdxf.layouts
    :noindex:

A Layout represents and manages DXF entities, there are three different layout objects:

- :class:`Modelspace` is the common working space, containing basic drawing entities.
- :class:`Paperspace` is arrangement of objects for printing and plotting, this layout contains basic drawing entities
  and viewports to the :class:`Modelspace`.
- :class:`BlockLayout` works on an associated :class:`~ezdxf.entities.block.Block`, Blocks are collections of drawing
  entities for reusing by block references.

.. warning::

    Do not instantiate layout classes by yourself - always use the provided factory functions!

Entity Ownership
----------------

A layout owns all entities residing in their entity space, this means the :attr:`dxf.owner` attribute of
any :class:`~ezdxf.entities.dxfgfx.DXFGraphic` in this layout is the :attr:`dxf.handle` of the layout, and deleting
an entity from a layout is the end of life of this entity, because it is also deleted from the
:class:`~ezdxf.entitydb.EntityDB`.
But it is possible to just unlink an entity from a layout, so it can be assigned to another layout, use the
:meth:`~BaseLayout.move_to_layout` method to move entities between layouts.


BaseLayout
==========

.. class:: BaseLayout

    :class:`BaseLayout` is the common base class for :class:`Layout` and :class:`BlockLayout`.

    .. autoattribute:: is_alive

    .. autoattribute:: is_active_paperspace

    .. autoattribute:: is_any_paperspace

    .. autoattribute:: is_modelspace

    .. autoattribute:: is_any_layout

    .. autoattribute:: is_block_layout

    .. autoattribute:: units

    .. automethod:: __len__

    .. automethod:: __iter__

    .. automethod:: __getitem__

    .. automethod:: get_extension_dict

    .. automethod:: delete_entity

    .. automethod:: delete_all_entities

    .. automethod:: unlink_entity

    .. automethod:: query(query: str = '*') -> EntityQuery

    .. automethod:: groupby

    .. automethod:: move_to_layout

    .. automethod:: add_entity

    .. automethod:: add_foreign_entity

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

    .. automethod:: add_radius_dim

    .. automethod:: add_radius_dim_2p

    .. automethod:: add_radius_dim_cra

    .. automethod:: add_diameter_dim

    .. automethod:: add_diameter_dim_2p

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

    :class:`Layout` is a subclass of :class:`BaseLayout` and common base class of :class:`Modelspace` and
    :class:`Paperspace`.

    .. autoattribute:: name

    .. autoattribute:: dxf

    .. automethod:: __contains__

    .. automethod:: reset_extends

    .. automethod:: set_plot_type

    .. automethod:: set_plot_style

    .. automethod:: set_plot_window

    .. automethod:: set_redraw_order

    .. automethod:: get_redraw_order

    .. automethod:: plot_viewport_borders

    .. automethod:: show_plot_styles

    .. automethod:: plot_centered

    .. automethod:: plot_hidden

    .. automethod:: use_standard_scale

    .. automethod:: use_plot_styles

    .. automethod:: scale_lineweights

    .. automethod:: print_lineweights

    .. automethod:: draw_viewports_first

    .. automethod:: model_type

    .. automethod:: update_paper

    .. automethod:: zoom_to_paper_on_update

    .. automethod:: plot_flags_initializing

    .. automethod:: prev_plot_init

    .. automethod:: set_plot_flags

Modelspace
==========

.. class:: Modelspace

    :class:`Modelspace` is a subclass of :class:`Layout`.

    The modelspace contains the "real" world representation of the drawing subjects in real world units.

    .. autoattribute:: name

    .. automethod:: new_geodata

    .. automethod:: get_geodata

Paperspace
==========

.. class:: Paperspace

    :class:`Paperspace` is a subclass of :class:`Layout`.

    Paperspace layouts are used to create different drawing sheets of the modelspace subjects for printing or
    PDF export.

    .. autoattribute:: name

    .. automethod:: page_setup(size=(297, 210), margins=(10, 15, 10, 15), units='mm', offset=(0, 0), rotation=0, scale=16, name='ezdxf', device='DWG to PDF.pc3')

    .. automethod:: rename

    .. automethod:: viewports

    .. automethod:: add_viewport

    .. automethod:: reset_viewports

    .. automethod:: reset_paper_limits

    .. automethod:: get_paper_limits


BlockLayout
===========

.. class:: BlockLayout

    :class:`BlockLayout` is a subclass of :class:`BaseLayout`.

    Block layouts are reusable sets of graphical entities, which can be referenced by multiple
    :class:`~ezdxf.entities.Insert` entities. Each reference can be placed, scaled and rotated individually and can
    have it's own set of DXF :class:`~ezdxf.entities.Attrib` entities attached.

    .. attribute:: name

       name of the associated BLOCK and BLOCK_RECORD entities.

    .. autoattribute:: block

    .. autoattribute:: endblk

    .. autoattribute:: dxf

    .. autoattribute:: can_explode

    .. autoattribute:: scale_uniformly

    .. automethod:: __contains__

    .. automethod:: attdefs

    .. automethod:: has_attdef

    .. automethod:: get_attdef

    .. automethod:: get_attdef_text

