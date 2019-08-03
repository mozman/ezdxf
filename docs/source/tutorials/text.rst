.. _tut_text:

.. module:: ezdxf.entities
    :noindex:

Tutorial for Text
=================

Add a simple one line text entity by factory function :meth:`~ezdxf.layouts.BaseLayout.add_text`.

.. literalinclude:: ../../../examples/tut/text/simple_text.py


Valid text alignments for argument `align` in :meth:`Text.set_pos`:

============   =============== ================= =====
Vert/Horiz     Left            Center            Right
============   =============== ================= =====
Top            ``TOP_LEFT``    ``TOP_CENTER``    ``TOP_RIGHT``
Middle         ``MIDDLE_LEFT`` ``MIDDLE_CENTER`` ``MIDDLE_RIGHT``
Bottom         ``BOTTOM_LEFT`` ``BOTTOM_CENTER`` ``BOTTOM_RIGHT``
Baseline       ``LEFT``        ``CENTER``         ``RIGHT``
============   =============== ================= =====

Special alignments are ``ALIGNED`` and ``FIT``, they require a second alignment point, the text
is justified with the vertical alignment `Baseline` on the virtual line between these two points.

=========== ===========
Alignment   Description
=========== ===========
``ALIGNED`` Text is stretched or compressed to fit exactly between `p1` and `p2` and the text height
            is also adjusted to preserve height/width ratio.
``FIT``     Text is stretched or compressed to fit exactly between `p1` and `p2` but only the text
            width is adjusted, the text height is fixed by the `height` attribute.
``MIDDLE``  also a `special` adjustment, but the result is the same as for ``MIDDLE_CENTER``.
=========== ===========


Standard Text Styles
--------------------

Setup some standard text styles and linetypes by argument :code:`setup=True`::

    doc = ezdxf.new('R12', setup=True)

Replaced all proprietary font declarations in :code:`setup_sytles()` (ARIAL, ARIAL_NARROW, ISOCPEUR and TIMES) by open
source fonts, this is also the style name (e.g. :code:`{'style': 'OpenSans-Italic'}`):

.. image:: gfx/fonts.png

New Text Style
--------------

Creating a new text style is simple:

.. code-block:: Python

    doc.styles.new('myStandard', dxfattribs={'font' : 'OpenSans-Regular.ttf'})

But getting the correct font name is often not that simple, especially on Windows.
This shows the required steps to get the font name for `Open Sans`:

    - open font folder `c:\\windows\\fonts`
    - select and open the font-family `Open Sans`
    - right-click on `Open Sans Standard` and select `Properties`
    - on top of the first tab you see the font name: `OpenSans-Regular.ttf`

The style name has to be unique in the DXF document, else `ezdxf` will raise an :class:`DXFTableEntryError` exception.
To replace an existing entry, delete the existing entry by :code:`doc.styles.remove(name)`, and add the replacement
entry.

3D Text
-------

It is possible to place the 2D :class:`Text` entity into 3D space by using the :ref:`OCS`,
for further infromation see: :ref:`tut_ocs`.