.. _tut_mtext:

Tutorial for MText
==================

The :class:`~ezdxf.entities.MText` entity is a multi line entity with extended formatting possibilities.
The paragraph text is placed in a bounding box that limits the extend of the text. The MText entity
requires at least DXF version R2000, to use all features (e.g. background fill) of MText it is
required to use DXF R2007.

Usual code prolog:

.. code-block:: python

    import ezdxf

    doc = ezdxf.new('R2007')
    msp = doc.modelspace()

    lorem_ipsum = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit,
    sed do eiusmod tempor incididunt ut labore et dolore magna
    aliqua. Ut enim ad minim veniam, quis nostrud exercitation
    ullamco laboris nisi ut aliquip ex ea commodo consequat.
    Duis aute irure dolor in reprehenderit in voluptate velit
    esse cillum dolore eu fugiat nulla pariatur. Excepteur sint
    occaecat cupidatat non proident, sunt in culpa qui officia
    deserunt mollit anim id est laborum.
    """

Adding a MText entity
---------------------

The MText entity can be added to any layout (modelspace, paperspace or block) by the
:meth:`~ezdxf.layouts.BaseLayout.add_mtext` function.

.. code-block:: python

    # store MText entity for additional manipulations
    mtext = msp.add_mtext(lorem_ipsum)

This adds a MText entity with a default column width of ``2.5`` drawing units, the default
text style ``'Standard'`` and many other default values. The MText content can be accessed
by the :attr:`text` attribute, this attribute can be edited like any Python string:

.. code-block:: python

    mtext.text += 'Append additional text to the MText entity.'
    # even shorter with __iadd__() support:
    mtext += 'Append additional text to the MText entity.'

Text placement
--------------

The location of the MText entity is defined by the :attr:`MText.dxf.insert` and the
:attr:`MText.dxf.attachment_point` attributes. The :attr:`attachment_point` defines
the text alignment relative to the :attr:`insert` location, default value is ``1``.

Attachment point constants defined in :mod:`ezdxf.lldxf.const`:

============================== =======
MText.dxf.attachment_point     Value
============================== =======
MTEXT_TOP_LEFT                 1
MTEXT_TOP_CENTER               2
MTEXT_TOP_RIGHT                3
MTEXT_MIDDLE_LEFT              4
MTEXT_MIDDLE_CENTER            5
MTEXT_MIDDLE_RIGHT             6
MTEXT_BOTTOM_LEFT              7
MTEXT_BOTTOM_CENTER            8
MTEXT_BOTTOM_RIGHT             9
============================== =======

The MText entity has a method for setting :attr:`insert`, :attr:`attachment_point` and :attr:`rotation` attributes
by one call: :meth:`~ezdxf.entities.MText.set_location`

Character height
----------------

The character height is defined by the DXF attribute :attr:`MText.dxf.char_height` in drawing units, which
has also consequences for the line spacing of the MText entity:

.. code-block:: python

    mtext.dxf.char_height = 0.5

The character height can be changed inline, see also :ref:`mtext_formatting` and :ref:`mtext_inline_codes`.

Text rotation (direction)
-------------------------

The :attr:`MText.dxf.rotation` attribute defines the text rotation as angle between the x-axis and the
horizontal direction of the text in degrees. The :attr:`MText.dxf.text_direction` attribute defines the
horizontal direction of MText as vector in WCS or OCS, if an :ref:`OCS` is defined.
Both attributes can be present at the same entity, in this case the :attr:`MText.dxf.text_direction`
attribute has the higher priority.

The MText entity has two methods to get/set rotation: :meth:`~ezdxf.entities.MText.get_rotation` returns the
rotation angle in degrees independent from definition as angle or direction, and
:meth:`~ezdxf.entities.MText.set_rotation` set the :attr:`rotation` attribute and
removes the :attr:`text_direction` attribute if present.

Defining the bounding box
-------------------------

The bounding box limits the text of the MText entity to a defined area:

.. _mtext_formatting:

MText formatting
----------------

Background color (filling)
--------------------------

