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

.. automethod:: ezdxf.layouts.layout.Layout.page_setup

.. automethod:: ezdxf.layouts.layout.Layout.reset_viewports

.. automethod:: ezdxf.layouts.layout.Layout.reset_extends

.. automethod:: ezdxf.layouts.layout.Layout.reset_paper_limits

.. automethod:: ezdxf.layouts.layout.Layout.get_paper_limits

.. automethod:: ezdxf.layouts.layout.Layout.set_plot_type

.. automethod:: ezdxf.layouts.layout.Layout.set_plot_style

.. automethod:: ezdxf.layouts.layout.Layout.set_plot_window

Access Existing Entities
------------------------

.. automethod:: ezdxf.layouts.layout.Layout.__iter__

.. automethod:: ezdxf.layouts.layout.Layout.__len__

.. automethod:: ezdxf.layouts.layout.Layout.__contains__

.. automethod:: ezdxf.layouts.layout.Layout.query

.. automethod:: ezdxf.layouts.layout.Layout.groupby

.. _Entity Factory Functions:

Create New Entities
-------------------

.. automethod:: ezdxf.layouts.layout.Layout.add_point

.. automethod:: ezdxf.layouts.layout.Layout.add_line

.. automethod:: ezdxf.layouts.layout.Layout.add_circle

.. automethod:: ezdxf.layouts.layout.Layout.add_ellipse

.. automethod:: ezdxf.layouts.layout.Layout.add_arc

.. automethod:: ezdxf.layouts.layout.Layout.add_solid

.. automethod:: ezdxf.layouts.layout.Layout.add_trace

.. automethod:: ezdxf.layouts.layout.Layout.add_3dface

.. automethod:: ezdxf.layouts.layout.Layout.add_text

.. automethod:: ezdxf.layouts.layout.Layout.add_blockref

.. automethod:: ezdxf.layouts.layout.Layout.add_auto_blockref

.. automethod:: ezdxf.layouts.layout.Layout.add_attrib

.. automethod:: ezdxf.layouts.layout.Layout.add_polyline2d

.. automethod:: ezdxf.layouts.layout.Layout.add_polyline3d

.. automethod:: ezdxf.layouts.layout.Layout.add_polymesh

.. automethod:: ezdxf.layouts.layout.Layout.add_polyface

.. automethod:: ezdxf.layouts.layout.Layout.add_shape

.. automethod:: ezdxf.layouts.layout.Layout.add_lwpolyline

.. automethod:: ezdxf.layouts.layout.Layout.add_mtext

.. automethod:: ezdxf.layouts.layout.Layout.add_ray

.. automethod:: ezdxf.layouts.layout.Layout.add_xline

.. automethod:: ezdxf.layouts.layout.Layout.add_spline

.. automethod:: ezdxf.layouts.layout.Layout.add_spline_control_frame

.. automethod:: ezdxf.layouts.layout.Layout.add_spline_approx

.. automethod:: ezdxf.layouts.layout.Layout.add_open_spline

.. automethod:: ezdxf.layouts.layout.Layout.add_closed_spline

.. automethod:: ezdxf.layouts.layout.Layout.add_rational_spline

.. automethod:: ezdxf.layouts.layout.Layout.add_closed_rational_spline

.. automethod:: ezdxf.layouts.layout.Layout.add_hatch

.. automethod:: ezdxf.layouts.layout.Layout.add_mesh

.. automethod:: ezdxf.layouts.layout.Layout.add_image

.. automethod:: ezdxf.layouts.layout.Layout.add_underlay

.. automethod:: ezdxf.layouts.layout.Layout.add_linear_dim

.. automethod:: ezdxf.layouts.layout.Layout.add_multi_point_linear_dim

.. automethod:: ezdxf.layouts.layout.Layout.add_aligned_dim

.. automethod:: ezdxf.layouts.layout.Layout.add_leader

.. automethod:: ezdxf.layouts.layout.Layout.add_body

.. automethod:: ezdxf.layouts.layout.Layout.add_region

.. automethod:: ezdxf.layouts.layout.Layout.add_3dsolid

.. automethod:: ezdxf.layouts.layout.Layout.add_surface

.. automethod:: ezdxf.layouts.layout.Layout.add_extruded_surface

.. automethod:: ezdxf.layouts.layout.Layout.add_lofted_surface

.. automethod:: ezdxf.layouts.layout.Layout.add_revolved_surface

.. automethod:: ezdxf.layouts.layout.Layout.add_swept_surface

Change Redraw Order
-------------------

.. automethod:: ezdxf.layouts.layout.Layout.set_redraw_order

.. automethod:: ezdxf.layouts.layout.Layout.get_redraw_order


Delete Entities
---------------

.. automethod:: ezdxf.layouts.layout.Layout.add_entity

.. automethod:: ezdxf.layouts.layout.Layout.unlink_entity

.. automethod:: ezdxf.layouts.layout.Layout.delete_entity

.. _model space:

Model Space
===========

   At this time the :class:`Modelspace` class is the :class:`Layout` class.

.. automethod:: ezdxf.layouts.layout.Layout.new_geodata

.. automethod:: ezdxf.layouts.layout.Layout.get_geodata

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

.. automethod:: ezdxf.layouts.blocklayout.BlockLayout.add_attdef

.. automethod:: ezdxf.layouts.blocklayout.BlockLayout.attdefs

.. automethod:: ezdxf.layouts.blocklayout.BlockLayout.has_attdef

.. automethod:: ezdxf.layouts.blocklayout.BlockLayout.get_attdef

.. automethod:: ezdxf.layouts.blocklayout.BlockLayout.get_attdef_text


