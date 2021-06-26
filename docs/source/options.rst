Options Module
==============

Configuration file support was added in version v0.16.5. The configuration files
are loaded from the user home directory as "~/.ezdxf/ezdxf.ini", the current
work directory as "./ezdxf.ini" and the file specified by the environment
variable ``EZDXF_CONFIG_FILE``.

INI File Structure:

.. code:: INI

    [CORE]
    test_files = D:\Source\dxftest
    font_cache_directory =
    auto_load_fonts = true
    load_proxy_graphics = true
    store_proxy_graphics = true
    log_unprocessed_tags = true
    filter_invalid_xdata_group_codes = true
    write_fixed_meta_data_for_testing = false
    default_text_style = OpenSans
    default_dimension_text_style = OpenSansCondensed-Light

    [DXF STRUCTURE BROWSER]
    text_editor = C:\Program Files\Notepad++\notepad++.exe
    goto_line_argument = -n{num}


.. module:: ezdxf.options

Global options stored in :mod:`ezdxf.options`

.. attribute:: config

    The :class:`ConfigParser` object.

.. attribute:: default_text_style

    Default text styles, default value is ``OpenSans``.

.. attribute:: default_dimension_text_style

    Default text style for Dimensions, default value is ``OpenSansCondensed-Light``.

.. attribute:: use_matplotlib

    Activate/deactivate Matplotlib support (e.g. for testing) if Matplotlib is
    installed, else :attr:`use_matplotlib` is always ``False``.

.. attribute:: font_cache_directory

    Set path to an external font cache directory: e.g. ``"~/.ezdxf"``

    By default the bundled font cache will be loaded.

    This example shows, how to create an external font cache in
    ``"~/.ezdxf"``. This has to be done only once after the `ezdxf` installation
    or to add new installed fonts to the cache. This requires Matplotlib:

    .. code-block:: Python

        from ezdxf.tools import fonts

        fonts.build_system_font_cache(path="~/.ezdxf")

    How to use this cached font data in your script:

    .. code-block:: Python

        from ezdxf import options, fonts

        option.font_cache_directory = "~/.ezdxf"
        # Default cache is loaded automatically, if auto load is not disabled:
        fonts.load(reload=True)

    Maybe it is better to set an environment variable before `ezdxf` is loaded::

        C:\> set EZDXF_FONT_CACHE_DIRECTORY=~/.ezdxf

.. attribute:: filter_invalid_xdata_group_codes

    Filter invalid XDATA group codes, default value is ``False``.

.. attribute:: log_unprocessed_tags

    Log unprocessed DXF tags for debugging, default value is ``True``.

.. attribute:: write_fixed_meta_data_for_testing

    Enable this option to always create same meta data for testing scenarios,
    e.g. to use a diff like tool to compare DXF documents, default is ``False``.

.. attribute:: load_proxy_graphics

    Load proxy graphics if ``True``, default is ``False``.

.. attribute:: store_proxy_graphics

    Export proxy graphics if ``True``, default is ``False``.

.. method:: preserve_proxy_graphics(state=True)

    Enable/disable proxy graphic load/store support.

.. method:: write(fp: TextIO)

    Write current configuration into given file object `fp`, the file object
    must be a writeable text file with "utf8" encoding.

.. method:: print()

    Print current configuration to `stdout`.

.. method:: write_home_config()

    Write current configuration into file "~/.ezdxf/ezdxf.ini".

.. _environment_variables:

Environment Variables
=====================

Some feature can be controlled by environment variables. Command line example
for disabling the optional C-extensions on Windows::

    C:\> set EZDXF_DISABLE_C_EXT=1

.. important::

    If you change any environment variable, you have to restart
    the Python interpreter! The C-extensions cannot be disabled by a config
    file option.

EZDXF_DISABLE_C_EXT
    Set environment variable EZDXF_DISABLE_C_EXT to ``1`` or ``True`` to disable
    the usage of C extensions implemented by Cython. Disabling the C-extensions
    can only be done on interpreter startup, before the first import of `ezdxf`.

EZDXF_TEST_FILES
    Path to the `ezdxf` test files required by some tests, for instance the
    `CADKit`_ sample files should be located in the
    "EZDXF_TEST_FILES/CADKitSamples" folder. See also config file
    ``CORE`` option ``TEST_FILES``.

EZDXF_CONFIG_FILE
    Use specified configuration file

.. _CADKit: https://cadkit.blogspot.com/p/sample-dxf-files.html?view=magazine