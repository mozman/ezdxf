
.. _get_entity_content:

Get Content From DXF Entities
=============================

TEXT Entity
-----------

The content of the TEXT entity is stored in a single DXF attribute :attr:`Text.dxf.text` 
and has an empty string as default value:

.. code-block:: Python

    for text in msp.query("TEXT"):
        print(text.dxf.text)

The :meth:`~ezdxf.entities.Text.plain_text` method returns the content of the TEXT 
entity without formatting codes.

.. seealso::

    **Classes**

    - :class:`ezdxf.entities.Text`

    **Tutorials**

    - :ref:`tut_text`

MTEXT Entity
------------

The content of the MTEXT entity is stored in multiple DXF attributes. The content can be 
accessed by the read/write property :attr:`~ezdxf.entities.MText.text` and the DXF attribute 
:attr:`MText.dxf.text` and has an empty string as default value:

.. code-block:: Python

    for mtext in msp.query("MTEXT"):
        print(mtext.text)
        # is the same as:
        print(mtext.dxf.text)

.. important::

    The line ending character ``\n`` will be replaced automatically by the MTEXT line 
    ending ``\P``.

The :meth:`~ezdxf.entities.MText.plain_text` method returns the content of the MTEXT 
entity without inline formatting codes.

.. seealso::

    **Classes**

    - :class:`ezdxf.entities.MText`
    - :class:`ezdxf.tools.text.MTextEditor`

    **Tutorials**

    - :ref:`tut_mtext`

MLEADER Entity
--------------

The content of MLEADER entities is stored in the :attr:`MultiLeader.context` object.  
The MLEADER contains text content if the :attr:`context.mtext` attribute is not ``None`` 
and block content if the :attr:`context.block` attribute is not ``None``

.. seealso::

    **Classes**

    - :class:`ezdxf.entities.MultiLeader`
    - :class:`ezdxf.entities.MLeaderContext`
    - :class:`ezdxf.entities.MTextData`
    - :class:`ezdxf.entities.BlockData`
    - :class:`ezdxf.entities.AttribData`

    **Tutorials**

    - :ref:`tut_mleader`

Text Content
~~~~~~~~~~~~

.. code-block:: Python

    for mleader in msp.query("MLEADER MULTILEADER"):
        mtext = mleader.context.mtext
        if mtext:
            print(mtext.insert)  # insert location
            print(mtext.default_content)  # text content

The text content supports the same formatting features as the MTEXT entity.

Block Content
~~~~~~~~~~~~~

The INSERT (block reference) attributes are stored in :attr:`MultiLeader.context.block` 
as :class:`~ezdxf.entities.BlockData`.

.. code-block:: Python

    for mleader in msp.query("MLEADER MULTILEADER"):
        block = mleader.context.block
        if block:
            print(block.insert)  # insert location


The ATTRIB attributes are stored outside the context object in :attr:`MultiLeader.block_attribs` 
as :class:`~ezdxf.entities.AttribData`.

.. code-block:: Python

    for mleader in msp.query("MLEADER MULTILEADER"):
        for attrib in mleader.block_attribs:
            print(attrib.text)  # text content of the ATTRIB entity


DIMENSION Entity
----------------

TODO

ACAD_TABLE Entity
-----------------

TODO

INSERT Entity - Block References
--------------------------------

TODO

Get Attribute Content
~~~~~~~~~~~~~~~~~~~~~

TODO

Get Virtual Entities
~~~~~~~~~~~~~~~~~~~~

TODO
