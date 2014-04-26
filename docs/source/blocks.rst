Blocks Section
==============

The :class:`BlocksSection` class manages all block definitions of a drawing
document.

.. class:: BlocksSection

.. method:: BlocksSection.__iter__()

   Iterate over all block definitions, yielding :class:`BlockLayout` objects.

.. method:: BlocksSection.__contains__(entity)

   Test if :class:`BlocksSection` contains the block definition `entity`, `entity`
   can be a block name as `str` or the :class:`Block` definition itself.

.. method:: BlocksSection.__getitem__(name)

   Get the :class:`Block` definition by `name`, raises `KeyError` if no block
   `name` exists.

.. method:: BlocksSection.get(name, default=None)

   Get the :class:`Block` definition by `name`, returns `default` if no block
   `name` exists.

.. method:: BlocksSection.new(name, base_point=(0, 0), dxfattribs=None)

   Create and add a new :class:`Block`, `name` is the block-name, `base_point`
   is the insertion point of the block.

.. method:: BlocksSection.new_anonymous_block(type_char='U', base_point=(0, 0))

   Create and add a new anonymous :class:`Block`, `type_char` is the block-type,
   `base_point` is the insertion point of the block.

.. method:: BlockSection.delete_block(name):

   Delete block *name*. Raises *KeyError* if block not exists.

.. method:: BlockSection.delete_all_blocks():

========= ==========
type_char Anonymous Block Type
========= ==========
U         \*U### anonymous blocks
E         \*E### anonymous non-uniformly scaled blocks
X         \*X### anonymous hatches
D         \*D### anonymous dimensions
A         \*A### anonymous groups
========= ==========

Block Definition
================

.. class:: Block

   Blocks are embedded into the :class:`BlockLayout` object.

Block Reference
===============

.. class:: Insert

   A block reference with the possibility to append attributes (:class:`Attrib`).

============== ======= ======
DXFAttr        Version Description
============== ======= ======
layer          R12     layer name (str), default is ``0``
linetype       R12     linetype name or special name ``BYLAYER`` (str), default is ``BYLAYER``
color          R12     dxf color index (int), 256 ... BYLAYER, default is 256
name           R12     block name (str)
insert         R12     insertion point as (2D/3D Point)
xscale         R12     scale factor for x direction (float)
yscale         R12     scale factor for y direction (float)
zscale         R12     scale factor for z direction (float)
rotation       R12     rotation angle in degrees (float)
row_count      R12     count of repeated insertions in row direction (int)
row_spacing    R12     distance between two insert points in row direction (float)
column_count   R12     count of repeated insertions in column direction (int)
column_spacing R12     distance between two insert points in column direction (float)
============== ======= ======

.. attribute:: Insert.dxf

   DXF attributes namespace, read/write DXF attributes, like :code:`object.dxf.layer = 'MyLayer'`

.. method:: Insert.place(insert=None, scale=None, rotation=None)

   Place block reference as point `insert` with scaling and rotation. `scale` has to be a (x, y, z)-tuple and `rotation`
   a rotation angle in degrees. Parameters which are *None* will not be altered.

.. method:: Insert.grid(size=(1, 1), spacing=(1, 1))

   Place block references in a grid layout with grid size=(rows, columns)-tuple and
   spacing=(row_spacing, column_spacing)-tuple. `spacing` is the distance from insertion point to insertion point.

.. method:: Insert.__iter__()

   Iterate over appended :class:`Attrib` objects.

.. method:: Insert.has_attrib(tag)

   Returns `True` if an attrib `tag` exists else `False`

.. method:: Insert.get_attrib(tag)

   Get the appended :class:`Attrib` object with :code:`object.dxf.tag == tag`, returns
   :code:`None` if not found.

.. method:: Insert.get_attrib_text(tag, default=None)

   Get content text for attrib `tag` as string or return `default` if no attrib `tag` exists.

.. method:: Insert.add_attrib(tag, text, insert, attribs={})

   Append an :class:`Attrib` to the block reference.

