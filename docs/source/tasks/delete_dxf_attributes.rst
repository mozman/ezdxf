.. _delete_dxf_attributes:

Delete DXF Attributes from Entities
===================================

All DXF attributes of an entity are grouped in the namespace attribute :attr:`dxf`. 
You can delete a DXF attribute by the `del` operator:

.. code-block:: Python

    line = msp.add_line((0, 0), (1, 0))
    line.dxf.layer = "MyLayer"
    del line.dxf.layer

    assert line.dxf.layer == "0"  # the default layer for all entities

The `del` operator raises an :class:`DXFAttributeError` if the attribute doesn't exist 
or isn't supported.  The :meth:`discard` method ignores these errors:

.. code-block:: Python

    line.dxf.discard('text')  # doesn't raise an exception

.. seealso::

    **Tasks**

    - :ref:`Common graphical DXF attributes`
    - :ref:`get_dxf_attributes`
    - :ref:`modify_dxf_attributes`

    **Tutorials:**
   
    - :ref:`tut_common_graphical_attributes`
