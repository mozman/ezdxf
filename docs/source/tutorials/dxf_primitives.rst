.. _tut_dxf_primitives:

Tutorial for Simple DXF Entities
================================

These are basic graphical entities located in an entity space like
the modelspace or a block definition and only support the common graphical
attributes.

The entities in the following examples are always placed in the xy-plane of the
:ref:`WCS` aka the 2D drawing space.
Some of these entities can only be placed outside the xy-plane in 3D space by
utilizing the :ref:`OCS`, but this feature is beyond the scope of this tutorial,
for more information about that go to: :ref:`tut_ocs`.

Prelude to all following examples::

    import ezdxf
    from ezdxf.gfxattribs import GfxAttribs

    doc = ezdxf.new()
    doc.layers.new("ENTITY", color=1)
    msp = doc.modelspace()
    attribs = GfxAttribs(layer="ENTITY")

.. seealso::

    - :ref:`tut_simple_drawings`
    - :ref:`tut_layers`
    - :mod:`ezdxf.gfxattribs` module

.. _tut_dxf_primitives_point:

Point
-----

The :class:`~ezdxf.entities.Point` entity marks a 3D point in the :ref:`WCS`::

    point = msp.add_point((10, 10), dxfattribs=attribs)

All :class:`~ezdxf.entities.Point` entities have the same styling stored in the
header variable $PDMODE, for more information read the reference of class
:class:`~ezdxf.entities.Point`.

.. seealso::

    - Reference of class :class:`~ezdxf.entities.Point`
    - :ref:`tut_common_graphical_attributes`

.. _tut_dxf_primitives_line:

Line
----

The :class:`~ezdxf.entities.Line` entity is a 3D line with a start- and
an end point in the :ref:`WCS`::

    line = msp.add_line((0, 0), (10, 10), dxfattribs=attribs)

.. seealso::

    - Reference of class :class:`~ezdxf.entities.Line`
    - :ref:`tut_common_graphical_attributes`
    - :class:`ezdxf.math.ConstructionLine`

.. _tut_dxf_primitives_circle:

Circle
------

The :class:`~ezdxf.entities.Circle` entity is an :ref:`OCS` entity defined by a
center point and a radius::

    circle = msp.add_circle((10, 10), radius=3, dxfattribs=attribs)


.. seealso::

    - Reference of class :class:`~ezdxf.entities.Circle`
    - :ref:`tut_common_graphical_attributes`
    - :class:`ezdxf.math.ConstructionCircle`

.. _tut_dxf_primitives_arc:

Arc
---

The :class:`~ezdxf.entities.Arc` entity is an :ref:`OCS` entity defined by a
center point, a radius a start-  and an end angle in degrees::

    arc = msp.add_arc((10, 10), radius=3, start_angle=30, end_angle=120, dxfattribs=attribs)

The arc goes always in counter-clockwise orientation around the z-axis more
precisely the extrusion vector of :ref:`OCS`, but this is beyond the scope of
this tutorial.

The helper class :class:`ezdxf.math.ConstructionArc` provides constructors to
create arcs from different scenarios:

- :class:`~ezdxf.math.ConstructionArc.from_2p_angle`: arc from 2 points and an angle
- :class:`~ezdxf.math.ConstructionArc.from_2p_radius`: arc from 2 points and a radius
- :class:`~ezdxf.math.ConstructionArc.from_3p`: arc from 3 points

This example creates an arc from point (10, 0) to point (0, 0) passing the
point (5, 3):

.. code-block:: Python

    from ezdxf.math import ConstructionArc

    # -x-x-x- snip -x-x-x-

    arc = ConstructionArc.from_3p(
        start_point=(10, 0), end_point=(0, 0), def_point=(5, 3)
    )
    arc.add_to_layout(msp, dxfattribs=attribs)

.. seealso::

    - Reference of class :class:`~ezdxf.entities.Arc`
    - :ref:`tut_common_graphical_attributes`
    - :class:`ezdxf.math.ConstructionArc`

.. _tut_dxf_primitives_ellipse:

Ellipse
-------

The :class:`~ezdxf.entities.Ellipse` entity requires DXF R2000 or newer and is a
true :ref:`WCS` entity. The ellipse is defined by a center point, a vector for
the major axis, the ratio between major- and minor axis and the start- and end
parameter in radians::

    ellipse = msp.add_ellipse(
        (10, 10), major_axis=(5, 0), ratio=0.5, start_param=0, end_param=math.pi, dxfattribs=attribs
    )


When placed in 3D space the extrusion vector defines the normal vector of the
ellipse plane and the minor axis is the extrusion vector ``cross`` the major axis.


.. seealso::

    - Reference of class :class:`~ezdxf.entities.Ellipse`
    - :ref:`tut_common_graphical_attributes`
    - :class:`ezdxf.math.ConstructionEllipse`


Further Tutorials
-----------------

- :ref:`tut_lwpolyline`
- :ref:`tut_spline`
- :ref:`tut_text`
- :ref:`tut_mtext`
- :ref:`tut_hatch`
- :ref:`tut_mleader`
- :ref:`tut_mesh`
