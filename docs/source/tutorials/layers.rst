.. _tut_layers:

Tutorial for Layers
===================

If you are not familiar with the concept of layers, please read this first: :ref:`layer_concept`

Reminder: a layer definition is not required for using a layer!

Create a Layer Definition
-------------------------

.. code-block:: python

    import ezdxf

    doc = ezdxf.new(setup=True)  # setup required line types
    msp = doc.modelspace()
    doc.layers.add(name="MyLines", color=7, linetype="DASHED")

The advantage of assigning a linetype and a color to a layer is that entities
on this layer can inherit this properties by using ``"BYLAYER"`` as linetype
string and ``256`` as color, both values are default values for new entities
so you can leave off these assignments:

.. code-block:: python

    msp.add_line((0, 0), (10, 0), dxfattribs={"layer": "MyLines"})

The new created line will be drawn with color ``7`` and linetype ``"DASHED"``.

Moving an Entity to a Different Layer
-------------------------------------

Moving an entity to a different layer is a simple assignment of the new
layer name to the :attr:`layer` attribute of the entity.

.. code-block:: python

    line = msp.add_line((0, 0), (10, 0), dxfattribs={"layer": "MyLines"})
    # move the entity to layer "OtherLayer"
    line.dxf.layer = "OtherLayer"

Changing Layer State
--------------------

Get the layer definition object from the layer table:

.. code-block:: python

    my_lines = doc.layers.get('MyLines')

Check the state of the layer:

.. code-block:: python

    my_lines.is_off()  # True if layer is off
    my_lines.is_on()   # True if layer is on
    my_lines.is_locked()  # True if layer is locked
    layer_name = my_lines.dxf.name  # get the layer name

Change the state of the layer:

.. code-block:: python

    # switch layer off, entities at this layer will not shown in CAD applications/viewers
    my_lines.off()

    # lock layer, entities at this layer are not editable in CAD applications
    my_lines.lock()

Get/set the color of a layer by property :attr:`Layer.color`, because the
DXF attribute :attr:`Layer.dxf.color` is misused for switching the layer on and
off, the layer is off if the color value is negative.

Changing the layer properties:

.. code-block:: python

    my_lines.dxf.linetype = "DOTTED"
    my_lines.color = 13  # preserves on/off state of layer

.. seealso::

    For all methods and attributes see class :class:`~ezdxf.entities.Layer`.

Check Available Layers
----------------------

The :class:`~ezdxf.sections.table.LayerTable` object supports some standard
Python protocols:

.. code-block:: python

    # iteration
    for layer in doc.layers:
        if layer.dxf.name != "0":
            layer.off()  # switch all layers off except layer "0"

    # check for existing layer definition
    if "MyLines" in doc.layers:
        layer = doc.layers.get("MyLines")

    layer_count = len(doc.layers) # total count of layer definitions

Renaming a Layer
----------------

The :class:`~ezdxf.entities.Layer` class has a method for renaming the layer,
but has same limitations, not all places where layer references can occur are
documented, third-party entities are black-boxes with unknown content and layer
references could be stored in the extended data section of any DXF entity or in
a XRECORD entity, so some references may reference a non-existing layer
definition after the renaming, at least these references are still valid,
because a layer definition is not required for using a layer.

.. code-block:: python

    my_lines = doc.layers.get("MyLines")
    my_lines.rename("YourLines")


Deleting a Layer Definition
---------------------------

Delete a layer definition:

.. code-block:: python

    doc.layers.remove("MyLines")

This just deletes the layer definition, all DXF entities referencing this layer
still exist, if they inherit any properties from the deleted layer they will now
get the default layer properties.

.. warning::

    The behavior of entities referencing the layer by handle is unknown and may
    break the DXF document.

Deleting All Entities From a Layer
----------------------------------

Because of all these uncertainties about layer references mentioned above,
deleting all entities referencing a certain layer from a DXF document is not
implemented as an API call!

Nonetheless deleting all graphical entities from the DXF document which do
reference a certain layer by the :attr:`layer` attribute is a safe procedure:

.. code-block:: python

    key_func = doc.layers.key
    layer_key = key_func("MyLines")
    # The trashcan context-manager is a safe way to delete entities from the
    # entities database while iterating.
    with doc.entitydb.trashcan() as trash:
        for entity in doc.entitydb.values():
            if not entity.dxf.hasattr("layer"):
                continue
            if layer_key == key_func(entity.dxf.layer):
                # safe destruction while iterating
                trash.add(entity.dxf.handle)
