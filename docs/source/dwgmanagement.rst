.. _dwgmanagement:

Drawing Management
==================

Create New Drawings
-------------------

.. function:: new(dxfversion='AC1009')

    Create a new drawing from a template-drawing. The template-drawings are
    located in a template directory, which resides by default in the *ezdxf*
    package subfolder `templates`. The location of the template directory can be changed by
    the global option :attr:`ezdxf.options.template_dir`.

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

.. _globaloptions:

Global Options
--------------

    Global options stored in :mod:`ezdxf.options`

.. attribute:: ezdxf.options.compress_binary_data

    If you don't need access to binary data of DXF entities, you can compress them in memory for a lower
    memory footprint, set the global :code:`ezdxf.options.compress_binary_data = True` to compress binray data
    for every drawing you open, but data compression cost time, so this option isn't active by default.
    You can individually compress the binary data of a drawing with the method :meth:`Drawing.compress_binary_data`.

.. attribute:: ezdxf.options.compress_default_chunks

    There are at least two sections in DXF drawings which are very useless: `THUMBNAILIMAGE` and since AutoCAD 2013
    (AC1027) `ACDSDATA`. They were managed by the simple :class:`DefaultChunk` class, which is just a bunch of dumb
    tags, to save some memory you can compress these default chunks by setting the option
    :code:`ezdxf.options.compress_default_chunks = True`.

.. attribute:: ezdxf.options.templatedir

    Directory where the :meth:`new` function looks for its template file (AC1009.dxf, AC1015.dxf, ...) , default is
    *None*, which means the package subfolder `templates`. But if you want to use your own templates set this option
    :code:`ezdxf.options.template_dir = "my_template_directory"`. But you don't really need this, just open your
    template file with :meth:`readfile` and save the drawing as new file with the :meth:`Drawing.saveas` method.

    This option is very useful if the *ezdxf* package resides in a zip archive.

.. attribute:: ezdxf.options.debug

    Activate debug mode.