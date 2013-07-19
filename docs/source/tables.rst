Table Class
===========

.. class:: Table

.. method:: Table.create(name, dxfattribs=None)

    :param str name: name of the new table-entry
    :param dict dxfattribs: optional table-parameters, these parameters are described at the table-entry-classes below.
    :returns: table-entry-class, can be ignored

Table entry creation is for all tables the same procedure::

    drawing.tablename.create(name, dxfattribs)

Where `tablename` can be: `layers`, `styles`, `linetypes`, `views`, `viewports`
or `dimstyles`.

.. method:: Table.get(name)

    Get table-entry `name`. Raises `ValueError` if table-entry is not
    present.

.. method:: Table.remove(name)

    Removes table-entry `name`. Raises `ValueError` if table-entry is not
    present.

.. method:: Table.__len__()

    Get count of table-entries.

.. method:: Table.__contains__(name)

    `True` if table contains a table-entry named `name`.

.. method:: Table.__iter__()

    Iterate over all table.entries, yields table-entry-objects.

Table Entry Classes
===================

Layer
-----

.. class:: Layer

   Layer definition, defines attribute values for entities on this layer for their attributes set to ``BYLAYER``.

.. attribute:: Layer.dxf

   The DXF attributes namespace, access DXF attributes by this attribute, like :code:`object.dxf.linetype = 'DASHED'`.
   Just the *dxf* attribute is read only, the DXF attributes are read- and writeable. (read only)

=========== ===========
DXFAttr     Description
=========== ===========
handle      DXF handle (feature for experts)
name        layer name (str)
flags       layer flags (feature for experts)
color       layer color, but use :meth:`Layer.get_color`, because color is negative for layer status *off* (int)
linetype    name of line type (str)
=========== ===========

.. method:: Layer.is_locked()

.. method:: Layer.lock()

   Lock layer, entities on this layer are not editable - just important in CAD applications.

.. method:: Layer.unlock()

   unlock layer, entities on this layer are editable - just important in CAD applications.

.. method:: Layer.is_off()

.. method:: Layer.is_on()

.. method:: Layer.on()

   Switch layer *on* (visible).

.. method:: Layer.off()

   Switch layer *off* (invisible).

.. method:: Layer.get_color()

   Get layer color, preferred method for getting the layer color, because color is negative for layer status *off*.

.. method:: Layer.set_color(color)

   Set layer color to *color*, preferred method for setting the layer color, because color is negative for layer status *off*.

Style
-----

.. class:: Style

.. attribute:: Style.dxf

   The DXF attributes namespace, access DXF attributes by this attribute, like :code:`object.dxf.name = 'MyStyle'`.
   Just the *dxf* attribute is read only, the DXF attributes are read- and writeable. (read only)

====================== ===========
DXFAttr                Description
====================== ===========
handle                 DXF handle (feature for experts)
name                   style name (str)
flags                  layer flags (feature for experts)
height                 fixed height in drawing units, ``0`` for not fixed (float)
width                  width factor (float), default is ``1``
oblique                oblique angle in degrees, ``0`` is vertical (float)
text_generation_flags  text generations flags (int)
                        - 2 = text is backward (mirrored in X)
                        - 4 = text is upside down (mirrored in Y)
last_height            last height used in drawing units (float)
font                   primary font file name (str)
bigfont                big font name, blank if none (str)
====================== ===========

Linetype
--------

.. class:: Linetype

Viewport
--------

.. class:: Viewport

View
----

.. class:: View

DimStyle
--------

.. class:: DimStyle
