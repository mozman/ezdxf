.. _dwgmanagement:

Drawing Management
==================

.. module:: ezdxf

Create New Drawings
-------------------

.. autofunction:: new(dxfversion='AC1027', setup=None) -> Drawing

Open Drawings
-------------

Open DXF drawings from file system or text stream, byte stream usage is not supported.

DXF files prior to R2007 requires file encoding defined by header variable $DWGCODEPAGE, DXF R2007 and later
requires an UTF-8 encoding.

`ezdxf` supports reading of files for following DXF versions:

=========== ========== ============== ===================================
Version     Release    Encoding       Remarks
=========== ========== ============== ===================================
< AC1009               $DWGCODEPAGE   pre AutoCAD R12 upgraded to AC1009
AC1009      R12        $DWGCODEPAGE   AutoCAD R12
AC1012      R13        $DWGCODEPAGE   AutoCAD R13 upgraded to AC1015
AC1014      R14        $DWGCODEPAGE   AutoCAD R14 upgraded to AC1015
AC1015      R2000      $DWGCODEPAGE   AutoCAD R2000
AC1018      R2004      $DWGCODEPAGE   AutoCAD R2004
AC1021      R2007      UTF-8          AutoCAD R2007
AC1024      R2010      UTF-8          AutoCAD R2010
AC1027      R2013      UTF-8          AutoCAD R2013
AC1032      R2018      UTF-8          AutoCAD R2018
=========== ========== ============== ===================================

.. autofunction:: readfile(filename: str, encoding: str = None, legacy_mode: bool = False, filter_stack=None) -> Drawing

.. autofunction:: read(stream: TextIO, legacy_mode: bool = False, filter_stack=None) -> Drawing

.. autofunction:: readzip(zipfile: str, filename: str = None) -> Drawing

.. autofunction:: decode_base64(data: bytes) -> Drawing


Save Drawings
-------------

Save the drawing to the file system by :class:`~ezdxf.document.Drawing` methods :meth:`~ezdxf.document.Drawing.save`
or :meth:`~ezdxf.document.Drawing.saveas`.
Write the :class:`~ezdxf.document.Drawing` to a text stream with :meth:`~ezdxf.document.Drawing.write`, the
text stream requires at least a :meth:`write` method.

.. versionadded:: 0.11

    Get required output encoding for text streams by :class:`~ezdxf.document.Drawing` property
    :attr:`~ezdxf.document.Drawing.output_encoding`

.. _globaloptions:

Drawing Settings
----------------

The :class:`~ezdxf.sections.header.HeaderSection` stores meta data like modelspace extensions, user name or saving time
and current application settings, like actual layer, text style or dimension style settings. These settings are not
necessary to process DXF data and therefore many of this settings are not maintained by `ezdxf` automatically.

Header variables set at new
~~~~~~~~~~~~~~~~~~~~~~~~~~~

================ =================================
$ACADVER         DXF version
$TDCREATE        date/time at creating the drawing
$FINGERPRINTGUID every drawing gets a GUID
================ =================================

Header variables updated at saving
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

================ =================================
$TDUPDATE        actual date/time at saving
$HANDSEED        next available handle as hex string
$DWGCODEPAGE     encoding setting
$VERSIONGUID     every saved version gets a new GUID
================ =================================

.. seealso::

    - Howto: :ref:`set/get header variables`
    - Howto: :ref:`set drawing units`
