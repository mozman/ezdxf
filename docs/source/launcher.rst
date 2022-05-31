Launcher
========

The command line script `ezdxf` launches various sub-commands:

=========== ====================================================================
``pp``      DXF pretty printer, replacement for the previous `dxfpp` command
``audit``   Audit and repair DXF files
``draw``    Draw and convert DXF files by the Matplotlib backend
``view``    PyQt DXF file viewer
``browse``  PyQt DXF structure browser for DXF debugging and curious people
``strip``   Strip comments and THUMBNAILIMAGE section from DXF files
``config``  Manage config files
``info``    Show information and optional stats of DXF files as loaded by ezdxf
=========== ====================================================================

The help option ``-h`` is supported by the main script and all sub-commands:

.. code-block:: Text

    C:\> ezdxf -h
    usage: ezdxf [-h] [-V] [-v] [--config CONFIG] [--log LOG]
                 {pp,audit,draw,view,browse,strip,config} ...

    Command launcher for the Python package "ezdxf":
    https://pypi.org/project/ezdxf/

    positional arguments:
      {pp,audit,draw,view,browse,strip}
        pp                  pretty print DXF files as HTML file
        audit               audit and repair DXF files
        draw                draw and convert DXF files by Matplotlib
        view                view DXF files by the PyQt viewer
        browse              browse DXF file structure
        strip               strip comments from DXF files
        config              manage config files
        info                show information and optional stats of DXF files loaded by ezdxf,
                            this may not represent the original content of the file, use the
                            browse command to see the original content

    optional arguments:
      -h, --help            show this help message and exit
      -V, --version         show version and exit
      -v, --verbose         give more output
      --config CONFIG       path to a config file
      --log LOG             path to a verbose appending log

.. note::

    The ``ezdxf`` script  is the only executable script installed on the user
    system, if installed by ``pip``, the ``dxfpp`` script is not included anymore.

Pretty Printer
--------------

Pretty print the DXF text content as HTML file and open the file in the
default web browser:

.. code-block:: Text

    C:\> ezdxf pp -o gear.dxf


.. image:: gfx/gear-pp.png
   :align: center

Print help:

.. code-block:: Text

    C:\> ezdxf pp -h
    usage: ezdxf pp [-h] [-o] [-r] [-x] [-l] [-s SECTIONS] FILE [FILE ...]

    positional arguments:
      FILE                  DXF files pretty print

    optional arguments:
      -h, --help            show this help message and exit
      -o, --open            open generated HTML file by the default web browser
      -r, --raw             raw mode, no DXF structure interpretation
      -x, --nocompile       don't compile points coordinates into single tags (only in raw mode)
      -l, --legacy          legacy mode, reorder DXF point coordinates
      -s SECTIONS, --sections SECTIONS
                            choose sections to include and their order, h=HEADER, c=CLASSES,
                            t=TABLES, b=BLOCKS, e=ENTITIES, o=OBJECTS

Auditor
-------

Audit and recover the DXF file "gear.dxf" and save the recovered version
as "gear.rec.dxf":

.. code-block:: Text

    C:\> ezdxf audit -s gear.dxf

    auditing file: gear.dxf
    No errors found.
    Saved recovered file as: gear.rec.dxf

Print help:

.. code-block:: Text

    C:\> ezdxf audit -h
    usage: ezdxf audit [-h] [-s] FILE [FILE ...]

    positional arguments:
      FILE        audit DXF files

    optional arguments:
      -h, --help  show this help message and exit
      -s, --save  save recovered files with extension ".rec.dxf"

Draw
----

Convert the DXF file "gear.dxf" into a SVG file by the *Matplotlib* backend:

.. code-block:: Text

    C:\> ezdxf draw -o gear.svg gear.dxf

The "gear.svg" created by the *Matplotlib* backend:

.. image:: gfx/gear.svg
   :align: center

Show all output formats supported by the *Matplotlib* backend
on your system. This output may vary:

