.. module:: ezdxf.math
    :noindex:

.. _tut_coordinates:

.. _tut_ocs:

Tutorial for OCS/UCS Usage
==========================

For OCS/UCS usage is a basic understanding of vectors required, for a brush up watch the YouTube tutorials of
`3Blue1Brown`_ about `Linear Algebra`_.

Second read the :ref:`Coordinate Systems` introduction please.


For :ref:`WCS` there is not much to say as, it is what it is: the main world coordinate system, and a drawing unit can
have any real world unit you want. Autodesk added some mechanism to define a scale for dimension and text entities, but
because I am not an AutoCAD user, I am not familiar with it, and further more I think this is more an AutoCAD topic than
a DXF topic.

Object Coordinate System (OCS)
------------------------------

The :ref:`OCS` is used to place planar 2D entities in 3D space. **ALL** points of a planar entity lay in the same plane,
this is also true if the plane is located in 3D space by an OCS. There are three basic DXF attributes that gives a 2D
entity its spatial form.

Extrusion
~~~~~~~~~

The extrusion vector defines the OCS, it is a normal vector to the base plane of a planar entity. This `base plane` is
always located in the origin of the :ref:`WCS`. But there are some entities like :class:`~ezdxf.entities.Ellipse`,
which have an extrusion vector, but do not establish an OCS. For this entities the extrusion vector defines
only the extrusion direction and thickness defines the extrusion distance, but all other points in WCS.

Elevation
~~~~~~~~~

The elevation value defines the z-axis value for all points of a planar entity, this is an OCS value, and defines
the distance of the entity plane from the `base plane`.

This value exists only in output from DXF versions prior to R11 as separated DXF attribute (group code 38).
In DXF R12 and later, the elevation value is supplied as z-axis value of each point. But as always in DXF, this
simple rule does not apply to all entities: :class:`~ezdxf.entities.LWPolyline` and :class:`~ezdxf.entities.Hatch`
have an DXF attribute :attr:`elevation`, where the z-axis of this point is the elevation height and
the x-axis = y-axis = ``0``.

Thickness
~~~~~~~~~

Defines the extrusion distance for an entity.

Placing 2D Circle in 3D Space
-----------------------------

The colors for axis follow the AutoCAD standard:

    - red is x-axis
    - green is y-axis
    - blue is z-axis

.. code-block:: Python

    import ezdxf
    from ezdxf.math import OCS

    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # For this example the OCS is rotated around x-axis about 45 degree
    # OCS z-axis: x=0, y=1, z=1
    # extrusion vector must not normalized here
    ocs = OCS((0, 1, 1))
    msp.add_circle(
        # You can place the 2D circle in 3D space
        # but you have to convert WCS into OCS
        center=ocs.from_wcs((0, 2, 2)),
        # center in OCS: (0.0, 0.0, 2.82842712474619)
        radius=1,
        dxfattribs={
            # here the extrusion vector should be normalized,
            # which is granted by using the ocs.uz
            'extrusion': ocs.uz,
            'color': 1,
        })
    # mark center point of circle in WCS
    msp.add_point((0, 2, 2), dxfattribs={'color': 1})

The following image shows the 2D circle in 3D space in AutoCAD `Left` and `Front` view. The blue line shows the OCS z-axis
(extrusion direction), elevation is the distance from the origin to the center of the circle in this case 2.828,
and you see that the x- and y-axis of OCS and WCS are not aligned.

.. image:: gfx/ocs-circle-side-view.png
    :alt: circle in ocs as side view
.. image:: gfx/ocs-circle-front-view.png
    :alt: circle in ocs as front view

Placing LWPolyline in 3D Space
------------------------------

For simplicity of calculation I use the :class:`UCS` class in this example to place a 2D pentagon in 3D space.

.. code-block:: Python

    import ezdxf
    from ezdxf.math import Vector, UCS

    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # center point of the pentagon should be (0, 2, 2), and the shape is
    # rotated around x-axis about 45 degree, to accomplish this I use an
    # UCS with z-axis (0, 1, 1) and an x-axis parallel to WCS x-axis.
    ucs = UCS(
        origin=(0, 2, 2),  # center of pentagon
        ux=(1, 0, 0),  # x-axis parallel to WCS x-axis
        uz=(0, 1, 1),  # z-axis
    )
    # calculating corner points in local (UCS) coordinates
    points = [Vector.from_deg_angle((360/5)*n) for n in range(5)]
    # converting UCS into OCS coordinates
    ocs_points = list(ucs.points_to_ocs(points))

    # LWPOLYLINE accepts only 2D points and has an separated DXF attribute elevation.
    # All points have the same z-axis (elevation) in OCS!
    elevation = ocs_points[0].z

    msp.add_lwpolyline(
        # LWPOLYLINE point format: (x, y, [start_width, [end_width, [bulge]]])
        # the z-axis would be start_width, so remove it
        points=[p[:2] for p in ocs_points],
        dxfattribs={
            'elevation': elevation,
            'extrusion': ucs.uz,
            'closed': True,
            'color': 1,
        })

