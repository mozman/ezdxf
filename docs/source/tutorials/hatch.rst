.. _tut_hatch:

Tutorial for Hatch
==================

Create hatches with one boundary path
-------------------------------------

The simplest form of a hatch has one polyline path with only straight lines as boundary path:

.. literalinclude:: ../../../examples/tut/hatch/solid_hatch_polyline_path.py

But like all polyline entities the polyline path can also have bulge values:

.. literalinclude:: ../../../examples/tut/hatch/solid_hatch_polyline_path_with_bulge.py

The most flexible way to define a boundary path is the edge path. An edge path consist of a number of edges and
each edge can be one of the following elements:

    - line :meth:`EdgePath.add_line`
    - arc :meth:`EdgePath.add_arc`
    - ellipse :meth:`EdgePath.add_ellipse`
    - spline :meth:`EdgePath.add_spline`

Create a solid hatch with an edge path (ellipse) as boundary path:

.. literalinclude:: ../../../examples/tut/hatch/solid_hatch_ellipse.py

Create hatches with multiple boundary paths (islands)
-----------------------------------------------------

TODO

Create hatches with with pattern fill
-------------------------------------

TODO

Create hatches with gradient fill
---------------------------------

TODO