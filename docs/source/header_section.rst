Drawing Header Section
======================

The drawing settings are stored in the header section, which is accessible by
the :attr:`~Drawing.header` attribute. See the online documentation from Autodesk for available `header variables`_.
the :attr:`~Drawing.header` attribute. See the online documentation from Autodesk for available `header variables`_.

.. class:: HeaderSection

.. method:: HeaderSection.__getitem__(key)

   Get drawing settings by index operator like: :code:`drawing.header['$ACADVER']`

.. method:: HeaderSection.__setitem__(key, value)

   Set drawing settings by index operator like: :code:`drawing.header['$ANGDIR'] = 1 # Clockwise angles`

.. attribute:: HeaderSection.custom_vars

   Stores the custom drawing properties in :class:`CustomVars` object.


.. class:: CustomVars

   Stores custom properties in the DXF header as $CUSTOMPROPERTYTAG/$CUSTOMPROPERTY values, but so far AutoCAD doesn't
   show this values - I don't know why.

.. attribute:: CustomVars.properties

   List of custom drawing properties, stored as string tuples ``(tag, value)``. Multiple occurrence of the same custom
   tag is allowed, but not well supported by the interface. This is a standard python list and it is save to change this
   list as long you store just tuples of strings in the format ``(tag, value)``.

.. method:: CustomVars.__len__()

   Count of custom properties.

.. method:: CustomVars.__iter__()

   Iterate over all custom properties as ``(tag, value)`` tuples.

.. method:: CustomVars.clear()

   Removes all custom properties.

.. method:: CustomVars.get(tag, default=None)

   Returns the value of the first custom property ``tag``.

.. method:: CustomVars.has_tag(tag)

   ``True`` if custom property ``tag`` exists, else ``False``.

.. method:: CustomVars.append(tag, value)

   Add custom property as ``(tag, value)`` tuple.

.. method:: CustomVars.remove(tag)

   Removes the the first custom property ``tag``.

.. _header variables: http://docs.autodesk.com/ACD/2014/ENU/files/GUID-A85E8E67-27CD-4C59-BE61-4DC9FADBE74A.htm