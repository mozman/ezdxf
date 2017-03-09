.. _tut_layers:

Tutorial for Layers
===================

Every object has a layer as one of its properties. You may be familiar with layers - independent drawing spaces that
stack on top of each other to create an overall image - from using drawing programs. Most CAD programs, uses layers as
the primary organizing principle for all the objects that you draw. You use layers to organize objects into logical
groups of things that belong together; for example, walls, furniture, and text notes usually belong on three separate
layers, for a couple of reasons:

* Layers give you a way to turn groups of objects on and off - both on the screen and on the plot.
* Layers provide the most efficient way of controlling object color and linetype

First you have to create layers, assigning them names and properties such as color and linetype. Then you can assign
those layers to other drawing entities. To assign a layer just use its name as string. It is not recommend but it is
possible to use layers without a layer definition, just use the layer name without a definition, the layer has the
default linetype `Continuous` and the default color is `1`.

Create a new layer definition::

    import ezdxf

    dwg = ezdxf.new()
    msp = modelspace()
    dwg.layers.new(name='MyLines', dxfattribs={'linetype': 'DASHED', 'color': 7})

The advantage of assigning a linetype and a color to a layer is that entities on this layer can inherit this properties
by using ``BYLAYER`` as linetype string ans `256` as color, both values are default values for new entities so you can
left off this assignments::

    msp.add_line((0, 0), (10, 0), dxfattribs={'layer': 'Lines'})

The new created line will be drawn with color `7` and linetype ``DASHED``.

Changing Layer State
--------------------

First get the layer definition object::

    my_lines = dwg.layers.get('MyLines')

Now you check the state of the layer::

    my_lines.is_off()  # True if layer is off
    my_lines.is_on()   # True if layer is on
    my_lines.is_locked()  # True if layer is locked
    layer_name = my_lines.dxf.name  # get the layer name

And you can change the state of the layer::

    my_lines.off()  # switch layer off, will not shown in CAD programs/viewers
    my_lines.lock()  # layer is not editable in CAD programs

Setting/Getting the default color of the layer should be done with :meth:`Layer.get_color` and :meth:`Layer.set_color`
because the color value is misused for switching the layer on and off, layer is off if the color value is negative.

Changing the default layer values::

    my_lines.dxf.linetype = 'DOTTED'
    my lines.set_color(13)  # preserves the layer on/off state

.. seealso::

    for all methods and attributes see class :class:`Layer`.

Check Available Layers
----------------------

The layers object supports some standard Python protocols::

    # iteration
    for layer in dwg.layers:
        if layer.dxf.name != '0':
            layer.off()  # switch all layers off except layer '0'

    # check for existing layer definition
    if 'MyLines' in dwg.layers::
        layer = dwg.layers.get('MyLines')

    layer_count = len(dwg.layers) # total count of layer definitions

Deleting a Layer
----------------

You can delete a layer definition::

    dwg.layers.remove('MyLines')

This just deletes the layer definition, all DXF entity with the DXF attribute layer set to ``MyLines`` are still there,
but if they inherit color and/or linetype from the layer definition they will be drawn now with linetype `Continuous`
and color `1`.