Attribs
=======

.. class:: Attdef

   The :class:`Attdef` entity is a place holder in the :class:`Block` definition, which will be used to create an
   appended :class:`Attrib` entity for an :class:`Insert` entity.

===================== ======= ===========
DXFAttr               Version Description
===================== ======= ===========
text                  R12     the default text prompted by CAD programs (str)
insert                R12     first alignment point of text (2D/3D Point), relevant for the adjustments ``LEFT``,
                              ``ALIGN`` and ``FIT``.
tag                   R12     tag to identify the attribute (str)
align_point           R12     second alignment point of text (2D/3D Point), if the justification is anything other than
                              ``LEFT``, the second alignment point specify also the first alignment
                              point: (or just the second alignment point for ``ALIGN`` and ``FIT``)
height                R12     text height in drawing units (float), default is 1
rotation              R12     text rotation in degrees (float), default is 0
oblique               R12     text oblique angle (float), default is 0
style                 R12     text style name (str), default is ``STANDARD``
width                 R12     width scale factor (float), default is 1
halign                R12     horizontal alignment flag (int), use :meth:`Attdef.set_pos` and :meth:`Attdef.get_align`
valign                R12     vertical alignment flag (int), use :meth:`Attdef.set_pos` and :meth:`Attdef.get_align`
text_generation_flag  R12     text generation flags (int)
                               - 2 = text is backward (mirrored in X)
                               - 4 = text is upside down (mirrored in Y)
prompt                R12     text prompted by CAD programs at placing a block reference containing this :class:`Attdef`
field_length          R12     just relevant to CAD programs for validating user input
===================== ======= ===========

.. attribute:: Attdef.dxf

   DXF attributes namespace, read/write DXF attributes, like :code:`object.dxf.layer = 'MyLayer'`

.. method:: Attdef.get_pos()

   see method :meth:`Text.get_pos`.

.. method:: Attdef.get_align()

   see method :meth:`Text.get_align`.

.. method:: Attdef.set_align(align='LEFT')

   see method :meth:`Text.set_align`.

.. class:: Attrib

   The :class:`Attrib` entity represents a text value associated with a tag. In most cases an :class:`Attrib` is
   appended to an :class:`Insert` entity, but it can also appear as standalone entity.

===================== ======= ===========
DXFAttr               Version Description
===================== ======= ===========
text                  R12     the content text (str)
insert                R12     first alignment point of text (2D/3D Point), relevant for the adjustments ``LEFT``,
                              ``ALIGN`` and ``FIT``.
tag                   R12     tag to identify the attribute (str)
align_point           R12     second alignment point of text (2D/3D Point), if the justification is anything other than
                              ``LEFT``, the second alignment point specify also the first alignment
                              point: (or just the second alignment point for ``ALIGN`` and ``FIT``)
height                R12     text height in drawing units (float), default is 1
rotation              R12     text rotation in degrees (float), default is 0
oblique               R12     text oblique angle (float), default is 0
style                 R12     text style name (str), default is ``STANDARD``
width                 R12     width scale factor (float), default is 1
halign                R12     horizontal alignment flag (int), use :meth:`Attrib.set_pos` and :meth:`Attrib.get_align`
valign                R12     vertical alignment flag (int), use :meth:`Attrib.set_pos` and :meth:`Attrib.get_align`
text_generation_flag  R12     text generation flags (int)
                               - 2 = text is backward (mirrored in X)
                               - 4 = text is upside down (mirrored in Y)
===================== ======= ===========

.. attribute:: Attrib.dxf

   DXF attributes namespace, read/write DXF attributes, like :code:`object.dxf.layer = 'MyLayer'`

.. method:: Attrib.get_pos()

   see method :meth:`Text.get_pos`.

.. method:: Attrib.get_align()

   see method :meth:`Text.get_align`.

.. method:: Attrib.set_align(align='LEFT')

   see method :meth:`Text.set_align`.


