.. _tut_layers:

Tutorial for Layers
===================

If you are not familiar with the concept of layers, please read this first: :ref:`layer_concept`

Create a Layer Definition
-------------------------

.. code-block:: python

    import ezdxf

    doc = ezdxf.new(setup=True)  # setup required line types
    msp = modelspace()
    doc.layers.new(name='MyLines', dxfattribs={'linetype': 'DASHED', 'color': 7})

The advantage of assigning a linetype and a color to a layer is that entities on this layer can inherit this properties
by using ``'BYLAYER'`` as linetype string and ``256`` as color, both values are default values for new entities
so you can left off this assignments:

.. code-block:: python

    msp.add_line((0, 0), (10, 0), dxfattribs={'layer': 'MyLines'})

The new created line will be drawn with color ``7`` and linetype ``'DASHED'``.

Changing Layer State
--------------------

Get the layer definition object:

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

Get/set default color of a layer by property :attr:`Layer.color`, because the DXF attribute :attr:`Layer.dxf.color`
is misused for switching the layer on and off, layer is off if the color value is negative.

Changing the default layer values:

.. code-block:: python

    my_lines.dxf.linetype = 'DOTTED'
    my_lines.color = 13  # preserves on/off state of layer

.. seealso::

    For all methods and attributes see class :class:`~ezdxf.entities.Layer`.

Check Available Layers
----------------------

The layers object supports some standard Python protocols:

.. code-block:: python

    # iteration
    for layer in doc.layers:
        if layer.dxf.name != '0':
            layer.off()  # switch all layers off except layer '0'

    # check for existing layer definition
    if 'MyLines' in doc.layers::
        layer = doc.layers.get('MyLines')

    layer_count = len(doc.layers) # total count of layer definitions

Deleting a Layer
----------------

Delete a layer definition:

.. code-block:: python

    doc.layers.remove('MyLines')

This just deletes the layer definition, all DXF entity with the DXF attribute layer set to ``'MyLines'`` are still there,
but if they inherit color and/or linetype from the layer definition they will be drawn now with linetype ``'Continuous'``
and color ``1``.

