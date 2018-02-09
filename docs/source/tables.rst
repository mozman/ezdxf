Table Class
===========

Generic Table Class
-------------------

.. class:: Table

    Table entry names are case insensitive: 'Test' == 'TEST'.

.. method:: Table.new(name, dxfattribs=None)

    :param str name: name of the new table-entry
    :param dict dxfattribs: optional table-parameters, these parameters are described at the table-entry-classes below.
    :returns: table-entry-class, can be ignored

Table entry creation is for all tables the same procedure::

    drawing.tablename.new(name, dxfattribs)

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

.. method:: Table.has_entry(name)

    `True` if table contains a table-entry `name`.

.. method:: Table.__contains__(name)

    `True` if table contains a table-entry `name`.

.. method:: Table.__iter__()

    Iterate over all table.entries, yields table-entry-objects.

Style Table Class
-----------------

.. class:: StyleTable(Table)

.. method:: StyleTable.get_shx(name)

    Get existing shx entry, or create a new entry.

.. method:: StyleTable.find_shx(name)

    Find .shx shape file table entry, by a case insensitive search. A .shx shape file table entry has no name, so you
    have to search by the font attribute.

Viewport Table Class
--------------------

.. class:: ViewportTable(Table)

    The viewport table stores the model space viewport configurations. A viewport configuration is a tiled view of multiple
    viewports or just one viewport. In contrast to other tables the viewport table can have multiple entries with the same
    name, because all viewport entries of a multi-viewport configuration are having the same name - the viewport
    configuration name.

    The name of the actual displayed viewport configuration is ``*ACTIVE``.

.. method:: ViewportTable.get_multi_config(name)

    Returns a list of :class:`Viewport` objects, of the multi-viewport configuration *name*.

.. method:: ViewportTable.delete_multi_config(name):

    Delete all :class:`Viewport` objects of the multi-viewport configuration *name*.


Table Entry Classes
===================

Layer
-----

.. class:: Layer

   Layer definition, defines attribute values for entities on this layer for their attributes set to ``BYLAYER``.

.. attribute:: Layer.dxf

   The DXF attributes namespace, access DXF attributes by this attribute, like :code:`object.dxf.linetype = 'DASHED'`.
   Just the *dxf* attribute is read only, the DXF attributes are read- and writeable. (read only)

===============  ======= ===========
DXFAttr          Version Description
===============  ======= ===========
handle           R12     DXF handle (feature for experts)
name             R12     layer name (str)
flags            R12     layer flags (feature for experts)
color            R12     layer color, but use :meth:`Layer.get_color`, because color is negative for layer status *off* (int)
linetype         R12     name of line type (str)
plot             R13     plot flag (int), ``1`` for plot layer (default value), ``0`` for don't plot layer
line_weight      R13     line weight enum value (int)
plot_style_name  R13     handle to PlotStyleName (feature for experts)
===============  ======= ===========

.. method:: Layer.is_frozen()

.. method:: Layer.freeze()

.. method:: Layer.thaw()

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

   Defines a text style, can be used by entities: :class:`Text`, :class:`Attrib` and :class:`Attdef`

.. attribute:: Style.dxf

   The DXF attributes namespace.

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

.. seealso::

   DXF Internals: :ref:`LTYPE Table`

.. class:: Linetype

   Defines a linetype.

.. attribute:: Linetype.dxf

   The DXF attributes namespace.

=========== ===========
DXFAttr     Description
=========== ===========
name        linetype name (str)
description linetype description (str)
length      total pattern length in drawing units (float)
items       number of linetype elements (int)
=========== ===========

DimStyle
--------

.. class:: DimStyle

   Defines a dimension style.

.. attribute:: DimStyle.dxf

   The DXF attributes namespace.

TODO DXFAttr for DimStyle class

VPort
-----

The viewport table stores the model space viewport configurations. So this entries just model space viewports, not paper
space viewports, for paper space viewports see the :class:`Viewport` entity.

.. seealso::

   DXF Internals: :ref:`VPORT Table`

.. class:: VPort

   Defines a viewport to the model space.

.. attribute:: VPort.dxf

   The DXF attributes namespace.

TODO DXFAttr for the Viewport class

View
----

The View table stores named views of the model or paper space layouts. This stored views makes parts of the
drawing or some view points of the model in a CAD applications more accessible. This views have no influence to the
drawing content or to the generated output by exporting PDFs or plotting on paper sheets, they are just for the
convenience of CAD application users.

.. seealso::

    DXF Internals: :ref:`VIEW Table`

.. class:: View

   Defines a view.

.. attribute:: View.dxf

   The DXF attributes namespace.

TODO DXFAttr for the View class

AppID
-----

.. class:: AppID

   Defines an AppID.

.. attribute:: AppID.dxf

   The DXF attributes namespace.

TODO DXFAttr for the AppID class

UCS
----

.. class:: UCS

   Defines an user coordinate system (UCS).

.. attribute:: UCS.dxf

   The DXF attributes namespace.

TODO DXFAttr for the UCS class

BlockRecord
-----------

.. class:: BlockRecord

   Defines a BlockRecord, exist just in DXF version R13 and later.

.. attribute:: BlockRecord.dxf

   The DXF attributes namespace.

TODO DXFAttr for the BlockRecord class