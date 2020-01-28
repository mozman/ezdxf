.. module:: ezdxf.math
    :noindex:

.. _tut_ucs_transform:

Tutorial for UCS Based Transformations
======================================

With `ezdxf` v0.11 a new feature for entity transformation was introduced, which makes working with OCS/UCS much
easier, this is a rework of the older :ref:`tut_ocs`. For the basic information read the old tutorial
please.

For this tutorial we don't have to worry about the OCS and the extrusion vector, this is done automatically
by the :meth:`transform_to_wcs` method of each DXF entity.

Placing 2D Circle in 3D Space
-----------------------------

To recreate the situation of the old tutorial instantiate a new UCS and rotate it around the local x-axis.
Use UCS coordinates to place the 2D CIRCLE in 3D space, and transform the UCS coordinates to the WCS.

.. literalinclude:: src/ucs/circle.py
    :lines: 6-26

.. image:: gfx/ucs-circle-side-view.png
    :alt: circle in ucs as side view
.. image:: gfx/ucs-circle-front-view.png
    :alt: circle in ucs as front view

Placing LWPolyline in 3D Space
------------------------------

Simplified LWPOLYLINE example:

.. literalinclude:: src/ucs/lwpolyline.py
    :lines: 13-27

The 2D pentagon in 3D space in BricsCAD `Left` and `Front` view.

.. image:: gfx/ucs-lwpolyline-side-view.png
    :alt: pentagon in ucs as side view
.. image:: gfx/ucs-lwpolyline-front-view.png
    :alt: pentagon in ucs as front view

Using UCS to Place 3D Polyline
------------------------------

Simplified POLYLINE example: Using a first UCS to transform the POLYLINE and a second UCS to
place the POLYLINE in 3D space.

.. literalinclude:: src/ucs/polyline3d.py
    :lines: 13-37

.. image:: gfx/ucs-polyline3d-bricscad.png
    :alt: 3d poyline with UCS


TODO Placing 2D Text in 3D Space
--------------------------------

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

TODO Placing 2D Arc in 3D Space
-------------------------------

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

TODO Placing Block References in 3D Space
-----------------------------------------

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
(extrusion vector) of the rotated block reference, following example rotates the block reference around the
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
    blockref = msp.add_blockref('CSYS', insert, dxfattribs={
        'extrusion': ucs.uz,
        'rotation': rotation,
    })

.. image:: gfx/insert_3.png
.. image:: gfx/insert_4.png

The next example shows how to translate a block references with an already established OCS:

.. code-block:: python

    translation = Vector(-3, -1, 1)
    # get established OCS
    ocs = blockref.ocs()
    # get insert location in WCS
    actual_wcs_location = ocs.to_wcs(blockref.dxf.insert)
    # translate location
    new_wcs_location = actual_wcs_location + translation
    # convert WCS location to OCS location
    blockref.dxf.insert = ocs.from_wcs(new_wcs_location)

Setting a new insert location is the same procedure without adding a translation vector, just transform the new
insert location into the OCS.

.. image:: gfx/insert_5.png
.. image:: gfx/insert_6.png

The next operation is to rotate a block reference with an established OCS, rotation axis is the block y-axis,
rotation angle is -90 degrees. First transform block y-axis (rotation axis) and block z-axis (extrusion vector)
from OCS into WCS:

.. code-block:: python

    ocs = blockref.ocs()
    # convert block y-axis (= rotation axis) into WCS vector
    rotation_axis = ocs.to_wcs((0, 1, 0))
    # convert local z-axis (=extrusion vector) into WCS vector
    local_z_axis = ocs.to_wcs((0, 0, 1))

Build transformation matrix and transform extrusion vector and build new UCS:

.. code-block:: python

    # build transformation matrix
    t = Matrix44.axis_rotate(axis=rotation_axis, angle=math.radians(-90))
    uz = t.transform(local_z_axis)
    uy = rotation_axis
    # the block reference origin stays at the same location, no rotation needed
    wcs_insert = ocs.to_wcs(blockref.dxf.insert)
    # build new UCS to convert WCS locations and angles into OCS
    ucs = UCS(origin=wcs_insert, uy=uy, uz=uz)

Set new OCS attributes, we also have to set the rotation attribute even though we do not rotate the block reference
around the local z-axis, the new block x-axis (0 deg) differs from OCS x-axis and has to be adjusted:

.. code-block:: python

    # set new OCS
    blockref.dxf.extrusion = ucs.uz
    # set new insert
    blockref.dxf.insert = ucs.to_ocs((0, 0, 0))
    # set new rotation: we do not rotate the block reference around the local z-axis,
    # but the new block x-axis (0 deg) differs from OCS x-axis and has to be adjusted
    blockref.dxf.rotation = ucs.to_ocs_angle_deg(0)


.. image:: gfx/insert_7.png
.. image:: gfx/insert_8.png

And here is the point, where my math knowledge ends, for more advanced CAD operation you have to look elsewhere.

.. _insert.py: https://github.com/mozman/ezdxf/blob/master/examples/tut/ocs/insert.py
