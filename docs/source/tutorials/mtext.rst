.. _tut_mtext:

Tutorial for MText
==================

The :class:`~ezdxf.entities.MText` entity is a multi line entity with extended
formatting possibilities and requires at least DXF version R2000, to use all
features (e.g. background fill) DXF R2007 is required.

Prolog code:

.. code-block:: python

    import ezdxf

    doc = ezdxf.new('R2007', setup=True)
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
    mtext = msp.add_mtext(lorem_ipsum, dxfattribs={'style': 'OpenSans'})

This adds a MText entity with text style ``'OpenSans'``.
The MText content can be accessed by the :attr:`text` attribute, this attribute can be edited
like any Python string:

.. code-block:: python

    mtext.text += 'Append additional text to the MText entity.'
    # even shorter with __iadd__() support:
    mtext += 'Append additional text to the MText entity.'


.. image:: gfx/mtext_without_width.png

.. important::

    Line endings ``\n`` will be replaced by the MTEXT line endings ``\P`` at DXF export, but **not**
    vice versa ``\P`` by ``\n`` at DXF file loading.

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

The MText entity has a method for setting :attr:`insert`,
:attr:`attachment_point` and :attr:`rotation` attributes
by one call: :meth:`~ezdxf.entities.MText.set_location`

Character height
----------------

The character height is defined by the DXF attribute
:attr:`MText.dxf.char_height` in drawing units, which
has also consequences for the line spacing of the MText entity:

.. code-block:: python

    mtext.dxf.char_height = 0.5

The character height can be changed inline, see also :ref:`mtext_formatting`
and :ref:`mtext_inline_codes`.

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

Defining a wrapping border
--------------------------

The wrapping border limits the text width and forces a line break for text beyond this border.
Without attribute :attr:`dxf.width` (or setting ``0``) the lines are wrapped only at the regular
line endings ``\P`` or ``\n``, setting the reference column width forces additional line wrappings
at the given width. The text height can not be limited, the text always occupies as much space as
needed.

.. code-block:: python

    mtext.dxf.width = 60

.. image:: gfx/mtext_width_60.png

.. _mtext_formatting:

MText formatting
----------------

MText supports inline formatting by special codes: :ref:`mtext_inline_codes`

.. code-block:: python

    mtext.text = "{\\C1red text} - {\\C3green text} - {\\C5blue text}"

.. image:: gfx/mtext_rgb.png

Stacked text
------------

MText also supports stacked text:

.. code-block:: python

    # the space ' ' in front of 'Lower' anr the ';' behind 'Lower' are necessary
    # combined with vertical center alignment
    mtext.text = "\\A1\\SUpper^ Lower; - \\SUpper/ Lower;} - \\SUpper# Lower;"


.. image:: gfx/mtext_stacked.png

Background color (filling)
--------------------------

The MText entity can have a background filling:

    - :ref:`ACI`
    - true color value as ``(r, g, b)`` tuple
    - color name as string, use special name ``'canvas'`` to use the canvas background color


Because of the complex dependencies `ezdxf` provides a method to set all required DXF attributes at once:

.. code-block:: python

    mtext.set_bg_color(2, scale=1.5)

The parameter `scale` determines how much border there is around the text, the value is based on the text height,
and should be in the range of ``1`` - ``5``, where ``1`` fits exact the MText entity.

.. image:: gfx/mtext_bg_color.png