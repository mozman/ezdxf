Object Base Class
=================

.. class:: DXFObject

   Common base class for all non-graphical DXF objects.

.. attribute:: DXFObject.dxf

   (read only) The DXF attributes namespace, access DXF attributes by this attribute, like
   :code:`entity.dxf.layer = 'MyLayer'`. Just the *dxf* attribute is read only, the DXF attributes are read- and
   writeable.

.. attribute:: DXFObject.drawing

   (read only) Get the associated drawing.

.. attribute:: DXFObject.dxffactory

   (read only) Get the associated DXF factory. (feature for experts)

.. method:: DXFObject.dxftype()

   Get the DXF type string, like ``GEODATA`` for the geo data entity.

.. method:: DXFObject.copy()

   Deep copy of DXFObject with new handle. This is not a deep copy in the meaning of Python, because handle, link and
   owner is changed.

.. method:: DXFObject.get_dxf_attrib(key, default=DXFValueError)

   Get DXF attribute *key*, returns *default* if key doesn't exist, or raise
   ``DXFValueError`` if *default* is ``DXFValueError`` and no DXF default
   value is defined.

.. method:: DXFObject.set_dxf_attrib(key, value)

.. method:: DXFObject.del_dxf_attrib(key)

   Delete/remove DXF attribute *key*. Raises :class:`AttributeError` if *key* isn't supported.

.. method:: DXFObject.dxf_attrib_exists(key)

   Returns *True* if DXF attrib *key* really exists else *False*. Raises :class:`AttributeError` if *key* isn't supported

.. method:: DXFObject.supported_dxf_attrib(key)

   Returns *True* if DXF attrib *key* is supported by this entity else *False*. Does not grant that attrib
   *key* really exists.

.. method:: DXFObject.valid_dxf_attrib_names(key)

   Returns a list of supported DXF attribute names.

.. method:: DXFObject.dxfattribs()

   Create a dict() with all accessible DXF attributes and their value, not all data is accessible by dxf attributes like
   definition points of :class:`LWPolyline` or :class:`Spline`

.. method:: DXFObject.update_attribs(dxfattribs)

   Set DXF attributes by a dict() like :code:`{'layer': 'test', 'color': 4}`.

.. method:: DXFObject.set_flag_state(flag, state=True, name='flags')

   Set binary coded `flag` of DXF attribute `name` to 1 (on) if `state` is True, set `flag` to 0 (off) if `state`
   is False.

.. method:: DXFObject.get_flag_state(flag, name='flags')

   Returns True if any `flag` of DXF attribute is 1 (on), else False. Always check just one flag state at the time.

.. _Common DXF objects attributes:

Common DXF Object Attributes
----------------------------

.. attribute:: DXFObject.dxf.handle

    DXF handle (feature for experts)

.. attribute:: DXFObject.dxf.owner

    handle to owner, it's a BLOCK_RECORD entry (feature for experts)
