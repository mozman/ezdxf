.. _tut_text:

.. module:: ezdxf.entities
    :noindex:

Tutorial for Text
=================

Add a simple one line text entity by factory function :meth:`~ezdxf.layouts.BaseLayout.add_text`.

.. code-block:: python

    import ezdxf
    from ezdxf.enums import TextEntityAlignment

    # The TEXT entity is a DXF primitive and is supported in all DXF versions.
    # The argument setup=True creates standard linetypes and text styles in the
    # new DXF document.
    doc = ezdxf.new("R12", setup=True)
    msp = doc.modelspace()

    # Use method set_placement() to define the TEXT alignment, because the
    # relations between the DXF attributes 'halign', 'valign', 'insert' and
    # 'align_point' are tricky.
    msp.add_text("A Simple Text").set_placement(
        (2, 3),
        align=TextEntityAlignment.MIDDLE_RIGHT
    )

    # Using a predefined text style:
    msp.add_text(
        "Text Style Example: Liberation Serif",
        height=0.35,
        dxfattribs={"style": "LiberationSerif"}
    ).set_placement((2, 6), align=TextEntityAlignment.LEFT)

    doc.saveas("simple_text.dxf")

Alignments defined by the enum :class:`~ezdxf.enums.TextEntityAlignment`:

============   =============== ================= =====
Vert/Horiz     Left            Center            Right
============   =============== ================= =====
Top            ``TOP_LEFT``    ``TOP_CENTER``    ``TOP_RIGHT``
Middle         ``MIDDLE_LEFT`` ``MIDDLE_CENTER`` ``MIDDLE_RIGHT``
Bottom         ``BOTTOM_LEFT`` ``BOTTOM_CENTER`` ``BOTTOM_RIGHT``
Baseline       ``LEFT``        ``CENTER``        ``RIGHT``
============   =============== ================= =====

Special alignments are ``ALIGNED`` and ``FIT``, they require a second alignment
point, the text is justified with the vertical alignment `Baseline` on the
virtual line between these two points.

=========== ===========
Alignment   Description
=========== ===========
``ALIGNED`` Text is stretched or compressed to fit exactly between `p1` and `p2`
            and the text height is also adjusted to preserve height/width ratio.
``FIT``     Text is stretched or compressed to fit exactly between `p1` and `p2`
            but only the text width is adjusted, the text height is fixed by the
            `height` attribute.
``MIDDLE``  also a `special` adjustment, but the result is the same as for
            ``MIDDLE_CENTER``.
=========== ===========


Standard Text Styles
--------------------

Setup some standard text styles and linetypes by argument :code:`setup=True`::

    doc = ezdxf.new('R12', setup=True)

Replaced all proprietary font declarations in :code:`setup_styles()` (ARIAL,
ARIAL_NARROW, ISOCPEUR and TIMES) by open source fonts, this is also the style
name (e.g. :code:`{'style': 'OpenSans-Italic'}`):

.. image:: gfx/fonts.png

.. important::

    To see the defined text styles in a DXF viewer or CAD application, the
    applications have to know where the referenced TTF fonts can be found.
    This configuration is not possible by `ezdxf` and has to be done for each
    application as described in their documentation.

    See also: :ref:`font resources`

New Text Style
--------------

Creating a new text style is simple:

.. code-block:: Python

    doc.styles.new("myStandard", dxfattribs={"font" : "OpenSans-Regular.ttf"})

Getting the correct font name is often not that simple, especially on Windows.
This shows the required steps to get the font name for `Open Sans`:

    - open font folder `c:\\windows\\fonts`
    - select and open the font-family `Open Sans`
    - right-click on `Open Sans Standard` and select `Properties`
    - on top of the first tab you see the font name: ``'OpenSans-Regular.ttf'``

The style name has to be unique in the DXF document, otherwise `ezdxf` will
raise an :class:`DXFTableEntryError` exception. To replace an existing entry,
delete the existing entry by :code:`doc.styles.remove(name)`, and add the
replacement entry.

3D Text
-------

It is possible to place the 2D :class:`Text` entity into 3D space by using the
:ref:`OCS`, for further information see: :ref:`tut_ocs` and
:ref:`tut_ucs_transform`.