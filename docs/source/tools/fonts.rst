Fonts
=====

.. module:: ezdxf.tools.fonts

The module :mod:`ezdxf.tools.fonts` manages the internal usage of fonts and
has no relation how the DXF formats manages text styles.

.. seealso::

    The :class:`~ezdxf.entities.Textstyle` entity, the DXF way to define fonts.

The tools in this module provide abstractions to get font measurements with and
without the optional Matplotlib package.

For a proper text rendering the font measurements are required. `Ezdxf` has a
lean approach to package dependencies, therefore the rendering results without
support from the optional Matplotlib package are not very good.

Font Classes
------------

.. autofunction:: make_font

.. autoclass:: AbstractFont

.. autoclass:: MonospaceFont

    .. automethod:: text_width

    .. automethod:: space_width


.. autoclass:: MatplotlibFont

    .. automethod:: text_width

    .. automethod:: space_width

.. _font_anatomy:

Font Anatomy
------------

- A Visual Guide to the Anatomy of Typography: https://visme.co/blog/type-anatomy/
- Anatomy of a Character: https://www.fonts.com/content/learning/fontology/level-1/type-anatomy/anatomy

.. _font_properties:

Font Properties
---------------

The default way of DXF to store fonts in the :class:`~ezdxf.entities.Textstyle`
entity by using the raw TTF file name is not the way how most render backends
select fonts. 

The render backends and web technologies select the fonts by their properties.
This list shows the Matplotlib properties:

family
    List of font names in decreasing order of priority.
    The items may include a generic font family name, either
    "serif", "sans-serif", "cursive", "fantasy", or "monospace".

style
    "normal" ("regular"), "italic" or "oblique"

stretch
    A numeric value in the range 0-1000 or one of
    "ultra-condensed", "extra-condensed", "condensed",
    "semi-condensed", "normal", "semi-expanded", "expanded",
    "extra-expanded" or "ultra-expanded"

weight
    A numeric value in the range 0-1000 or one of
    "ultralight", "light", "normal", "regular", "book", "medium",
    "roman", "semibold", "demibold", "demi", "bold", "heavy",
    "extra bold", "black".

This way the backend can choose a similar font if the original font is not
available.

.. seealso::

    - Matplotlib: https://matplotlib.org/stable/api/font_manager_api.html
    - PyQt: https://doc.qt.io/archives/qtforpython-5.12/PySide2/QtGui/QFont.html
    - W3C: https://www.w3.org/TR/2018/REC-css-fonts-3-20180920/


.. autoclass:: FontFace

    This is the equivalent to the Matplotlib :class:`FontProperties` class.

    .. attribute:: ttf

        Raw font file name as string, e.g. "arial.ttf"

    .. attribute:: family

        Family name as string, the default value is "sans-serif"

    .. attribute:: style

        Font style as string, the default value is "normal"

    .. attribute:: stretch

        Font stretch as string, the default value is "normal"

    .. attribute:: weight

        Font weight as string, the default value is "normal"

    .. property:: is_italic

        Returns ``True`` if font face is italic

    .. property:: is_oblique

        Returns ``True`` if font face is oblique

    .. property:: is_bold

        Returns ``True`` if font face weight > 400

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

Font Caching
------------

`Ezdxf` uses Matplotlib to manage fonts and caches the collected information.
The default installation of `ezdxf` provides a basic set of font properties.
It is possible to create your own font cache specific for your system:
see :attr:`ezdxf.options.font_cache_directory`

The font cache is loaded automatically at startup, if not disabled by setting
environment variable ``EZDXF_AUTO_LOAD_FONTS`` to ``False``:
see :ref:`environment_variables`

.. autofunction:: get_font_face

.. autofunction:: get_font_measurements

.. autofunction:: build_system_font_cache

.. autofunction:: load

.. autofunction:: save

