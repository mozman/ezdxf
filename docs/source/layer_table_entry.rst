Layer
=====

.. class:: Layer

Layer definition, defines attribute values for entities on this layer for their attributes set to ``BYLAYER``.

DXF Attributes for Layer
------------------------

.. attribute:: Layer.dxf.handle

DXF handle (feature for experts)

.. attribute:: Layer.dxf.owner

requires DXF R13 or later

.. attribute:: Layer.dxf.name

Layer name (str)

.. attribute:: Layer.dxf.flags

Layer flags (feature for experts)

.. attribute:: Layer.dxf.color

Layer color, but use :meth:`Layer.get_color`, because color is negative for layer status *off* (int)

.. attribute:: Layer.dxf.linetype

Name of line type (str)

.. attribute:: Layer.dxf.plot

Plot flag (int)

- 1 = plot layer (default value)
- 0 = don't plot layer

.. attribute:: Layer.dxf.line_weight

Line weight enum value (int)

.. attribute:: Layer.dxf.plot_style_name

Handle to PlotStyleName (feature for experts)

requires DXF R13 or later

.. attribute:: Layer.dxf.line_weight

requires DXF R13 or later

.. attribute:: Layer.dxf.plot_style_name

requires DXF R13 or later

.. attribute:: Layer.dxf.material

requires DXF R13 or later

Layer Methods
-------------

.. method:: Layer.is_frozen()

.. method:: Layer.freeze()

.. method:: Layer.thaw()

.. method:: Layer.is_locked()

.. method:: Layer.lock()

Lock layer, entities on this layer are not editable - just important in CAD applications.

.. method:: Layer.unlock()

Unlock layer, entities on this layer are editable - just important in CAD applications.

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