.. code-block:: Text

    C:\> ezdxf draw --formats
    eps: Encapsulated Postscript
    jpg: Joint Photographic Experts Group
    jpeg: Joint Photographic Experts Group
    pdf: Portable Document Format
    pgf: PGF code for LaTeX
    png: Portable Network Graphics
    ps: Postscript
    raw: Raw RGBA bitmap
    rgba: Raw RGBA bitmap
    svg: Scalable Vector Graphics
    svgz: Scalable Vector Graphics
    tif: Tagged Image File Format
    tiff: Tagged Image File Format

Print help:

.. code-block:: Text

    C:\> ezdxf draw -h
    usage: ezdxf draw [-h] [--formats] [--layout LAYOUT] [--all-layers-visible]
                      [--all-entities-visible] [-o OUT] [--dpi DPI]
                      [--ltype {approximate,accurate}]
                      [FILE]

    positional arguments:
      FILE                  DXF file to view or convert

    optional arguments:
      -h, --help            show this help message and exit
      --formats             show all supported export formats and exit
      --layout LAYOUT       select the layout to draw
      --all-layers-visible  draw all layers including the ones marked as invisible
      --all-entities-visible
                            draw all entities including the ones marked as
                            invisible (some entities are individually marked as
                            invisible even if the layer is visible)
      -o OUT, --out OUT     output filename for export
      --dpi DPI             target render resolution, default is 300
      --ltype {approximate,accurate}
                            select the line type rendering method, default is
                            approximate. Approximate uses the closest
                            approximation available to the backend, the accurate
                            method renders as accurately as possible but this
                            approach is slower.

View
----

View the DXF file "gear.dxf" by the *PyQt* backend:

.. code-block:: Text

    C:\> ezdxf view gear.dxf

.. image:: gfx/gear-qt-backend.png
   :align: center

Print help:

.. code-block:: Text

    C:\> ezdxf view -h
    usage: ezdxf view [-h] [--layout LAYOUT]
                      [--ltype {approximate,accurate}] [--lwscale LWSCALE]
                      [FILE]

    positional arguments:
      FILE                  DXF file to view

    optional arguments:
      -h, --help            show this help message and exit
      --layout LAYOUT       select the layout to draw
      --ltype {approximate,accurate}
                            select the line type rendering method, default
                            is approximate. Approximate uses the closest
                            approximation available to the backend, the
                            accurate method renders as accurately as
                            possible but this approach is slower.
      --lwscale LWSCALE     set custom line weight scaling, default is 0 to
                            disable line weights at all

Browse
------

Browse the internal structure of a DXF file like a file system:

.. code-block:: Text

    C:\> ezdxf browse gear.dxf


.. image:: gfx/gear-browse.png
   :align: center

.. code-block:: Text

    C:\> ezdxf browse -h
    usage: ezdxf browse [-h] [-l LINE] [-g HANDLE] [FILE]

    positional arguments:
      FILE                  DXF file to browse

    optional arguments:
      -h, --help            show this help message and exit
      -l LINE, --line LINE  go to line number
      -g HANDLE, --handle HANDLE
                            go to entity by HANDLE, HANDLE has to be a hex value without
                            any prefix like 'fefe'

The `browse` command stores options in the config file,
e.g. for the `Notepad++` on Windows:

.. code-block:: ini

    [browse-command]

    text_editor = "C:\Program Files\Notepad++\notepad++.exe" "{filename}" -n{num}
    icon_size = 32

``text_editor`` is a simple format string:
:code:`text_editor.format(filename="test.dxf", num=100)`

Quote commands including spaces and always quote the filename argument!

For `xed` on Linux Mint use (note: absolute path to executable):

.. code-block:: ini

    [browse-command]

    text_editor = /usr/bin/xed "{filename}" +{num}
    icon_size = 32

For `gedit` on Linux use (untested):

.. code-block:: ini

    [browse-command]

    text_editor = /use/bin/gedit +{num} "{filename}"
    icon_size = 32

The *browse* command opens a DXF structure browser to investigate the
internals of a DXF file without interpreting the content. The functionality of
the DXF browser is similar to the DXF `Pretty Printer`_ (*pp* command), but without
the disadvantage of creating giant HTML files. The intended usage is debugging
invalid DXF files, which can not be loaded by the :func:`ezdxf.readfile()` or
the :func:`ezdxf.recover.readfile()` functions.