The following image shows the 2D pentagon in 3D space in AutoCAD `Left`, `Front` and `Top` view. The three lines from the
center of the pentagon show the UCS, the three colored lines in the origin show the OCS the white lines in the origin
show the WCS.

The z-axis of the UCS and the OCS show the same direction (extrusion direction), and the x-axis of the UCS and the WCS
show the same direction. The elevation is the distance from the origin to the center of the pentagon and all points of
the pentagon have the same elevation, and you see that the y- axis of UCS, OCS and WCS are not aligned.

.. image:: gfx/ocs-lwpolyline-left.png
    :alt: pentagon in ucs as side view
.. image:: gfx/ocs-lwpolyline-front.png
    :alt: pentagon in ucs as front view

Using UCS to Place 3D Polyline
------------------------------

It is much simpler to use a 3D :class:`~ezdxf.entities.Polyline` to create the 3D pentagon.
The :class:`UCS` class is handy for this example and all kind of 3D operations.

.. code-block:: Python

    import math
    import ezdxf
    from ezdxf.math import UCS, Matrix44

    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # using an UCS simplifies 3D operations, but UCS definition can happen later
    # calculating corner points in local (UCS) coordinates without Vector class
    angle = math.radians(360/5)
    corners_ucs = [(math.cos(angle*n), math.sin(angle*n), 0) for n in range(5)]

    # let's do some transformations
    tmatrix = Matrix44.chain(  # creating a transformation matrix
        Matrix44.z_rotate(math.radians(15)),   # 1. rotation around z-axis
        Matrix44.translate(0, .333, .333),  # 2. translation
    )
    transformed_corners_ucs = tmatrix.transform_vectors(corners_ucs)

    # transform UCS into WCS
    ucs = UCS(
        origin=(0, 2, 2),  # center of pentagon
        ux=(1, 0, 0),  # x-axis parallel to WCS x-axis
        uz=(0, 1, 1),  # z-axis
    )
    corners_wcs = list(ucs.points_to_wcs(transformed_corners_ucs))

    msp.add_polyline3d(
        points=corners_wcs,
        dxfattribs={
            'closed': True,
            'color': 1,
        })

    # add lines from center to corners
    center_wcs = ucs.to_wcs((0, .333, .333))
    for corner in corners_wcs:
        msp.add_line(center_wcs, corner, dxfattribs={'color': 2})

.. image:: gfx/ucs-polyline3d.png
    :alt: 3d poyline with UCS


Placing 2D Text in 3D Space
---------------------------

The problem by placing text in 3D space is the text rotation, which is always counter clockwise around the OCS z-axis,
and ``0`` degree is in direction of the positive OCS x-axis, and the OCS x-axis is calculated by the
:ref:`Arbitrary Axis Algorithm`.

Calculate the OCS rotation angle by converting the TEXT rotation angle (in UCS or WCS) into a vector or begin with text
direction as vector, transform this direction vector into OCS and convert the OCS vector back into an angle in the OCS
xy-plane (see example), this procedure is available as :meth:`UCS.to_ocs_angle_deg` or :meth:`UCS.to_ocs_angle_rad`.

AutoCAD supports thickness for the TEXT entity only for `.shx` fonts and not for true type fonts.

.. code-block:: Python

    import ezdxf
    from ezdxf.math import UCS, Vector

    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # thickness for text works only with shx fonts not with true type fonts
    doc.styles.new('TXT', dxfattribs={'font': 'romans.shx'})

    ucs = UCS(origin=(0, 2, 2), ux=(1, 0, 0), uz=(0, 1, 1))
    # calculation of text direction as angle in OCS:
    # convert text rotation in degree into a vector in UCS
    text_direction = Vector.from_deg_angle(-45)
    # transform vector into OCS and get angle of vector in xy-plane
    rotation = ucs.to_ocs(text_direction).angle_deg

    text = msp.add_text(
        text="TEXT",
        dxfattribs={
            # text rotation angle in degrees in OCS
            'rotation': rotation,
            'extrusion': ucs.uz,
            'thickness': .333,
            'color': 1,
            'style': 'TXT',
        })
    # set text position in OCS
    text.set_pos(ucs.to_ocs((0, 0, 0)), align='MIDDLE_CENTER')

.. image:: gfx/ocs-text-top.png
    :alt: text in ucs as top view

.. image:: gfx/ocs-text-front.png
    :alt: text in ucs as front view

.. hint::

    For calculating OCS angles from an UCS, be aware that 2D entities, like TEXT or ARC, are placed parallel to the
    xy-plane of the UCS.

Placing 2D Arc in 3D Space
--------------------------

