Global Options
==============

.. module:: ezdxf.options

Options Module
--------------

Global options stored in :mod:`ezdxf.options`

.. attribute:: default_text_style

    Default text styles, default value is ``OpenSans``.

.. attribute:: default_dimension_text_style

    Default text style for Dimensions, default value is ``OpenSansCondensed-Light``.

.. attribute:: use_matplotlib

    Activate/deactivate Matplotlib support (e.g. for testing) if Matplotlib is
    installed, else :attr:`use_matplotlib` is always ``False``.

.. attribute:: font_cache_directory

    Set path to an external font cache directory: e.g. ``"~/.ezdxf"``

    This example shows, how to create an external font cache in
    ``"~/.ezdxf"``. This has to be done only once or to add
    new installed fonts to the cache and this also requires Matplotlib:

    .. code-block:: Python

        from ezdxf.tools import fonts
        from ezdxf import options

        options.font_cache_directory = "~/.ezdxf"
        fonts.build_system_font_cache()

    How to use this cached font data in your script:

    .. code-block:: Python

        from ezdxf import options, fonts

        option.font_cache_directory = "~/.ezdxf"
        fonts.load()

.. attribute:: filter_invalid_xdata_group_codes

    Check for invalid XDATA group codes, default value is ``False``

.. attribute:: log_unprocessed_tags

    Log unprocessed DXF tags for debugging, default value is ``True``

.. attribute:: write_fixed_meta_data_for_testing

    Enable this option to always create same meta data for testing scenarios,
    e.g. to use a diff like tool to compare DXF documents, default is ``False``.

.. attribute:: load_proxy_graphics

    Load proxy graphics if ``True``, default is ``False``.

.. attribute:: store_proxy_graphics

    Export proxy graphics if ``True``, default is ``False``.

.. method:: preserve_proxy_graphics()

    Enable proxy graphic load/store support.

Environment Variables
---------------------

Some feature can be controlled by environment variables. Example for
disabling the optional C-extensions on Windows:

.. code-block::

    set EZDXF_DISABLE_C_EXT=1


.. important::

    If you change any environment variable, you have to restart
    the Python interpreter!

EZDXF_DISABLE_C_EXT
    Set environment variable EZDXF_DISABLE_C_EXT to ``1`` or ``True`` to disable
    the usage of C extensions implemented by Cython. Disabling the C-extensions
    can only be done on interpreter startup, before the first import of `ezdxf`.

EZDXF_AUTO_LOAD_FONTS
    Set EZDXF_AUTO_LOAD_FONTS to ``0`` or ``False`` to deactivate font cache
    loading at startup, if this slows down the interpreter startup too much and
    font measuring is not important to you. The font cache can always be loaded
    manually by calling :func:`ezdxf.fonts.load`

EZDXF_TEST_FILES
    Path to the `ezdxf` test files required by some tests, for instance the
    `CADKit`_ sample files should be located in the
    "EZDXF_TEST_FILES/CADKitSamples" folder.

.. _CADKit: https://cadkit.blogspot.com/p/sample-dxf-files.html?view=magazine