.. _howto_fonts:

Fonts
=====

Rendering SHX Fonts
-------------------

The SHX font format is not documented nor supported by many libraries/packages
like `Matplotlib` and `Qt`, therefore only SHX fonts which have corresponding
TTF-fonts can be rendered by these backends. The mapping from/to SHX/TTF fonts
is hard coded in the source code file: `ezdxf/tools/fonts.py`_

Rebuild Internal Font Cache
---------------------------

`Ezdxf` uses Matplotlib to manage fonts and caches the collected information.
If you wanna use new installed fonts which are not included in the default
cache files of `ezdxf` you have to rebuild the cache files:

.. code-block:: Python

    import ezdxf
    from ezdxf.tools import fonts

    # xdg_path() returns "$XDG_CACHE_HOME/ezdxf" or "~/.cache/ezdxf" if
    # $XDG_CACHE_HOME is not set
    font_cache_dir = ezdxf.options.xdg_path("XDG_CACHE_HOME", ".cache")
    fonts.build_system_font_cache(path=font_cache_dir)
    ezdxf.options.font_cache_directory = font_cache_dir
    # Save changes to the default config file "~/.config/ezdxf/ezdxf.ini"
    # to load the font cache always from the new location.
    ezdxf.options.write_home_config()


For more information see the :mod:`ezdxf.options` and the
:mod:`ezdxf.tools.fonts` module.

Matplotlib Doesn't Find Fonts
-----------------------------

If `Matplotlib` does not find an installed font and rebuilding the matplotlib
font cache does not help, deleting the cache file ``~/.matplotlib/fontlist-v330.json``
(or similar file in newer versions) may help.

For more information see the :mod:`ezdxf.tools.fonts` module.

.. _ezdxf/tools/fonts.py: https://github.com/mozman/ezdxf/blob/6670af2ac9931fc5b429c80299d2d5f72dfaf7d2/src/ezdxf/tools/fonts.py