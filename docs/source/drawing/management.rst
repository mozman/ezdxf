.. _dwgmanagement:

Document Management
===================

.. module:: ezdxf

Create New Drawings
-------------------

.. autofunction:: new(dxfversion='AC1027', setup=False, units=6) -> Drawing

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

.. autofunction:: readfile(filename: str, encoding: str = None, errors: str="surrogateescape") -> Drawing

.. autofunction:: read(stream: TextIO) -> Drawing

.. autofunction:: readzip(zipfile: str, filename: str = None, errors: str="surrogateescape") -> Drawing

.. autofunction:: decode_base64(data: bytes, errors: str="surrogateescape") -> Drawing

.. hint::

    This works well with DXF files from trusted sources like AutoCAD or BricsCAD,
    for loading DXF files with minor or major flaws look at the
    :mod:`ezdxf.recover` module.

Save Drawings
-------------

Save the DXF document to the file system by :class:`~ezdxf.document.Drawing` methods
:meth:`~ezdxf.document.Drawing.save` or :meth:`~ezdxf.document.Drawing.saveas`.
Write the DXF document to a text stream with :meth:`~ezdxf.document.Drawing.write`,
the text stream requires at least a :meth:`write` method. Get required output
encoding for text streams by property :attr:`Drawing.output_encoding`

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

.. _ezdxf_metadata:

Ezdxf Metadata
~~~~~~~~~~~~~~

Store internal metadata like *ezdxf* version and creation time for
a new created document as metadata in the DXF file. The :class:`MetaData`
object can also store custom metadata.

The :class:`MetaData` object has a dict-like interface::

    metadata = doc.ezdxf_metadata()

    # set data
    metadata["MY_CUSTOM_META_DATA"] = "a string with max. length of 254"

    # get data, raises a KeyError() if key not exist
    value = metadata["MY_CUSTOM_META_DATA"]

    # get data, returns an empty string if key not exist
    value = metadata.get("MY_CUSTOM_META_DATA")

    # delete entry, raises a KeyError() if key not exist
    del metadata["MY_CUSTOM_META_DATA"]

    # discard entry, does not raise a KeyError() if key not exist
    metadata.discard("MY_CUSTOM_META_DATA")

Keys and values are limited to strings with a max. length of 254 characters
and line ending ``\n`` will be replaced by ``\P``.

Keys used by *ezdxf*:

    - ``WRITTEN_BY_EZDXF``: *ezdxf* version and UTC time in ISO format
    - ``CREATED_BY_EZDXF``: *ezdxf* version and UTC time in ISO format

Example of the ezdxf marker string: ``0.16.4b1 @ 2021-06-12T07:35:34.898808+00:00``

.. class:: ezdxf.document.MetaData

    .. automethod:: __contains__

    .. automethod:: __getitem__

    .. automethod:: get

    .. automethod:: __setitem__

    .. automethod:: __delitem__

    .. automethod:: discard

