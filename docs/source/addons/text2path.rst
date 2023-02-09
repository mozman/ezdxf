.. module:: ezdxf.addons.text2path

text2path
=========

Tools to convert text strings and text based DXF entities into outer- and inner
linear paths as :class:`~ezdxf.path.Path` objects. These tools depend on
the optional `Matplotlib`_ package. At the moment only the TEXT and the ATTRIB
entity can be converted into paths and hatches.

Don't expect a 100% match compared to CAD applications.

Text Alignments
---------------

The text alignments are enums of type :class:`ezdxf.enums.TextEntityAlignment`

============   =============== ================= =====
Vertical       Left            Center            Right
============   =============== ================= =====
Top            TOP_LEFT        TOP_CENTER        TOP_RIGHT
Middle         MIDDLE_LEFT     MIDDLE_CENTER     MIDDLE_RIGHT
Bottom         BOTTOM_LEFT     BOTTOM_CENTER     BOTTOM_RIGHT
Baseline       LEFT            CENTER            RIGHT
============   =============== ================= =====

The vertical middle alignments (MIDDLE_XXX), center the text
vertically in the middle of the uppercase letter "X" (cap height).

Special alignments, where the horizontal alignment is always in the center of
the text:

- ALIGNED: text is scaled to match the given `length`, scales x- and
  y-direction by the same factor.
- FIT: text is scaled to match the given `length`, but scales only in
  x-direction.
- MIDDLE: insertion point is the center of the total height (cap height +
  descender height) without scaling, the `length` argument is ignored.

Font Face Definition
--------------------

A font face is defined by the Matplotlib compatible
:class:`~ezdxf.tools.fonts.FontFace` object by ``font-family``, ``font-style``,
``font-stretch`` and ``font-weight``.

.. seealso::

    - :ref:`font_anatomy`
    - :ref:`font_properties`


String Functions
----------------

.. autofunction:: make_path_from_str

.. autofunction:: make_paths_from_str

.. autofunction:: make_hatches_from_str

Entity Functions
----------------

.. autoclass:: Kind

.. autofunction:: virtual_entities

.. autofunction:: explode

.. autofunction:: make_path_from_entity

.. autofunction:: make_paths_from_entity

.. _Matplotlib: https://matplotlib.org