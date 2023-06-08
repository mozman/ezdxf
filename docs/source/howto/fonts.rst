.. _howto_fonts:

Fonts
=====

Rendering SHX Fonts
-------------------

The SHX font format is not documented nor supported by many libraries/packages
like `Matplotlib` and `Qt`, therefore only SHX fonts which have corresponding
TTF-fonts can be rendered by these backends. The mapping from/to SHX/TTF fonts
is hard coded in the source code file: `ezdxf/tools/fonts.py`_

Rebuild Font Manager Cache
--------------------------

If you wanna use new installed fonts which are not included in the current
cache file of `ezdxf` you have to rebuild the cache file:

.. code-block:: Python

    import ezdxf
    from ezdxf.tools import fonts

    fonts.build_system_font_cache()

or call the `ezdxf` launcher to do that::

    ezdxf --fonts


.. _ezdxf/tools/fonts.py: https://github.com/mozman/ezdxf/blob/6670af2ac9931fc5b429c80299d2d5f72dfaf7d2/src/ezdxf/tools/fonts.py