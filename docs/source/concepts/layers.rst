.. _layer_concept:

Layer Concept
=============

Every object has a layer as one of its properties. You may be familiar with layers - independent drawing spaces that
stack on top of each other to create an overall image - from using drawing programs. Most CAD programs, uses layers as
the primary organizing principle for all the objects that you draw. You use layers to organize objects into logical
groups of things that belong together; for example, walls, furniture, and text notes usually belong on three separate
layers, for a couple of reasons:

* Layers give you a way to turn groups of objects on and off - both on the screen and on the plot.
* Layers provide the most efficient way of controlling object color and linetype

Create a layer table entry :class:`~ezdxf.entities.Layer` by :meth:`Drawing.layers.new`, assign the layer
properties such as color and linetype. Then assign those layers to other DXF entities by setting the DXF attribute
:attr:`~ezdxf.entities.DXFGraphic.dxf.layer` to the layer name as string.

It is possible to use layers without a layer definition but not recommend, just use a layer name without a
layer definition, the layer has the default linetype ``'Continuous'`` and the default color is ``7``.

The advantage of assigning a linetype and a color to a layer is that entities on this layer can inherit this properties
by using ``'BYLAYER'`` as linetype string and ``256`` as color, both values are default values for new entities.

.. seealso::

    :ref:`tut_layers`
