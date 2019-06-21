View
====

The View table stores named views of the model or paperspace layouts. This stored views makes parts of the
drawing or some view points of the model in a CAD applications more accessible. This views have no influence to the
drawing content or to the generated output by exporting PDFs or plotting on paper sheets, they are just for the
convenience of CAD application users.

.. class:: View

DXF Attributes for View
-----------------------

.. attribute:: View.dxf.handle

.. attribute:: View.dxf.owner

requires DXF R13 or later

.. attribute:: View.dxf.name

.. attribute:: View.dxf.flags

.. attribute:: View.dxf.height

.. attribute:: View.dxf.width

.. attribute:: View.dxf.center_point

.. attribute:: View.dxf.direction_point

.. attribute:: View.dxf.target_point

.. attribute:: View.dxf.lens_length

.. attribute:: View.dxf.front_clipping

.. attribute:: View.dxf.back_clipping

.. attribute:: View.dxf.view_twist

.. attribute:: View.dxf.view_mode

.. seealso::

    DXF Internals: :ref:`VIEW Table`
