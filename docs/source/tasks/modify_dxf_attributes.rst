.. _modify_dxf_attributes:

Modify DXF Attributes of Entities
=================================

All DXF attributes of an entity are grouped in the namespace attribute :attr:`dxf`. 
You can modify/set a DXF attribute by assignment:

.. code-block:: Python

    e.dxf.layer = "MyLayer"
    e.dxf.color = 9

... or by the :meth:`set` method:

.. code-block:: Python

    e.dxf.set('color', 9)

The attribute has to be supported by the DXF type otherwise a :class:`DXFAttributeError` 
will be raised.  You can check if an DXF attribute is supported by the method 
:meth:`dxf.is_supported`:

.. code-block:: Python

    line = msp.add_line((0, 0), (1, 0))
    assert line.dxf.is_supported("text") is False


.. seealso::
    
    **Tasks**

    - :ref:`Common graphical DXF attributes`
    - :ref:`get_dxf_attributes`
    - :ref:`delete_dxf_attributes`

    **Tutorials:**
   
    - :ref:`tut_common_graphical_attributes`
