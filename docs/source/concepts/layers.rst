.. _layer_concept:

Layers
======

Every object has a layer as one of its properties. You may be familiar with
layers - independent drawing spaces that stack on top of each other to create
an overall image - from using drawing programs. Most CAD programs use layers as
the primary organizing principle for all the objects that you draw.
You use layers to organize objects into logical groups of things that belong
together; for example, walls, furniture, and text notes usually belong on three
separate layers, for a couple of reasons:

- Layers give you a way to turn groups of objects on and off - both on the screen
  and on the plot.
- Layers provide the most efficient way of controlling object color and linetype

Create a layer table entry :class:`~ezdxf.entities.Layer` by :meth:`Drawing.layers.add`,
assign the layer properties such as color and linetype. Then assign those layers
to other DXF entities by setting the DXF attribute :attr:`~ezdxf.entities.DXFGraphic.dxf.layer`
to the layer name as string.

The DXF format do not require a layer table entry for a layer. A layer
without a layer table entry has the default linetype ``'Continuous'``, a default
color of ``7`` and a lineweight of ``-3`` which represents the default
lineweight of 0.25mm in most circumstances.

Layer Properties
----------------

The advantage of assigning properties to a layer is that entities
can inherit this properties from the layer by using the string ``'BYLAYER'`` as
linetype string, ``256`` as color or ``-1`` as lineweight, all these values
are the default values for new entities. DXF version R2004 and later also
support inheriting `true_color` and `transparency` attributes from a layer.

Layer Status
------------

The layer status is important for the visibility and the ability to
select and edit DXF entities on that layer in CAD applications.
`Ezdxf` does not care about the visual representation and works at the level
of entity spaces and the entity database and therefore all the layer states
documented below are ignored by `ezdxf`.
This means if you iterate an entity space like the modelspace or the entity
database you will get all entities from that entity space regardless the layer
status.

- ON: the layer is visible, entities on that layer are visible, selectable and editable
- OFF: the layer is not visible, entities on that layer are not visible, not
  selectable and not editable
- FROZEN: the layer is not visible, entities on that layer are not visible,
  not selectable and not editable, very similar to the OFF status but layers
  can be frozen individually in VIEWPORTS and freezing layers may speed up some
  commands in CAD applications like ZOOM, PAN or REGEN.
- LOCKED: the layer is visible, entities on that layer are visible but not
  selectable and not editable

Deleting Layers
---------------

Deleting a layer is not as simple as it might seem, especially if you are used
to use a CAD application like AutoCAD. There is no directory of locations where
layers can be used and references to layers can occur even in third-party data.
Deleting the layer table entry removes only the default attributes of that layer
and does not delete any layer references automatically. And because a layer can
exist without a layer table entry, the layer exist as long as at least one layer
reference to the layer exist.

Renaming Layers
---------------

Renaming a layer is also problematic because the DXF format stores the layer
references in most cases as text strings, so renaming the layer table entry
just creates a new layer and all entities which still have a reference to the
old layer now inherit their attributes from an undefined layer table entry with
default settings.

Viewport Overrides
------------------

Most of the layer properties can be overriden for each
:class:`~ezdxf.entities.Viewport` entity individually and this overrides are
stored in layer table entry referenced by the handle of the VIEWPORT entity.
In contrast the frozen status of layers is store in the VIEWPORT entity.

.. seealso::

    - :ref:`tut_layers`
    - :ref:`tut_psp_viewports`
    - Autodesk Knowledge Network: `About Layers`_
    - BricsCAD Help Center: `Working with Layers`_

.. _About Layers: https://knowledge.autodesk.com/support/autocad/learn-explore/caas/CloudHelp/cloudhelp/2019/ENU/AutoCAD-Core/files/GUID-6B3E3B5D-3AE2-4162-A5FE-CFE42AB0743B-htm.html
.. _Working with Layers: https://help.bricsys.com/document/_guides--BCAD_2D_drafting--GD_workingwithlayers/V22/EN_US?id=165079137441