.. _get_dxf_attributes:

Get DXF Attributes From Entities
================================

All DXF attributes of an entity are grouped in the namespace attribute :attr:`dxf`:

.. code-block:: Python

    e.dxf.layer  # layer of the entity as string
    e.dxf.color  # color of the entity as integer

The :attr:`dxf` namespace attribute has a :meth:`get` method, which can return a 
default value if the attribute doesn't exist:

.. code-block:: Python

    e.dxf.get('color', 9)

The attribute has to be supported by the DXF type otherwise a :class:`DXFAttributeError` 
will be raised.  You can check if an DXF attribute is supported by the method 
:meth:`dxf.is_supported`:

.. code-block:: Python

    line = msp.add_line((0, 0), (1, 0))
    assert line.dxf.is_supported("text") is False

Optional DXF Attributs
----------------------

Many DXF attributes are optional, you can check if an attribute exists by the 
:meth:`hasattrib` method:

.. code-block:: Python

    assert line.dxf.hasattrib("linetype") is False

Default Values
--------------

Some DXF attributes have default values and this default value will be returned if the 
DXF attribute doesn't exist:

.. code-block:: Python

    assert line.dxf.linetype == "BYLAYER"

.. seealso::

    **Tasks:**

    - :ref:`Common graphical DXF attributes`    
    - :ref:`modify_dxf_attributes`
    - :ref:`delete_dxf_attributes`

    **Tutorials:**
   
    - :ref:`tut_common_graphical_attributes`
    - :ref:`tut_getting_data`



