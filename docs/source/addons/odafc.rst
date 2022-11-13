.. _odafc_addon:

.. module:: ezdxf.addons.odafc

ODA File Converter Support
==========================

Use an installed `ODA File Converter`_ for converting between different versions
of `.dwg`, `.dxb` and `.dxf`.

.. warning::

    Execution of an external application is a big security issue! Especially
    when the path to the executable can be altered.

    To avoid this problem delete the ``ezdxf.addons.odafc.py`` module.

Install ODA File Converter
--------------------------

The `ODA File Converter`_ has to be installed by the user, the application is
available for Windows XP, Windows 7 or later, Mac OS X, and Linux in 32/64-bit
RPM and DEB format.

.. versionadded:: 1.0.0
    The option "unix_exec_path" was added to define an executable for Linux
    and macOS, this executable overrides the default command ``ODAFileConverter``.
    Assign an **absolute** path to the executable to that key and if the
    executable is not found the add-on falls back to the ``ODAFileConverter``
    command.

AppImage Support
----------------

The option "unix_exec_path" also adds support for AppImages provided by the
Open Design Alliance. Download the AppImage file and store it in a folder of
your choice (e.g. ``~/Apps``) and make the file executable::

    chmod a+x ~/Apps/ODAFileConverter_QT5_lnxX64_8.3dll_23.9.AppImage

Add the **absolute** path as config option "unix_exec_path" to the
"odafc-addon" section:

.. code-block:: INI

    [odafc-addon]
    win_exec_path = "C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe"
    unix_exec_path = "/home/<your user name>/Apps/ODAFileConverter_QT5_lnxX64_8.3dll_23.9.AppImage"

This overrides the default command ``ODAFileConverter`` and if the executable is
not found the add-on falls back to the ``ODAFileConverter`` command.

.. seealso::

    For more information about config files see section: :ref:`global_options`

Suppressed GUI
--------------

On Windows the GUI of the ODA File Converter is suppressed, on Linux you may
have to install the ``xvfb`` package to prevent this, for macOS is no solution
known.

Supported DXF and DWG Versions
------------------------------

ODA File Converter version strings, you can use any of this strings to specify
a version, ``'R..'`` and ``'AC....'`` strings will be automatically mapped to
``'ACAD....'`` strings:

=========== =============== ===========
ODAFC       ezdxf           Version
=========== =============== ===========
ACAD9       not supported   AC1004
ACAD10      not supported   AC1006
ACAD12      R12             AC1009
ACAD13      R13             AC1012
ACAD14      R14             AC1014
ACAD2000    R2000           AC1015
ACAD2004    R2004           AC1018
ACAD2007    R2007           AC1021
ACAD2010    R2010           AC1024
ACAD2013    R2013           AC1027
ACAD2018    R2018           AC1032
=========== =============== ===========

Config
------

On Windows the path to the ``ODAFileConverter.exe`` executable is
stored in the config file (see :mod:`ezdxf.options`) in the "odafc-addon"
section as key "win_exec_path", the default entry is:

.. code-block:: INI

    [odafc-addon]
    win_exec_path = "C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe"
    unix_exec_path =

On Linux and macOS the ``ODAFileConverter`` command is located by the
:func:`shutil.which` function but can be overridden since version 1.0 by the key
"linux_exec_path".


Usage
-----

.. code-block:: Python

    from ezdxf.addons import odafc

    # Load a DWG file
    doc = odafc.readfile('my.dwg')

    # Use loaded document like any other ezdxf document
    print(f'Document loaded as DXF version: {doc.dxfversion}.')
    msp = doc.modelspace()
    ...

    # Export document as DWG file for AutoCAD R2018
    odafc.export_dwg(doc, 'my_R2018.dwg', version='R2018')


.. attribute:: win_exec_path

    Path to installed `ODA File Converter` executable on Windows systems,
    default is ``"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe"``.

.. attribute:: unix_exec_path

    Absolute path to a Linux or macOS executable if set, otherwise an empty
    string and the default command ``ODAFileConverter`` is used.

.. autofunction:: is_installed

.. autofunction:: readfile

.. autofunction:: export_dwg

.. autofunction:: convert

.. _ODA File Converter: https://www.opendesign.com/guestfiles/oda_file_converter