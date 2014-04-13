.. _dwgmanagement:

Drawing Management
==================

Create New Drawings
-------------------

.. function:: new(dxfversion='AC1009')

    Create a new drawing from a template-drawing. The template-drawings are
    located in a `templatedir`, which resides by default in the `ezdxf`
    package-directory. The location of the `templatedir` can be changed in
    the package options.

.. include:: dxfversion.inc

Open Drawings
-------------

You can open DXF drawings from disk or from a text-stream. (byte-stream usage
is not implemented yet).

.. function:: readfile(filename)

    This is the preferred method to open existing DXF files. Read the DXF
    drawing from the file-system with auto-detection of encoding. Decoding
    errors will be ignored.

.. function:: read(stream)

    Read DXF drawing from a text-stream, returns a :class:`Drawing` object.
    Open mode has to be ``'rt'`` and the correct encoding has to be set at the
    open function (in Python 2.7 use :func:`io.open`), at least the stream requires
    a :meth:`readline` method.

.. function:: readfile_as_utf8(filename, errors='strict')

    This Read DXF drawing from file *filename*, expects an *utf-8* encoding.

.. function:: readfile_as_asc(filename)

    Read DXF drawing from file *filename*, expects an ASCII code-page encoding.
    Raises :class:`UnicodeDecodeError` for invalid character encodings.

Save Drawings
-------------

Save the drawing to the file-system by :meth:`Drawing.save` or :meth:`Drawing.saveas`.
Write the drawing to a text-stream with :meth:`Drawing.write`, the text-stream requires
at least a :meth:`write` method.