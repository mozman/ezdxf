Drawing Settings
================

The drawing settings are stored in the header section, which is accessible by
the :attr:`~Drawing.header` attribute. See online documentation from Autodesk for available `header variables`_.

.. class:: HeaderSection

.. method:: HeaderSection.__getitem__(key)

   Get drawing settings by index operator like: :code:`drawing.header['$ACADVER']`

.. method:: HeaderSection.__setitem__(key, value)

   Set drawing settings by index operator like: :code:`drawing.header['$ANGDIR'] = 1 # Clockwise angles`

.. _header variables: http://docs.autodesk.com/ACD/2014/ENU/files/GUID-A85E8E67-27CD-4C59-BE61-4DC9FADBE74A.htm