.. _howto_fonts:

Fonts
=====

Rendering SHX Fonts
-------------------

The SHX font format is not documented nor supported by many libraries/packages
like `Matplotlib` and `Qt`, therefore only SHX fonts which have corresponding
TTF-fonts can be rendered by these backends. The mapping from/to SHX/TTF fonts
is hard coded in the source code file: `fonts.py`_

Since `ezdxf` v1.1 is the rendering of SHX fonts supported if the path to these fonts 
is added to the ``support_dirs`` in the :ref:`config_files`.

Adding New Font Directories
---------------------------

When you add new directories to the ``support_dirs`` in your config file, you have to
rebuild the font cache to use these fonts with `ezdxf`, see section `Rebuild Font Manager Cache`_


Adding New Fonts
----------------

When you add new fonts to any of the support directories, you have to rebuild the font
cache to use these fonts with `ezdxf`, see section `Rebuild Font Manager Cache`_

Rebuild Font Manager Cache
--------------------------

If you want to use new installed fonts or fonts from a new added font directory which is
not included in the current cache file of `ezdxf` you have to rebuild the cache file:

.. code-block:: Python

    import ezdxf
    from ezdxf.fonts import fonts

    fonts.build_system_font_cache()

or call the `ezdxf` launcher to do that::

    ezdxf --fonts


.. _fonts.py: https://github.com/mozman/ezdxf/blob/master/src/ezdxf/fonts/fonts.py