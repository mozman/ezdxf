
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

Get real measurement determined by definition points:

.. code-block:: Python

    for dimension in msp.query("DIMENSION"):
        print(str(dimension))
        print(f"Dimension Type: {dimension.dimtype}")
        print(f"Measurement: {dimension.get_measurement()}")

==== ============================== ===
Type Dimension Type                 Measurement
==== ============================== ===
0    Linear and Rotated Dimension   length in drawing units
1    Aligned Dimension              length in drawing units
2    Angular Dimension              angle in degree
3    Diameter Dimension             length in drawing units
4    Radius Dimension               length in drawing units
5    Angular 3P Dimension           angle in degree
6    Ordinate Dimension             feature location as :class:`~ezdxf.math.Vec3`
==== ============================== ===

Get measurement text. This is how the measurement text was rendered into the associated
geometry block by the CAD application as the DIMENSION entity was created:

.. code-block:: Python

    for dimension in msp.query("DIMENSION"):
        print(str(dimension))
        print(f"Measurement Text: {dimension.dxf.text}")

======== ===
Text     Measurement text rendered by CAD application
======== ===
``"<>"`` actual measurement
``""``   (empty string) actual measurement
``" "``  (space) measurement text is suppressed
other    measurement text entered by the CAD user
======== ===

Get measurement text from text entities in the associated geometry block. This is the
actual measurement text displayed by CAD applications:

.. code-block:: Python

    for dimension in msp.query("DIMENSION"):
        print(str(dimension))
        block = dimension.get_geometry_block()
        if block is None:
            print("Geometry block not found.")
            continue
        for entity in block.query("TEXT MTEXT"):
            print(f"{str(entity)}: {entity.dxf.text}")

.. seealso::

    **Tutorials:**

    - :ref:`tut_linear_dimension`

    **Classes:**

    - :class:`ezdxf.entities.Dimension`

ACAD_TABLE Entity
-----------------

The helper function :func:`read_acad_table_content` returns the content of an ACAD_TABLE
entity as list of table rows. If the count of table rows or table columns is missing the
complete content is stored in the first row. All cells contain strings.

.. code-block:: Python

    from ezdxf.entities.acad_table import read_acad_table_content

    ...

    for acad_table in msp.query("ACAD_TABLE"):
        content = read_acad_table_content(acad_table)
        for n, row in enumerate(content):
            for m, value in enumerate(row):
                print(f"cell [{n}, {m}] = '{value}'")

.. important::

    The ACAD_TABLE entity has only limited support to preserve the entity. There is no
    support for adding a new ACAD_TABLE entity or modifying it's content.

INSERT Entity - Block References
--------------------------------

Get Block Attributes
~~~~~~~~~~~~~~~~~~~~

Get a block attribute by tag:

.. code-block:: Python

    diameter = insert.get_attrib('diameter')
    if diameter is not None:
        print(f"diameter = {diameter.dxf.text}")

Iterate over all block attributes:

.. code-block:: Python

    for attrib in insert.attribs:
        print(f"{attrib.dxf.tag} = {attrib.dxf.text}")

.. important::

    Do not confuse block attributes and DXF entity attributes, these are different
    concepts!

Get Block Entities
~~~~~~~~~~~~~~~~~~

Get block entities as virtual DXF entities from an :class:`~ezdxf.entities.Insert` entity:

.. code-block:: Python

    for insert in msp.query("INSERT"):
        for entity in insert.virtual_entities():
            print(str(entity))

Get Transformation Matrix
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: Python

    m = insert.matrix44()

This transformation matrix transforms the virtual block entities from the block reference
coordinate system into the :ref:`WCS`.

.. seealso::

    **Tasks:**

    - :ref:`add_blockrefs`
    - :ref:`explode_block_references`

    **Tutorials:**

    - :ref:`tut_blocks`

    **Basics:**

    - :ref:`block_concept`

    **Classes:**

    - :class:`ezdxf.entities.Insert`
    - :class:`ezdxf.entities.Attrib`
    - :class:`ezdxf.entities.AttDef`
    - :class:`ezdxf.math.Matrix44`
