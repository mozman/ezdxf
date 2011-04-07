Drawing Management
==================

Create Drawings
---------------

.. function:: new(dxfversion='AC1009')

    Create a new drawing from a template-drawing. The template-drawings are
    located in a `templatedir`, which resides by default in the `ezdxf`
    package-directory. The loction of the `templatedir` can be changed in
    the package options.

=========== ========================
DXF         AutoCAD Version
=========== ========================
AC1009      AutoCAD V12
AC1015      AutoCAD V2000
AC1018      AutoCAD V2004
AC1021      AutoCAD V2007
AC1024      AutoCAD V2010
=========== ========================

Read Drawings
-------------

You can open DXF drawings from disk or from a text-stream. (byte-stream usage
is not implemented yet).

.. function:: read(stream)

    Read DXF drawing from a text-stream, returns a :class:`Drawing` object.
    Open mode has to be ``'rt'`` and the correct encoding also has to be set
    at opening stream.

.. function:: readbytes(stream)

    Read the DXF drawing from a byte-stream with auto-detection of encoding
    but **not implemented yet**.

.. function:: readfile(filename)

    Read the DXf drawing from the file-system with auto-detection of encoding.

Write Drawings
--------------

Save the drawing to the file-system by :meth:`Drawing.save` or :meth:`Drawing.saveas`.
Write the drawing to a text-stream with :meth:`Drawing.write` or to a
byte-stream with :meth:`Drawing.writebytes`.