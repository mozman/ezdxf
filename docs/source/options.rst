.. _global_options:

Global Options Object
=====================

.. module:: ezdxf.options

The global `ezdxf` options are stored in the object :mod:`ezdxf.options`.

Recommended usage of the global :attr:`options` object::

    import ezdxf

    value = ezdxf.options.attribute

The :attr:`options` object uses the Standard Python class :class:`ConfigParser`
to manage the configuration. Shortcut attributes like :attr:`test_files` are
simple properties and most shortcuts are read only marked by (Read only),
read and writeable attributes are marked by (Read/Write).

To change options, especially the read only attributes, you have to edit the
config file with a text editor, or set options by the :meth:`set` method and
write the current configuration into a config file.

.. _config_files:

Config Files
============

The default config files are loaded from the user home directory as
"~/.config/ezdxf/ezdxf.ini", and the current working directory as "./ezdxf.ini".
A custom config file can be specified  by the environment variable
``EZDXF_CONFIG_FILE``. Ezdxf follows the `XDG Base Directory specification`_
if the environment variable ``XDG_CONFIG_HOME`` is set.

The config file loading order:

1. user home directory: "~/.config/ezdxf/ezdxf.ini"
2. current working directory: "./ezdxf.ini"
3. config file specified by ``EZDXF_CONFIG_FILE``

A configuration file that is loaded later does not replace the previously loaded
ones, only the existing options in the newly loaded file are added to the
configuration and can overwrite existing options.

.. _config_file:

Configuration files are regular INI files, managed by the standard Python
`ConfigParser`_ class.

File Structure:

.. code:: INI

    [core]
    default_dimension_text_style = OpenSansCondensed-Light
    test_files = D:\Source\dxftest
    font_cache_directory =
    load_proxy_graphics = true
    store_proxy_graphics = true
    log_unprocessed_tags = false
    filter_invalid_xdata_group_codes = true
    write_fixed_meta_data_for_testing = false
    disable_c_ext = false

    [browse-command]
    text_editor = "C:\Program Files\Notepad++\notepad++.exe" "{filename}" -n{num}

Modify and Save Changes
-----------------------

This code shows how to get and set values of the underlying :class:`ConfigParser`
object, but use the shortcut attributes if available:

.. code-block:: Python

    # Set options, value has to ba a str, use "true"/"false" for boolean values
    ezdxf.options.set(section, key, value)

    # Get option as string
    value = ezdxf.options.get(section, key, default="")

    # Special getter for boolean, int and float
    value = ezdxf.options.get_bool(section, key, default=False)
    value = ezdxf.options.get_int(section, key, default=0)
    value = ezdxf.options.get_float(section, key, default=0.0)

If you set options, they are not stored automatically in a config file, you have
to write back the config file manually:

.. code-block:: Python

    # write back the default user config file "ezdxf.ini" in the
    # user home directory
    ezdxf.options.write_home_config()

    # write back to the default config file "ezdxf.ini" in the
    # current working directory
    ezdxf.options.write_file()

    # write back to a specific config file
    ezdxf.options.write_file("my_config.ini")
    # which has to be loaded manually at startup
    ezdxf.options.read_file("my_config.ini")

This example shows how to change the :attr:`test_files` path and save the
changes into a custom config file "my_config.ini":

.. code-block:: Python

    import ezdxf

    test_files = Path("~/my-dxf-test-files").expand_user()
    ezdxf.options.set(
        ezdxf.options.CORE,  # section
        "test_files",  # key
        "~/my-dxf-test-files",  # value
    )
    ezdxf.options.write_file("my_config.ini")

.. _use_a_custom_config_file:

Use a Custom Config File
------------------------

You can specify a config file by the environment variable
``EZDXF_CONFIG_FILE``, which is loaded after the default config files.

.. code-block:: Text

    C:\> set EZDXF_CONFIG_FILE=D:\user\path\custom.ini

Custom config files are not loaded automatically like the default config files.

This example shows how to load the previous created custom config file
"my_config.ini" from the current working directory:

.. code-block:: Python

    import ezdxf

    ezdxf.options.read("my_config.ini")

That is all and because this is the last loaded config file, it overrides all
default config files and the config file specified by ``EZDXF_CONFIG_FILE``.

Functions
---------

.. function:: set(section: str, key: str, value: str)

    Set option `key` in `section` to `values` as ``str``.

.. function:: get(section: str, key: str, default: str = "") -> str

    Get option `key` in `section` as string.