Here we have the same problem as for placing text, you need the start and end angle of the arc in degrees in OCS, and
this example also shows a shortcut for calculating the OCS angles.

.. code-block:: Python

    ucs = UCS(origin=(0, 2, 2), ux=(1, 0, 0), uz=(0, 1, 1))
    msp.add_arc(
        center=ucs.to_ocs((0, 0)),
        radius=1,
        start_angle=ucs.to_ocs_angle_deg(45),  # shortcut
        end_angle=ucs.to_ocs_angle_deg(270),  # shortcut
        dxfattribs={
            'extrusion': ucs.uz,
            'color': 1,
        })
    center = ucs.to_wcs((0, 0))
    msp.add_line(
        start=center,
        end=ucs.to_wcs(Vector.from_deg_angle(45)),
        dxfattribs={'color': 1},
    )
    msp.add_line(
        start=center,
        end=ucs.to_wcs(Vector.from_deg_angle(270)),
        dxfattribs={'color': 1},
    )

.. image:: gfx/ocs-arc-top.png
    :alt: arc in ucs as top view
.. image:: gfx/ocs-arc-front.png
    :alt: arc in ucs as front view

Placing Block References in 3D Space
------------------------------------

Despite the fact that block references (:class:`~ezdxf.entities.Insert`) can contain true 3D entities like
:class:`~ezdxf.entities.Line` or :class:`~ezdxf.entities.Mesh`, the :class:`~ezdxf.entities.Insert` entity
uses the same placing principe as :class:`~ezdxf.entities.Text` or :class:`~ezdxf.entities.Arc` shown in the
previous chapters.

Simple placing by OCS and rotation about the z-axis, can be achieved the same way as for generic 2D
entity types. The DXF attribute :attr:`Insert.dxf.rotation` rotates a block reference around the
block z-axis, which is located in the :attr:`Block.dxf.base_point`. To rotate the block reference
around the WCS x-axis, a transformation of the block z-axis into the WCS x-axis is required by
rotating the block z-axis 90 degree counter clockwise around y-axis by using an UCS:

This is just an excerpt of the important parts, see the whole code of `insert.py`_ at github.

.. code-block:: python

    # rotate UCS around an arbitrary axis:
    def ucs_rotation(ucs: UCS, axis: Vector, angle: float):
        # new in ezdxf v0.11: UCS.rotate(axis, angle)
        t = Matrix44.axis_rotate(axis, math.radians(angle))
        ux, uy, uz = t.transform_vectors([ucs.ux, ucs.uy, ucs.uz])
        return UCS(origin=ucs.origin, ux=ux, uy=uy, uz=uz)

    doc = ezdxf.new('R2010', setup=True)
    blk = doc.blocks.new('CSYS')
    setup_csys(blk)
    msp = doc.modelspace()

    ucs = ucs_rotation(UCS(), axis=Y_AXIS, angle=math.radians(90))
    # transform insert location to OCS
    insert = ucs.to_ocs((0, 0, 0))
    # rotation angle about the z-axis (= WCS x-axis)
    rotation = ucs.to_ocs_angle_deg(15)
    msp.add_blockref('CSYS', insert, dxfattribs={
        'extrusion': ucs.uz,
        'rotation': rotation,
    })

.. image:: gfx/insert_1.png
.. image:: gfx/insert_2.png

To rotate a block reference around another axis than the block z-axis, you have to find the rotated z-axis
(= extrusion vector) of the rotated block reference, following example rotates the block reference around the
block x-axis by 15 degrees:

.. code-block:: python

    # t is a transformation matrix to rotate 15 degree around the x-axis
    t = Matrix44.axis_rotate(axis=X_AXIS, angle=math.radians(15))
    # transform the block z-axis into new UCS z-axis (= extrusion vector)
    uz = Vector(t.transform(Z_AXIS))
    # create new UCS at the insertion point, because we are rotating around the x-axis,
    # ux is the same as the WCS x-axis and uz is the rotated z-axis.
    ucs = UCS(origin=(1, 2, 0), ux=X_AXIS, uz=uz)
    # transform insert location to OCS, block base_point=(0, 0, 0)
    insert = ucs.to_ocs((0, 0, 0))
    # for this case a rotation around the z-axis is not required
    rotation = 0
    msp.add_blockref('CSYS', insert, dxfattribs={
        'extrusion': ucs.uz,
        'rotation': rotation,
    })

.. image:: gfx/insert_3.png
.. image:: gfx/insert_4.png


.. _Linear Algebra: https://www.youtube.com/watch?v=kjBOesZCoqc&list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab
.. _3Blue1Brown: https://www.youtube.com/channel/UCYO_jab_esuFRV4b17AJtAw
.. _insert.py: https://github.com/mozman/ezdxf/blob/master/examples/tut/ocs/insert.py
