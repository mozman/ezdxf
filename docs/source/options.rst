Options Module
==============

Configuration file support was added in version v0.16.5. The default
config files are loaded from the user home directory as "~/.ezdxf/ezdxf.ini",
and the current working directory as "./ezdxf.ini". A custom config file can be
specified  by the environment variable ``EZDXF_CONFIG_FILE``.

The config file loading order:

1. user home directory: "~/.ezdxf/ezdxf.ini" (lowest priority)
2. working directory: "./ezdxf.ini"
3. config file specified by ``EZDXF_CONFIG_FILE`` (highest priority)

.. _config_file:

Config Files
============

Configuration files are regular INI files, managed by the standard Python
`ConfigParser`_ class.

File Structure:

.. code:: INI

    [core]
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

    [browse-command]
    text_editor = C:\Program Files\Notepad++\notepad++.exe
    goto_line_argument = -n{num}


.. module:: ezdxf.options

The global `ezdxf` options are stored in :mod:`ezdxf.options`. This is a wrapper
around the :class:`ConfigParser` class. Shortcut attributes like :attr:`test_files`
are simple properties and mMost shortcuts are read only marked by (Read only),
read and writeable attributes are marked by (Read/Write).

To change options, especially the read only attributes, you have to edit the
config file with a text editor, or set options by the :meth:`set` method and
write the current configuration into a config file.

Modify and Save Changes
-----------------------

This example shows how to change the ``test_files`` path and save the
changes into a custom config file "my.ini":

.. code-block:: Python

    import ezdxf

    test_files = Path("~/my-dxf-test-files").expand_user()
    ezdxf.options.set(
        ezdxf.options.CORE,  # section
        "test_files",  # key
        "~/my-dxf-test-files",  # value
    )
    ezdxf.options.write_file("my.ini")

.. _use_a_custom_config_file:

Use a Custom Config File
------------------------

You can specify a config file by the environment variable
``EZDXF_CONFIG_FILE``, which is loaded after the default config files.

.. code-block:: Text

    C:\> set EZDXF_CONFIG_FILE=D:\user\path\custom.ini

Custom config files are not loaded automatically like the default config files.

This example shows how to load the previous created custom config file "my.ini"
from the current working directory:

.. code-block:: Python

    import ezdxf

    ezdxf.options.read("my.ini")

That is all and because this is the last loaded config file, it overrides all
default config files and the config file specified by ``EZDXF_CONFIG_FILE``.

Functions
---------

.. function:: set(section: str, key: str, value: str)

    Set option `key` in `section` to `values` as string.

.. function:: get(section: str, key: str, default: str = "")

    Get option `key` in `section` as string.

.. function:: get_bool(section: str, key: str, default: bool = False)

    Get option `key` in `section` as bool.

.. function:: write(fp: TextIO)

    Write configuration into given file object `fp`, the file object
    must be a writeable text file with "utf8" encoding.

.. function:: write_file(filename: str = "ezdxf.ini")

    Write current configuration into file `filename`, default is "ezdxf.ini" in
    the current working directory.

.. function:: write_home_config()

    Write configuration into file "~/.ezdxf/ezdxf.ini".

.. function:: read_file(filename: str)

    Append content from config file `filename`, but does not reset the
    configuration.

.. function:: print()

    Print configuration to `stdout`.

.. function:: reset()

    Factory reset, delete config files "./ezdxf.ini" and "~/.ezdxf/ezdxf.ini".

.. function:: preserve_proxy_graphics(state=True)

    Enable/disable proxy graphic load/store support by setting the
    options ``load_proxy_graphics`` and ``store_proxy_graphics`` to `state`.

.. attribute:: loaded_config_files

    Returns the loaded config files as tuple for :class:`Path`
    objects.

Shortcut Attributes
-------------------

.. attribute:: default_text_style

    (Read only) Default text styles, default value is ``OpenSans``.

.. attribute:: default_dimension_text_style

    (Read only) Default text style for Dimensions, default value is ``OpenSansCondensed-Light``.

.. attribute:: use_matplotlib

    (Read/Write) Activate/deactivate Matplotlib support (e.g. for testing) if
    Matplotlib is installed, else :attr:`use_matplotlib` is always ``False``.

.. attribute:: font_cache_directory

    (Read/Write) Get the current font cache directory or an empty string if the
    bundled font cache is used. Expands "~" construct automatically.

    Set path to an external font cache directory: e.g. ``"~/.ezdxf"``
    By default the bundled font cache will be loaded. Expands "~" construct
    automatically.

    This example shows, how to create an external font cache in
    ``"~/.ezdxf"``. This has to be done only once after the `ezdxf` installation
    or to add new installed fonts to the cache. This requires Matplotlib:

    .. code-block:: Python

        import ezdxf
        from ezdxf.tools import fonts

        font_cache_dir = "~/.ezdxf"
        fonts.build_system_font_cache(path=font_cache_dir)
        ezdxf.options.font_cache_directory = font_cache_dir
        # Save changes to the user config file "~/.ezdxf/ezdxf.ini" to load
        # the font cache always from the new location.
        ezdxf.options.write_home_config()


.. attribute:: filter_invalid_xdata_group_codes

    (Read only) Filter invalid XDATA group codes, default value is ``False``.

.. attribute:: log_unprocessed_tags

    (Read/Write) Log unprocessed DXF tags for debugging, default value is
    ``True``.

.. attribute:: write_fixed_meta_data_for_testing

    (Read/Write) Enable this option to always create same meta data for testing
    scenarios, e.g. to use a diff like tool to compare DXF documents,
    default is ``False``.

.. attribute:: load_proxy_graphics

    (Read only) Load proxy graphics if ``True``, default is ``False``.

.. attribute:: store_proxy_graphics

    (Read only)  Export proxy graphics if ``True``, default is ``False``.

.. attribute:: test_files

    (Read only) Returns the path to the `ezdxf` test files, expands "~" construct
    automatically.

.. attribute:: test_files_path

    (Read only) Path to test files as :class:`pathlib.Path` object.


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
.. _ConfigParser: https://docs.python.org/3/library/configparser.html