.. function:: get_bool(section: str, key: str, default: bool = False) -> bool

    Get option `key` in `section` as ``bool``.

.. function:: get_int(section: str, key: str, default: int = 0) -> int

    Get option `key` in `section` as ``int``.

.. function:: get_float(section: str, key: str, default: float = 0.0) -> flot

    Get option `key` in `section` as ``float``.

.. function:: write(fp: TextIO)

    Write configuration into given file object `fp`, the file object
    must be a writeable text file with "utf8" encoding.

.. function:: write_file(filename: str = "ezdxf.ini")

    Write current configuration into file `filename`, default is "ezdxf.ini" in
    the current working directory.

.. function:: write_home_config()

    Write configuration into file "~/.config/ezdxf/ezdxf.ini",
    ``$XDG_CONFIG_HOME`` is supported if set.

.. function:: read_file(filename: str)

    Append content from config file `filename`, but does not reset the
    configuration.

.. function:: print()

    Print configuration to `stdout`.

.. function:: reset()

    Reset options to factory default values.

.. function:: delete_default_config_files()

    Delete the default config files "ezdxf.ini" in the current working and in
    the user home directory "~/.config/ezdxf", ``$XDG_CONFIG_HOME`` is supported
    if set.

.. function:: preserve_proxy_graphics(state=True)

    Enable/disable proxy graphic load/store support by setting the
    options ``load_proxy_graphics`` and ``store_proxy_graphics`` to `state`.

.. attribute:: loaded_config_files

    Read only property of loaded config files as tuple for :class:`Path`
    objects.

Core Options
------------

For all core options the section name is ``core``.



Default Dimension Text Style
++++++++++++++++++++++++++++

The default dimension text style is used by the DIMENSION renderer of `ezdxf`,
if the specified text style exist in the STYLE table. To use any of the default
style of `ezdxf` you have to setup the styles at the creation of the DXF
document: :code:`ezdxf.new(setup=True)`, or setup the `ezdxf` default styles
for a loaded DXF document:

.. code-block:: Python

    import ezdxf
    from ezdxf.tool.standard import setup_drawing

    doc = ezdxf.readfile("your.dxf")
    setup_drawing(doc)

Config file key: ``default_dimension_text_style``

Shortcut attribute:

.. attribute:: default_dimension_text_style

    (Read/Write) Get/Set default text style for DIMENSION rendering, default
    value is ``OpenSansCondensed-Light``.

Font Cache Directory
++++++++++++++++++++

`Ezdxf` has a bundled font cache to have faster access to font metrics.
This font cache includes only fonts installed on the developing workstation.
To add the fonts of your computer to this cache, you have to create your
own external font cache. This has to be done only once after `ezdxf` was
installed, or to add new installed fonts to the cache, and this requires the
`Matplotlib` package.

This example shows, how to create an external font cache in the recommended
directory of the `XDG Base Directory specification`_: ``"~/.cache/ezdxf"``.

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

Config file key: ``font_cache_directory``

Shortcut attribute:

.. attribute:: font_cache_directory

    (Read/Write) Get/set the font cache directory, if the directory is an empty
    string, the bundled font cache is used. Expands "~" construct automatically.

Load Proxy Graphic
++++++++++++++++++

Proxy graphics are not essential for DXF files, but they can provide a simple
graphical representation for complex entities, but extra memory is needed to
store this information. You can save some memory by not loading the proxy
graphic, but the proxy graphic is lost if you write back the DXF file.

The current version of `ezdxf` uses this proxy graphic to render MLEADER
entities by the :mod:`~ezdxf.addons.drawing` add-on.

Config file key: ``load_proxy_graphics``

Shortcut attribute:

.. attribute:: load_proxy_graphics

    (Read/Write) Load proxy graphics if ``True``, default is ``True``.

Store Proxy Graphic
+++++++++++++++++++

Prevent exporting proxy graphics if set to ``False``.

Config file key: ``store_proxy_graphics``

Shortcut attribute:

.. attribute:: store_proxy_graphics

    (Read/Write)  Export proxy graphics if ``True``, default is ``True``.

Support Directories
+++++++++++++++++++

Search directories for support files:

- plot style tables, the CTB or STB pen assignment files
- shape font files of type SHX or SHP

Config file key: ``support_dirs``

Shortcut attribute:

.. attribute:: support_dirs

    (Read/Write) Search directories as list of strings.

Debugging Options
-----------------

