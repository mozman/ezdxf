.. _layout:

Layout
======

A Layout represents and manages drawing entities, there are three different
layout objects:

- Model space is the common working space, containing basic drawing entities.
- Paper spaces are arrangements of objects for printing and plotting,
  this layouts contains basic drawing entities and viewports to the model-space.
- BlockLayout works on an associated :class:`Block`, Blocks are
  collections of drawing entities for reusing by block references.

Paper Space Layout Setup
------------------------

.. class:: Layout

.. automethod:: ezdxf.modern.layouts.Layout.page_setup

.. automethod:: ezdxf.modern.layouts.Layout.reset_viewports

.. automethod:: ezdxf.modern.layouts.Layout.reset_extends

.. automethod:: ezdxf.modern.layouts.Layout.reset_paper_limits

.. automethod:: ezdxf.modern.layouts.Layout.get_paper_limits

.. automethod:: ezdxf.modern.layouts.Layout.set_plot_type

.. automethod:: ezdxf.modern.layouts.Layout.set_plot_style

.. automethod:: ezdxf.modern.layouts.Layout.set_plot_window

Access Existing Entities
------------------------

.. automethod:: ezdxf.modern.layouts.Layout.__iter__

.. automethod:: ezdxf.modern.layouts.Layout.__len__

.. automethod:: ezdxf.modern.layouts.Layout.__contains__

.. automethod:: ezdxf.modern.layouts.Layout.query

.. automethod:: ezdxf.modern.layouts.Layout.groupby

.. _Entity Factory Functions:

Create New Entities
-------------------

.. automethod:: ezdxf.modern.layouts.Layout.add_point

.. automethod:: ezdxf.modern.layouts.Layout.add_line

.. automethod:: ezdxf.modern.layouts.Layout.add_circle

.. automethod:: ezdxf.modern.layouts.Layout.add_ellipse

.. automethod:: ezdxf.modern.layouts.Layout.add_arc

.. automethod:: ezdxf.modern.layouts.Layout.add_solid

.. automethod:: ezdxf.modern.layouts.Layout.add_trace

.. automethod:: ezdxf.modern.layouts.Layout.add_3dface

.. automethod:: ezdxf.modern.layouts.Layout.add_text

.. automethod:: ezdxf.modern.layouts.Layout.add_blockref

.. automethod:: ezdxf.modern.layouts.Layout.add_auto_blockref

.. automethod:: ezdxf.modern.layouts.Layout.add_attrib

.. automethod:: ezdxf.modern.layouts.Layout.add_polyline2d

.. automethod:: ezdxf.modern.layouts.Layout.add_polyline3d

.. automethod:: ezdxf.modern.layouts.Layout.add_polymesh

.. automethod:: ezdxf.modern.layouts.Layout.add_polyface

.. automethod:: ezdxf.modern.layouts.Layout.add_shape

.. automethod:: ezdxf.modern.layouts.Layout.add_lwpolyline

.. automethod:: ezdxf.modern.layouts.Layout.add_mtext

.. automethod:: ezdxf.modern.layouts.Layout.add_ray

.. automethod:: ezdxf.modern.layouts.Layout.add_xline

.. automethod:: ezdxf.modern.layouts.Layout.add_spline

.. automethod:: ezdxf.modern.layouts.Layout.add_spline_control_frame

.. automethod:: ezdxf.modern.layouts.Layout.add_spline_approx

.. automethod:: ezdxf.modern.layouts.Layout.add_open_spline

.. automethod:: ezdxf.modern.layouts.Layout.add_closed_spline

.. automethod:: ezdxf.modern.layouts.Layout.add_rational_spline

.. automethod:: ezdxf.modern.layouts.Layout.add_closed_rational_spline

.. automethod:: ezdxf.modern.layouts.Layout.add_hatch

.. automethod:: ezdxf.modern.layouts.Layout.add_mesh

.. automethod:: ezdxf.modern.layouts.Layout.add_image

.. automethod:: ezdxf.modern.layouts.Layout.add_underlay

.. automethod:: ezdxf.modern.layouts.Layout.add_linear_dim

.. automethod:: ezdxf.modern.layouts.Layout.add_multi_point_linear_dim

.. automethod:: ezdxf.modern.layouts.Layout.add_aligned_dim

.. automethod:: ezdxf.modern.layouts.Layout.add_body

.. automethod:: ezdxf.modern.layouts.Layout.add_region

.. automethod:: ezdxf.modern.layouts.Layout.add_3dsolid

.. automethod:: ezdxf.modern.layouts.Layout.add_surface

.. automethod:: ezdxf.modern.layouts.Layout.add_extruded_surface

.. automethod:: ezdxf.modern.layouts.Layout.add_lofted_surface

.. automethod:: ezdxf.modern.layouts.Layout.add_revolved_surface

.. automethod:: ezdxf.modern.layouts.Layout.add_swept_surface

Change Redraw Order
-------------------

.. automethod:: ezdxf.modern.layouts.Layout.set_redraw_order

.. automethod:: ezdxf.modern.layouts.Layout.get_redraw_order


Delete Entities
---------------

.. automethod:: ezdxf.modern.layouts.Layout.add_entity

.. automethod:: ezdxf.modern.layouts.Layout.unlink_entity

.. automethod:: ezdxf.modern.layouts.Layout.delete_entity

.. _model space:

Model Space
===========

   At this time the :class:`Modelspace` class is the :class:`Layout` class.

.. automethod:: ezdxf.modern.layouts.Layout.new_geodata

.. automethod:: ezdxf.modern.layouts.Layout.get_geodata

.. _paper space:

Paper Space
===========

   At this time the :class:`Paperspace` class is the :class:`Layout` class.

.. _block layout:

BlockLayout
===========

.. class:: BlockLayout(Layout)

.. attribute:: BlockLayout.name

   The name of the associated block element. (read/write)

.. attribute:: BlockLayout.block

   Get the associated DXF *BLOCK* entity.

.. attribute:: BlockLayout.is_layout_block

    True if block is a model space or paper space block definition.

.. automethod:: ezdxf.modern.layouts.BlockLayout.add_attdef

.. automethod:: ezdxf.modern.layouts.BlockLayout.attdefs

.. automethod:: ezdxf.modern.layouts.BlockLayout.has_attdef

.. automethod:: ezdxf.modern.layouts.BlockLayout.get_attdef

.. automethod:: ezdxf.modern.layouts.BlockLayout.get_attdef_text