Line Numbers
~~~~~~~~~~~~

The low level tag loader ignores DXF comments (group code 999). If there are
comments in the DXF file the line numbers displayed in the DXF browser are
not synchronized, use the `strip`_ command beforehand to remove all comments
from the DXF file in order to keep the line numbers synchronized.

GUI Features
~~~~~~~~~~~~

The tree view on the left shows the outline of the DXF file. The number in round
brackets on the right side of each item shows the count of structure entities
within the structure layer, the value in angle brackets on the left side is
the entity handle.

The right list view shows the entity content as DXF tags.
Structure tags (data type <ctrl>) are shown in blue, a double click on a reference
handle (datatype <ref>) jumps to the referenced entity, reference handles of
non-existent targets are shown in red.

Clicking on the first structure tag in the list opens the DXF reference provided
by Autodesk in the standard web browser.

Auto Reload
~~~~~~~~~~~

The browser automatically displays a dialog for reloading DXF files if they have
been modified by an external application.

Menus and Shortcuts
~~~~~~~~~~~~~~~~~~~

- File Menu
    - **Open DXF file...** *Ctrl+O*
    - **Reload DXF file** *Ctrl+R*
    - **Open in Text Editor** *Ctrl+T*, open the DXF file in the associated text
      editor at the current location
    - **Export DXF Entity...** *Ctrl+E*, export the current DXF entity shown in the
      list view as text file
    - **Copy selected DXF Tags to Clipboard** *Ctrl+C*, copy the current
      selected DXF tags into the clipboard
    - **Copy DXF Entity to Clipboard** *Ctrl+Shift+C*, copy all DXF tags of the
      current DXF entity shown in the list view into the clipboard
    - **Quit** *Ctrl+Q*

- Navigate Menu
    - **Go to Handle...** *Ctrl+G*
    - **Go to Line...** *Ctrl+L*
    - **Find Text...** *Ctrl+F*, opens the find text dialog
    - **Next Entity** *Ctrl+Right*, go to the next entity in the DXF structure
    - **Previous Entity** *Ctrl+Right*, go to the previous entity in the DXF structure
    - **Show Entity in TreeView** *Ctrl+Down*, expand the left tree view to the
      currently displayed entity in the list view - this does not happen
      automatically for performance reasons
    - **Entity History Back** *Alt+Left*
    - **Entity History Forward** *Alt+Right*
    - **Go to HEADERS Section** *Shift+H*
    - **Go to BLOCKS Section** *Shift+B*
    - **Go to ENTITIES Section** *Shift+E*
    - **Go to OBJECTS Section** *Shift+O*

- Bookmarks Menu
    - **Store Bookmark...** *Ctrl+Shift+B*, store current location as named bookmark
    - **Go to Bookmark...** *Ctrl+B*, go to stored location

Strip
-----

Strip comment tags (group code 999) from ASCII DXF files and can remove the
THUMBNAILIMAGE section. Binary DXF files are not supported.

.. code-block:: Text

    C:\> ezdxf strip -h
    usage: ezdxf strip [-h] [-b] [-v] FILE [FILE ...]

    positional arguments:
      FILE           DXF file to process, wildcards "*" and "?" are supported

    optional arguments:
      -h, --help       show this help message and exit
      -b, --backup     make a backup copy with extension ".bak" from the DXF file,
                       overwrites existing backup files
      -t, --thumbnail  strip THUMBNAILIMAGE section
      -v, --verbose    give more output

Config
------

Manage config files.

.. code-block:: Text

    C:\> ezdxf config -h
    usage: ezdxf config [-h] [-p] [--home] [--reset]

    optional arguments:
      -h, --help   show this help message and exit
      -p, --print  print configuration, to store the configuration use:
                   "ezdxf config -p > my.ini"
      --home       create config file 'ezdxf.ini' in the user home directory
                   '~/.config/ezdxf', $XDG_CONFIG_HOME is supported if set

      --reset      factory reset, delete default config files 'ezdxf.ini'

To create a new config file "my.ini" by printing the configuration into a file:

.. code-block:: Text

    C:\> ezdxf config -p > my.ini

Info
----