For all debugging options the section name is ``core``.

Test Files
++++++++++

Path to test files. Some of the `CADKit`_ test files are used by the
integration tests, these files should be located in the
:code:`ezdxf.options.test_files_path / "CADKitSamples"` folder.

Config file key: ``test_files``

Shortcut attributes:

.. attribute:: test_files

    (Read only) Returns the path to the `ezdxf` test files as ``str``,
    expands "~" construct automatically.

.. attribute:: test_files_path

    (Read only) Path to test files as :class:`pathlib.Path` object.


Filter Invalid XDATA Group Codes
++++++++++++++++++++++++++++++++

Only a very limited set of group codes is valid in the XDATA section and
AutoCAD is very picky about that. `Ezdxf` removes invalid XDATA group codes
if this option is set to ``True``, but this needs processing time, which is
wasted if you get your DXF files from trusted sources like AutoCAD or BricsCAD.

Config file key: ``filter_invalid_xdata_group_codes``

.. attribute:: filter_invalid_xdata_group_codes

    (Read only) Filter invalid XDATA group codes, default value is ``True``.

Log Unprocessed Tags
++++++++++++++++++++

Logs unprocessed DXF tags, this helps to find new and undocumented DXF features.

Config file key: ``log_unprocessed_tags``

.. attribute:: log_unprocessed_tags

    (Read/Write) Log unprocessed DXF tags for debugging, default value is
    ``False``.

Write Fixed Meta Data for Testing
+++++++++++++++++++++++++++++++++

Write the DXF files with fixed meta data to test your DXF files by a diff-like
command, this is necessary to get always the same meta data like the saving
time stored in the HEADER section. This may not work across different `ezdxf`
versions!

Config file key: ``write_fixed_meta_data_for_testing``

.. attribute:: write_fixed_meta_data_for_testing

    (Read/Write) Enable this option to always create same meta data for testing
    scenarios, e.g. to use a diff-like tool to compare DXF documents,
    default is ``False``.

Disable C-Extension
+++++++++++++++++++

It is possible to deactivate the optional C-extensions if there are any issues
with the C-extensions. This has to be done in a default config file or by
environment variable before the first import of `ezdxf`. For ``pypy3`` the
C-extensions are always disabled, because the JIT compiled Python code is
much faster.

.. important::

    This option works only in the **default config files**, user config files which
    are loaded by :func:`ezdxf.options.read_file()` cannot disable the C-Extensions,
    because at this point the setup process of `ezdxf` is already finished!

Config file key: ``disable_c_ext``

.. attribute:: disable_c_ext

    (Read only) This option disables the C-extensions if ``True``.
    This can only be done before the first import of `ezdxf` by using a config
    file or the environment variable ``EZDXF_DISABLE_C_EXT``.

Use C-Extensions
++++++++++++++++

.. attribute:: use_c_ext

    (Read only) Shows the actual state of C-extensions usage.

Use Matplotlib
++++++++++++++

This option can deactivate Matplotlib support for testing. This option is not
stored in the :class:`ConfigParser` object and is therefore not supported by
config files!

Only access by attribute is supported:

.. attribute:: use_matplotlib

    (Read/Write) Activate/deactivate Matplotlib support (e.g. for testing) if
    Matplotlib is installed, otherwise :attr:`use_matplotlib` is always ``False``.


.. _environment_variables:

Environment Variables
=====================

Some feature can be controlled by environment variables. Command line example
for disabling the optional C-extensions on Windows::

    C:\> set EZDXF_DISABLE_C_EXT=1

.. important::

    If you change any environment variable, you have to restart
    the Python interpreter!

EZDXF_DISABLE_C_EXT
    Set environment variable ``EZDXF_DISABLE_C_EXT`` to ``1`` or ``True`` to
    disable the usage of the C-extensions.

EZDXF_TEST_FILES
    Path to the `ezdxf` test files required by some tests, for instance the
    `CADKit`_ sample files should be located in the
    ``EZDXF_TEST_FILES/CADKitSamples`` folder. See also option
    :attr:`ezdxf.options.test_files`.

EZDXF_CONFIG_FILE
    Specifies a user config file which will be loaded automatically after the
    default config files at the first import of `ezdxf`.

.. _CADKit: https://cadkit.blogspot.com/p/sample-dxf-files.html?view=magazine
.. _ConfigParser: https://docs.python.org/3/library/configparser.html
.. _XDG Base Directory specification: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html