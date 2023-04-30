.. module:: ezdxf.addons.text2path

text2path
=========

Tools to convert text strings and text based DXF entities into outer- and inner
linear paths as :class:`~ezdxf.path.Path` objects. At the moment only the TEXT and the
ATTRIB entity can be converted into paths and hatches.

.. versionadded:: 1.1

    Text rendering is done by the `fontTools`_ package, which is a hard dependency of
    `ezdxf`. Support for stroke fonts, these are the basic vector fonts included in CAD
    applications, like .shx, .shp or .lff fonts. These fonts cannot be rendered
    as HATCH entities.

    The required font files are not included with `ezdxf` as they are copyrighted or,
    in the case of the LibreCAD font format, licensed under the "GPL v2 and later".
    Set the paths to such stroke fonts in the config file, see option
    :attr:`ezdxf.options.support_dirs`:

    .. code-block:: ini

        [core]
        support_dirs =
            "C:\Program Files\Bricsys\BricsCAD V23 en_US\Fonts",
            ~/shx_fonts,
            ~/shp_fonts,
            ~/lff_fonts,




Don't expect a 100% match compared to CAD applications but the results with `fontTools`
are better than the previous `Matplotlib` renderings.

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

.. _fontTools: https://pypi.org/project/fonttools/