Show information and optional stats of DXF files as loaded by ezdxf, this may
not represent the original content of the file, use the `browse`_ command to see
the original content. The upgrade is necessary for very old DXF versions
prior to R12 and for the "special" versions R13 and R14. The `-s` option shows
some statistics about the DXF content like entity count or table count. Use the
`-v` option show more of everything.

.. code-block:: Text

    C:\> ezdxf info -h
    usage: ezdxf info [-h] [-v] [-s] FILE [FILE ...]

    positional arguments:
      FILE           DXF file to process, wildcards "*" and "?" are supported

    options:
      -h, --help     show this help message and exit
      -v, --verbose  give more output
      -s, --stats    show content stats

This is the verbose output for an old DXF R10 file and shows that the loading
process created some required structures which do not exist in DXF R10 files,
like the BLOCK_RECORD table or the OBJECTS section:

.. code-block:: Text

    C:\> ezdxf info -v -s test_R10.dxf

    Filename: "test_R10.dxf"
    Loaded content was upgraded from DXF Version AC1006 (R10)
    Release: R12
    DXF Version: AC1009
    Maintenance Version: <undefined>
    Codepage: ANSI_1252
    Encoding: cp1252
    Unit system: Imperial
    Modelspace units: Unitless
    $LASTSAVEDBY: <undefined>
    $HANDSEED: 0
    $FINGERPRINTGUID: {9EADDC7C-5982-4C68-B770-8A62378C2B90}
    $VERSIONGUID: {49336E63-D99B-45EC-803C-4D2BD03A7DE0}
    $USERI1=0
    $USERI2=0
    $USERI3=0
    $USERI4=0
    $USERI5=0
    $USERR1=0.0
    $USERR2=0.0
    $USERR3=0.0
    $USERR4=0.0
    $USERR5=0.0
    File was not created by ezdxf >= 0.16.4
    File was not written by ezdxf >= 0.16.4
    Content stats:
    LAYER table entries: 18
      0
      Defpoints
      LYR_00
      LYR_01
      LYR_02
      LYR_03
      LYR_04
      LYR_05
      LYR_06
      LYR_07
      LYR_08
      LYR_09
      LYR_10
      LYR_11
      LYR_12
      LYR_13
      LYR_14
      LYR_15
    LTYPE table entries: 13
      BORDER
      ByBlock
      ByLayer
      CENTER
      CONTINUOUS
      CUTTING
      DASHDOT
      DASHED
      DIVIDE
      DOT
      HIDDEN
      PHANTOM
      STITCH
    STYLE table entries: 1
      STANDARD
    DIMSTYLE table entries: 1
      Standard
    APPID table entries: 1
      ACAD
    UCS table entries: 0
    VIEW table entries: 0
    VPORT table entries: 1
      *Active
    BLOCK_RECORD table entries: 2
      *Model_Space
      *Paper_Space
    Entities in modelspace: 78
      ARC (2)
      CIRCLE (2)
      LINE (74)
    Entities in OBJECTS section: 20
      ACDBDICTIONARYWDFLT (1)
      ACDBPLACEHOLDER (1)
      DICTIONARY (11)
      LAYOUT (2)
      MATERIAL (3)
      MLEADERSTYLE (1)
      MLINESTYLE (1)


Show Version & Configuration
----------------------------

Show the *ezdxf* version and configuration:

.. code-block:: Text

    C:\> ezdxf -Vv

    ezdxf v0.16.5b0 @ d:\source\ezdxf.git\src\ezdxf
    Python version: 3.9.6 (tags/v3.9.6:db3ff76, Jun 28 2021, 15:26:21) [MSC v.1929 64 bit (AMD64)]
    using C-extensions: yes
    using Matplotlib: yes

    Configuration:
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


    Environment Variables:
    EZDXF_DISABLE_C_EXT=
    EZDXF_TEST_FILES=D:\Source\dxftest
    EZDXF_CONFIG_FILE=

    Existing Configuration Files:
    C:\Users\manfred\.config\ezdxf\ezdxf.ini

.. seealso::

    Documentation of the :mod:`ezdxf.options` module and the
    :ref:`environment_variables`.
