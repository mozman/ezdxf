Fonts
=====

.. module:: ezdxf.fonts.fonts

The module :mod:`ezdxf.fonts.fonts` manages the internal usage of fonts and
has no relation how the DXF formats manages text styles.

.. seealso::

    The :class:`~ezdxf.entities.Textstyle` entity, the DXF way to define fonts.


.. versionadded:: 1.1

Since `ezdxf` v1.1 text rendering is done by the `fontTools`_ package.
Support for stroke fonts, these are the basic vector fonts included in CAD
applications, like .shx, .shp or .lff fonts was also added.

None of the required font files (.ttf, .ttc, .otf, .shx, .shp or .lff) are included in
`ezdxf` as they are copyrighted or, in the case of the LibreCAD font format (.lff),
licensed under the "GPL v2 and later".


Font Locations
--------------

TrueType Fonts
~~~~~~~~~~~~~~

The font manager searches the following directories recursively for .ttf, .ttc and .otf
font files.

- Windows:
    - ~/AppData/Local/Microsoft/Windows/Fonts
    - <SystemRoot>/Fonts

- Linux and other \*nix like systems:
    - /usr/share/fonts
    - /usr/local/share/fonts
    - ~/.fonts
    - ~/.local/share/fonts
    - ~/.local/share/texmf/fonts

- macOS:
    - /Library/Fonts

The `fc-list` command on Linux shows all available fonts and their location.

The default font is selected in the following order, if none of them is available on
your system - install one of them, the open source fonts can be found in the github
repository in the folder `ezdxf/fonts`_.

- Arial.ttf
- DejaVuSansCondensed.ttf
- DejaVuSans.ttf
- LiberationSans-Regular.ttf
- OpenSans-Regular.ttf

Basic Stroke Fonts
~~~~~~~~~~~~~~~~~~

There is no universal way to find the basic stroke fonts of CAD applications on a
system, beside scanning all drives. Set the paths to the stroke fonts in your config
file manually to tell `ezdxf` where to search for them, all paths are search recursively,
see also option :attr:`ezdxf.options.support_dirs`:

.. code-block:: ini

    [core]
    support_dirs =
        "C:\Program Files\Bricsys\BricsCAD V23 en_US\Fonts",
        ~/shx_fonts,
        ~/shp_fonts,
        ~/lff_fonts,

The .shx fonts can be found on the internet but be aware that they are not free as all
websites claim. The LibreCAD font files (.llf) can be downloaded from their github
repository: https://github.com/LibreCAD/LibreCAD/tree/master/librecad/support/fonts

Font Caching
------------

The fonts available on a system are cached automatically, the cache has to be rebuild
to recognize new installed fonts by :func:`build_system_font_cache`. The cache is stored
in the users home directory "~/.cache/ezdxf" or the directory specified by the
environment variable "XDG_CACHE_HOME".


Functions
---------

.. autofunction:: make_font

.. autofunction:: get_font_face

.. autofunction:: find_font_face

.. autofunction:: find_font_file_name

.. autofunction:: find_best_match

.. autofunction:: get_entity_font_face

.. autofunction:: get_font_measurements

.. autofunction:: build_system_font_cache()

.. autofunction:: load

.. autofunction:: sideload_ttf

Classes
-------

.. autoclass:: AbstractFont

    .. attribute:: name

        The font filename e.g. "LiberationSans-Regular.ttf"

    .. attribute:: font_render_type

        The font type, see enum :class:`FontRenderType`

    .. attribute:: measurement

        The :class:`FontMeasurements` data.

    .. automethod:: text_width

    .. automethod:: text_width_ex

    .. automethod:: text_path

    .. automethod:: text_path_ex

    .. automethod:: space_width


.. autoclass:: MonospaceFont

.. autoclass:: TrueTypeFont

.. autoclass:: ShapeFileFont

.. autoclass:: LibreCadFont


.. _font_anatomy:

Font Anatomy
------------

- A Visual Guide to the Anatomy of Typography: https://visme.co/blog/type-anatomy/
- Anatomy of a Character: https://www.fonts.com/content/learning/fontology/level-1/type-anatomy/anatomy

.. _font_properties:

Font Properties
---------------

DXF to store fonts in the :class:`~ezdxf.entities.Textstyle` entity as TTF file name e.g.
"LiberationSans-Regular.ttf".

The :class:`FontFace` class can be used to specify a font in a more generic way:

family
    font name e.g. "Liberation Sans" or "Arial", may a generic font family name, either "serif",
    "sans-serif" or "monospace"

style
    "Regular", "Italic", "Oblique", "Bold", "BoldOblique", ...

width
    (usWidthClass) A numeric value in the range 0-9

    === ==================
    1   UltraCondensed
    2   ExtraCondensed
    3   Condensed
    4   SemiCondensed
    5   Normal or Medium
    6   SemiExpanded
    7   Expanded
    8   ExtraExpanded
    9   UltraExpanded
    === ==================

weight
    (usWeightClass) A numeric value in the range 0-1000

    === =============
    100 Thin
    200 ExtraLight
    300 Light
    400 Normal
    500 Medium
    600 SemiBold
    700 Bold
    800 ExtraBold
    900 Black
    === =============

.. seealso::

    - W3C: https://www.w3.org/TR/2018/REC-css-fonts-3-20180920/

.. class:: FontRenderType

    Enumeration of font render type.

    .. attribute:: STROKE

        Basic stroke font, can only be rendered as linear paths.

    .. attribute:: OUTLINE

        TrueType or similar font, can be rendered as filled paths or as outline strokes.


.. autoclass:: FontFace

    .. attribute:: filename

        font file name without parent directories as string, e.g. "arial.ttf"

    .. attribute:: family

        Family name as string, the default value is "sans-serif"

    .. attribute:: style

        Font style as string, the default value is "Regular"

    .. attribute:: weight

        Font weight as int in the renge from 0-1000, the default value is 400 (Normal)

    .. autoproperty:: weight_str

    .. attribute:: width

        Font width (stretch) as int in the range from 1-9, the default value is 5 (Normal)

    .. autoproperty:: width_str

    .. autoproperty:: is_italic

    .. autoproperty:: is_oblique

    .. autoproperty:: is_bold


.. class:: FontMeasurements

    See `Font Anatomy`_ for more information.

    .. attribute:: baseline

    .. attribute:: cap_height

    .. attribute:: x_height

    .. attribute:: descender_height

    .. automethod:: scale

    .. automethod:: scale_from_baseline

    .. automethod:: shift

    .. autoproperty:: cap_top

    .. autoproperty:: x_top

    .. autoproperty:: bottom

    .. autoproperty:: total_height


.. _ezdxf/fonts: https://github.com/mozman/ezdxf/tree/master/fonts
.. _fontTools: https://pypi.org/project/fonttools/