.. _tut_hatch:

Tutorial for Hatch
==================

Create hatches with one boundary path
-------------------------------------

The simplest form of the :class:`~ezdxf.entities.Hatch` entity has one polyline
path with only straight lines as boundary path:

.. literalinclude:: src/hatch/solid_hatch_polyline_path.py

But like all polyline entities the polyline path can also have bulge values:

.. literalinclude:: src/hatch/solid_hatch_polyline_path_with_bulge.py

The most flexible way to define a boundary path is the edge path. An edge path
can have multiple edges and each edge can be one of the following elements:

    - line :meth:`EdgePath.add_line`
    - arc :meth:`EdgePath.add_arc`
    - ellipse :meth:`EdgePath.add_ellipse`
    - spline :meth:`EdgePath.add_spline`

Create a solid hatch with an edge path (ellipse) as boundary path:

.. literalinclude:: src/hatch/solid_hatch_ellipse.py

Create hatches with multiple boundary paths (islands)
-----------------------------------------------------

The DXF attribute :attr:`hatch_style` defines the island detection style:

=== ========================================================
0   nested - altering filled and unfilled areas
1   outer - area between `external` and `outermost` path is filled
2   ignore - `external` path is filled
=== ========================================================

.. literalinclude:: src/hatch/solid_hatch_islands.py
    :lines: 11-27

This is also the result for all 4 paths and :attr:`hatch_style` set to ``2``
(ignore).

.. image:: gfx/hatch-island-01.png
    :align: center

.. literalinclude:: src/hatch/solid_hatch_islands.py
    :lines: 31-36

This is also the result for all 4 paths and :attr:`hatch_style` set to ``1``
(outer).

.. image:: gfx/hatch-island-02.png
    :align: center

.. literalinclude:: src/hatch/solid_hatch_islands.py
    :lines: 40-45

.. image:: gfx/hatch-island-03.png
    :align: center

.. literalinclude:: src/hatch/solid_hatch_islands.py
    :lines: 49-56

.. image:: gfx/hatch-island-04.png
    :align: center

The expected result of combinations of various :attr:`hatch_style` values and
paths `flags`, or the handling of overlapping paths is not documented by the
DXF reference, so don't ask me, ask Autodesk or just try it by yourself
and post your experience in the forum.

Example for Edge Path Boundary
------------------------------

.. literalinclude:: src/hatch/edge_path.py
    :lines: 8-56

.. image:: gfx/hatch-edge-path.png
    :align: center

Associative Boundary Paths
--------------------------

A HATCH entity can be associative to a base geometry, which means if the base
geometry is edited in a CAD application the HATCH get the same modification.
Because `ezdxf` is **not** a CAD application, this association is **not**
maintained nor verified by `ezdxf`, so if you modify the base geometry
afterwards the geometry of the boundary path is not updated and no verification
is done to check if the associated geometry matches the boundary path, this
opens many possibilities to create invalid DXF files: USE WITH CARE.

This example associates a LWPOLYLINE entity to the hatch created from the
LWPOLYLINE vertices:

.. literalinclude:: src/hatch/assoc_hatch.py
    :lines: 8-24

An :class:`EdgePath` needs associations to all geometry entities forming the
boundary path.

Predefined Hatch Pattern
------------------------

Use predefined hatch pattern by name:

.. code-block:: Python

    hatch.set_pattern_fill("ANSI31", scale=0.5)


.. image:: gfx/hatch-predefined-pattern.png
    :align: center

Load Hatch Patterns From File
-----------------------------

CAD applications store the hatch patterns in pattern files with the file extension 
``.pat``. The following script shows how to load and use these pattern files:

.. code-block:: Python

    from ezdxf.tools import pattern

    EXAMPLE = """; a pattern file

    *SOLID, Solid fill
    45, 0,0, 0,.125
    *ANSI31, ANSI Iron, Brick, Stone masonry
    45, 0,0, 0,.125
    *ANSI32, ANSI Steel
    45, 0,0, 0,.375
    45, .176776695,0, 0,.375
    *ANSI33, ANSI Bronze, Brass, Copper
    45, 0,0, 0,.25
    45, .176776695,0, 0,.25, .125,-.0625
    *ANSI34, ANSI Plastic, Rubber
    45, 0,0, 0,.75
    45, .176776695,0, 0,.75
    45, .353553391,0, 0,.75
    45, .530330086,0, 0,.75
    """

    hatch = msp.add_hatch()
    # load your pattern file from the file system as string:
    # with open("pattern_file.pat", "rt") as fp:
    #      EXAMPLE = fp.read()
    patterns = pattern.parse(EXAMPLE)

    hatch.set_pattern_fill(
        "MyPattern",
        color=7,
        angle=0,  # the overall rotation of the pattern in degrees
        scale=1.0,  # overall scaling of the pattern
        style=0,  # normal hatching style
        pattern_type=0,  # user-defined
        # pattern name without the preceding asterisk
        definition=patterns["ANSI34"],  
    )
    points = [(0, 0), (10, 0), (10, 10), (0, 10)]
    hatch.paths.add_polyline_path(points)
    msp.add_lwpolyline(points, close=True, dxfattribs={"color": 1})


.. seealso::

    :ref:`tut_hatch_pattern`
