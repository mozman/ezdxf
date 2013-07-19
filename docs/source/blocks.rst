Blocks Section
==============

The :class:`BlocksSection` class manages all block definitions of a drawing
document.

.. class:: BlocksSection

.. method:: BlocksSection.__iter__()

   Iterate over all block definitions, yielding :class:`BlockLayout` objects.

.. method:: BlocksSection.__contains__(entity)

   Test if BlockssSection contains the block definition `entity`, `entity`
   can be a block name as `str` or the :class:`Block` definition itself.

.. method:: BlocksSection.__getitem__(name)

   Get the :class:`Block` definition by `name`, raises `KeyError` if no block
   `name` exists.

.. method:: BlocksSection.get(name, default=None)

   Get the :class:`Block` definition by `name`, returns `default` if no block
   `name` exists.

.. method:: BlocksSection.new(name, base_point=(0, 0), dxfattribs={})

   Create and add a new :class:`Block`, `name` is the block-name, `base_point`
   is the insertion point of the block.

.. method:: BlocksSection.new_anonymous_block(type_char='U', base_point=(0, 0))

   Create and add a new anonymous :class:`Block`, `type_char` is the block-type,
   `base_point` is the insertion point of the block.


Block Definition
================

.. class:: Block

   Blocks are embedded into the :class:`BlockLayout` object.

Block Reference
===============

.. class:: Insert

=========== ======
DXFAttr     Description
=========== ======
layer       layer name as string, default is ``0``
linetype    linetype as string, special names ``BYLAYER``, ``BYBLOCK``,
            default is ``BYLAYER``
color       dxf color index, 0 ... BYBLOCK, 256 ... BYLAYER, default is 256
=========== ======

.. attribute:: Insert.dxf

   DXF attributes namespace, read/write DXF attributes, like :code:`object.dxf.layer = 'MyLayer'`

.. method:: Insert.__iter__()

   Iterate over appended :class:`Attrib` objects.

.. method:: Insert.get_attrib(tag)

   Get the appended :class:`Attrib` object with :code:`object.dxf.tag == tag`, returns
   :code:`None` if not found.

.. method:: Insert.add_attrib(tag, text, insert, attribs={})

   Append an :class:`Attrib` to the block reference.

Attribs
=======

.. class:: Attdef

.. attribute:: Attdef.dxf

   DXF attributes namespace, read/write DXF attributes, like :code:`object.dxf.layer = 'MyLayer'`

.. class:: Attrib

.. attribute:: Attrib.dxf

   DXF attributes namespace, read/write DXF attributes, like :code:`object.dxf.layer = 'MyLayer'`




