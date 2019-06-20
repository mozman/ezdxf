Insert
======

.. class:: Insert

   A block reference (DXF type: INSERT) with the possibility to append attributes (:class:`Attrib`).

DXF Attributes for Insert
-------------------------

:ref:`Common graphical DXF attributes`

TODO: influence of layer, linetype, color DXF attributes to block entities

.. attribute:: Insert.dxf.name

Block name (str)

.. attribute:: Insert.dxf.insert

Insertion point as (2D/3D Point in :ref:`OCS`)

.. attribute:: Insert.dxf.xscale

Scale factor for x direction (float)

.. attribute:: Insert.dxf.yscale

Scale factor for y direction (float)

.. attribute:: Insert.dxf.zscale

Scale factor for z direction (float)

.. attribute:: Insert.dxf.rotation

Rotation angle in degrees (float)

.. attribute:: Insert.dxf.row_count

Count of repeated insertions in row direction (int)

.. attribute:: Insert.dxf.row_spacing

Distance between two insert points in row direction (float)

.. attribute:: Insert.dxf.column_count

Count of repeated insertions in column direction (int)

.. attribute:: Insert.dxf.column_spacing

Distance between two insert points in column direction (float)


Insert Methods
--------------

.. method:: Insert.place(insert=None, scale=None, rotation=None)

Place block reference as point `insert` with scaling and rotation. `scale` has to be a (x, y, z)-tuple and `rotation`
a rotation angle in degrees. Parameters which are *None* will not be altered.

.. method:: Insert.grid(size=(1, 1), spacing=(1, 1))

Place block references in a grid layout with grid size=(rows, columns)-tuple and
spacing=(row_spacing, column_spacing)-tuple. `spacing` is the distance from insertion point to insertion point.

.. method:: Insert.attribs()

Iterate over appended :class:`Attrib` objects.

.. method:: Insert.has_attrib(tag, search_const=False)

Returns `True` if an attrib `tag` exists else `False`, for *search_const* doc see :meth:`Insert.get_attrib`.

.. method:: Insert.get_attrib(tag, search_const=False)

Get the appended :class:`Attrib` object with :code:`object.dxf.tag == tag`, returns
:code:`None` if not found. Some applications may not attach :class:`Attrib`, which do represent constant values, set
*search_const=True* and you get at least the associated :class:`Attdef` entity.

.. method:: Insert.get_attrib_text(tag, default=None, search_const=False)

Get content text for attrib `tag` as string or return `default` if no attrib `tag` exists, for *search_const* doc
see :meth:`Insert.get_attrib`.

.. method:: Insert.add_attrib(tag, text, insert=(0, 0), attribs={})

Append an :class:`Attrib` to the block reference. Returns an :class:`Attrib` object.

Example for appending an attribute to an INSERT entity with none standard alignment::

    insert_entity.add_attrib("TAG", "example text").set_pos((3, 7), align='MIDDLE_CENTER')

.. method:: Insert.delete_attrib(tag, ignore=False)

Delete an :class:`Attrib` from :class:`Insert`. If `ignore` is `False`, an ``DXFKeyError`` exception is raised, if
:class:`Attrib` `tag` does not exist.

.. method:: Insert.delete_all_attribs()

Delete all attached :class:`Attrib` entities.
