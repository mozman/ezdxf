.. _odafc_addon:

.. module:: ezdxf.addons.odafc

ODA File Converter Support
==========================

Use an installed `ODA File Converter`_ for converting between different versions of `.dwg`, `.dxb` and `.dxf`.

.. warning::

    Execution of an external application is a big security issue! Especially
    when the path to the executable can be altered.

    To avoid this problem delete the ``ezdxf.addons.odafc.py`` module.

The `ODA File Converter`_ has to be installed by the user, the application is available for Windows XP,
Windows 7 or later, Mac OS X, and Linux in 32/64-bit RPM and DEB format.

At least at Windows the GUI of the ODA File Converter pops up on every call.

ODA File Converter version strings, you can use any of this strings to specify a version, ``'R..'`` and
``'AC....'`` strings will be automatically mapped to ``'ACAD....'`` strings:

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

On Windows systems the path of the ``ODAFileConverter.exe`` application is
stored in the config file (see :mod:`ezdxf.options`) in the "odafc-addon"
section as key "win_exec_path", the default entry is:

.. code-block:: INI

    [odafc-addon]
    win_exec_path = "C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe"

On Linux and macOS the ``ODAFileConverter`` command is located by the
:func:`shutil.which` function.


Usage:

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

    Path to installed `ODA File Converter` executable, default is
    ``"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe"``.

.. autofunction:: readfile(filename: str, version: str = None, audit=False) -> Drawing

.. autofunction:: export_dwg(doc: Drawing, filename: str, version: str = None, audit=False, replace=False) -> None

.. _ODA File Converter: https://www.opendesign.com/guestfiles/oda_file_converter