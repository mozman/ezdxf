Global Options
--------------

.. module:: ezdxf.options

Global options stored in :mod:`ezdxf.options`

.. attribute:: default_text_style

    Default text styles, default value is ``OpenSans``.

.. attribute:: default_dimension_text_style

    Default text style for Dimensions, default value is ``OpenSansCondensed-Light``.

.. attribute:: use_matplotlib_font_support

    Active the Matplotlib font support to calculate font metrics:
    This requires a working Matplotlib installation else an ``ImportError``
    exception will be raised sooner or later.
    Default is ``False``

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

.. attribute:: load_proxy_graphics

    Load proxy graphics if ``True``, default is ``False``.

.. attribute:: store_proxy_graphics

    Export proxy graphics if ``True``, default is ``False``.

.. attribute:: write_fixed_meta_data_for_testing

    Enable this option to always create same meta data for testing scenarios,
    e.g. to use a diff like tool to compare DXF documents.

.. method:: preserve_proxy_graphics()

    Enable proxy graphic load/store support.
