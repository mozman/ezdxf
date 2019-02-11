.. _dwgmanagement:

Drawing Management
==================

Create New Drawings
-------------------

.. function:: ezdxf.new(dxfversion='AC1009')

    Create a new drawing from a template-drawing. The template-drawings are
    located in a template directory, which resides by default in the *ezdxf*
    package subfolder `templates`. The location of the template directory can be changed by
    the global option :attr:`ezdxf.options.template_dir`. *dxfversion* can be either ``'AC1009'``
    the official DXF version name or ``'R12'`` the AutoCAD release name (release name works since ezdxf 0.7.4).
    You can only create new drawings for the following DXF versions:

    ======= ========================
    Version AutoCAD Release
    ======= ========================
    AC1009  AutoCAD R12
    AC1015  AutoCAD R2000
    AC1018  AutoCAD R2004
    AC1021  AutoCAD R2007
    AC1024  AutoCAD R2010
    AC1027  AutoCAD R2013
    AC1032  AutoCAD R2018
    ======= ========================


Open Drawings
-------------

    You can open DXF drawings from disk or from a text-stream. (byte-stream usage
    is not implemented yet).

.. function:: ezdxf.readfile(filename, encoding='auto', legacy_mode=False)

    This is the preferred method to open existing DXF files. Read the DXF
    drawing from the file-system with auto-detection of encoding. Decoding
    errors will be ignored. Override encoding detection by setting parameter
    *encoding* to the estimated encoding. (use Python encoding names like in
    the :func:`open` function).

    If parameter `legacy_mode` is `True`, ezdxf tries to reorder the coordinates of the LINE entity in DXF files from
    CAD applications which wrote the coordinates in the order: x1, x2, y1, y2. Additional fixes may be added later. The
    legacy mode has a speed penalty of around 5%.

    .. hint::

        Try option `legacy_mode=True` if error "Missing required y coordinate near line: ..." occurs.

.. function:: ezdxf.read(stream, legacy_mode=False)

    Read DXF drawing from a text-stream, returns a :class:`Drawing` object.
    Open the stream in text mode (`mode='rt'`) and the correct encoding has to be set at the
    open function (in Python 2.7 use :func:`io.open`), the stream requires at least a :meth:`readline` method.
    Since DXF version R2007 (AC1021) file encoding is always 'utf-8'.

    If parameter `legacy_mode` is `True`, ezdxf tries to reorder the coordinates of the LINE entity in DXF files from
    CAD applications which wrote the coordinates in the order: x1, x2, y1, y2, see also :meth:`readfile` method.

Save Drawings
-------------

    Save the drawing to the file-system by :meth:`Drawing.save` or :meth:`Drawing.saveas`.
    Write the drawing to a text-stream with :meth:`Drawing.write`, the text-stream requires
    at least a :meth:`write` method.

.. _globaloptions:

Global Options
--------------

    Global options stored in :mod:`ezdxf.options`

.. attribute:: ezdxf.options.default_text_style

    Default text styles (``OpenSans``).

.. attribute:: ezdxf.options.default_dimension_text_style

    Default text style for Dimensions (``OpenSansCondensed-Light``).


.. attribute:: ezdxf.options.templatedir

    Directory where the :meth:`new` function looks for its template file (AC1009.dxf, AC1015.dxf, ...) , default is
    *None*, which means the package subfolder `templates`. But if you want to use your own templates set this option
    :code:`ezdxf.options.template_dir = "my_template_directory"`. But you don't really need this, just open your
    template file with :meth:`ezdxf.readfile` and save the drawing as new file with the :meth:`Drawing.saveas` method.

    This option is very useful if the *ezdxf* package resides in a zip archive.

.. attribute:: ezdxf.options.check_entity_tag_structures

    Check app data (:ref:`app_data_tags`) and xdata (:ref:`xdata_tags`) tag structures, set this option to `False` for
    a little performance boost, default is `True`.

