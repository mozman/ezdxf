Drawing Object
==============

.. class:: Drawing

    The :class:`Drawing` class manages all entities and tables related to a
    DXF drawing. Every drawing has its own character :attr:`~Drawing.encoding`
    which is only important for saving to disk.

Drawing Attributes
------------------

.. attribute:: Drawing.dxfversion

    contains the DXF version as string like ``'AC1009'``, set by the
    :func:`new` or the :func:`readfile` function. (read only)

.. attribute:: Drawing.acad_version

    contains the AutoCAD release number string like ``'R12'`` or ``'R2000'`` that introduced the DXF version
    of this drawing. (read only)

.. attribute:: Drawing.encoding

    DXF drawing text encoding, the default encoding for new drawings is
    ``'cp1252'``. Starting with DXF version R2007 (AC1021) DXF files are written
    as UTF-8 encoded text files, regardless of the attribute :attr:`Drawing.encoding` (read/write)
    see also: :ref:`dxf file encoding`

    ============ =================
    supported    encodings
    ============ =================
    ``'cp874'``  Thai
    ``'cp932'``  Japanese
    ``'gbk'``    UnifiedChinese
    ``'cp949'``  Korean
    ``'cp950'``  TradChinese
    ``'cp1250'`` CentralEurope
    ``'cp1251'`` Cyrillic
    ``'cp1252'`` WesternEurope
    ``'cp1253'`` Greek
    ``'cp1254'`` Turkish
    ``'cp1255'`` Hebrew
    ``'cp1256'`` Arabic
    ``'cp1257'`` Baltic
    ``'cp1258'`` Vietnam
    ============ =================

.. attribute:: Drawing.filename

    Contains the drawing filename, if the drawing was opened with the
    :func:`readfile` function else set to `None`. (read/write)

.. attribute:: Drawing.dxffactory

    DXF entity creation factory, see also :class:`DXFFactory` (read only).

.. attribute:: Drawing.sections

    Collection of all existing sections of a DXF drawing.

.. attribute:: Drawing.header

    Shortcut for :attr:`Drawing.sections.header`

    Reference to the :class:`HeaderSection` of the drawing, where
    you can change the drawing settings.

.. attribute:: Drawing.entities

    Shortcut for :attr:`Drawing.sections.entities`

    Reference to the :class:`EntitySection` of the drawing, where all
    graphical entities are stored, independently from modelspace or layout.

.. attribute:: Drawing.blocks

    Shortcut for :attr:`Drawing.sections.blocks`

    Reference to the blocks section, see also :class:`BlocksSection`.

.. attribute:: Drawing.groups

    requires DXF version R13 or later

    Table (dict) of all groups used in this drawing, see also :class:`DXFGroupTable`.

.. attribute:: Drawing.layers

    Shortcut for :attr:`Drawing.sections.tables.layers`

    Reference to the layers table, where you can create, get and
    remove layers, see also :class:`Table` and :class:`Layer`

.. attribute:: Drawing.styles

    Shortcut for :attr:`Drawing.sections.tables.styles`

    Reference to the styles table, see also :class:`Style`.

.. attribute:: Drawing.dimstyles

    Shortcut for :attr:`Drawing.sections.tables.dimstyles`

    Reference to the dimstyles table, see also :class:`DimStyle`.

.. attribute:: Drawing.linetypes

    Shortcut for :attr:`Drawing.sections.tables.linetypes`

    Reference to the linetypes table, see also :class:`Linetype`.

.. attribute:: Drawing.views

    Shortcut for :attr:`Drawing.sections.tables.views`

    Reference to the views table, see also :class:`View`.

.. attribute:: Drawing.viewports

    Shortcut for :attr:`Drawing.sections.tables.viewports`

    Reference to the viewports table, see also :class:`Viewport`.

.. attribute:: Drawing.ucs

    Shortcut for :attr:`Drawing.sections.tables.ucs`

    Reference to the ucs table, see also :class:`UCS`.

.. attribute:: Drawing.appids

    Shortcut for :attr:`Drawing.sections.tables.appids`

    Reference to the appids table, see also :class:`AppID`.

.. attribute:: Drawing.is_binary_data_compressed

   Indicates if binary data is compressed in memory. see: :meth:`Drawing.compress_binary_data`

Drawing Methods
---------------

.. method:: Drawing.modelspace()

    Get the model space layout, see also :class:`Layout`.

.. method:: Drawing.layout(name)

    Get a paper space layout by `name`, see also :class:`Layout`.
    (DXF version AC1009, supports only one paper space layout, so `name` is
    ignored)

.. method:: Drawing.layout_names()

    Get a list of available paper space layouts.

.. method:: Drawing.new_layout(name, dxfattribs=None)

    Create a new paper space layout *name*. Returns a :class:`Layout` object.
    Available only for DXF version AC1015 or newer, AC1009 supports only one paper space.

.. method:: Drawing.delete_layout(name)

    Delete paper space layout *name* and all its entities. Available only for DXF version AC1015
    or newer, AC1009 supports only one paper space and you can't delete it.

.. method:: Drawing.add_image_def(filename, size_in_pixel, name=None)

    Add an :class:`ImageDef` entity to the drawing (objects section). `filename` is the image file name as relative or
    absolute path and `size_in_pixel` is the image size in pixel as (x, y) tuple. To avoid dependencies to external
    packages, ezdxf can not determine the image size by itself. Returns a :class:`ImageDef` entity which is needed to
    create an image reference, see :ref:`tut_image`. `name` is the internal image name, if set to None, name is
    auto-generated.

    :param filename: image file name
    :param size_in_pixel: image size in pixel as (x, y) tuple
    :param name: image name for internal use, None for an auto-generated name

.. method:: Drawing.add_underlay_def(filename, format='pdf', name=None)

    Add an :class:`UnderlayDef` entity to the drawing (objects section). `filename` is the underlay file name as
    relative or absolute path and format as string (pdf, dwf, dgn). Returns a :class:`UnderlayDef` entity which is
    needed to create an underlay reference, see :ref:`tut_underlay`. `name` is the internal underlay name, if set to
    None, name is auto-generated.

    :param filename: underlay file name
    :param format: file format (pdf, dwf or dgn) or ext=get format from filename extension
    :param name: underlay name for internal use, None for an auto-generated name

.. method:: Drawing.save(encoding='auto')

    Write drawing to file-system by using the :attr:`~Drawing.filename` attribute
    as filename. Overwrite file encoding by argument *encoding*, handle with care, but this option allows you to create
    DXF files for applications that handles file encoding different than AutoCAD.

    :param encoding: override file encoding

.. method:: Drawing.saveas(filename, encoding='auto')

    Write drawing to file-system by setting the :attr:`~Drawing.filename`
    attribute to `filename`. For argument *encoding* see: :meth:`~Drawing.save`.

    :param filename: file name
    :param encoding: override file encoding

.. method:: Drawing.write(stream)

    Write drawing to a text stream. For DXF version R2004 (AC1018) and prior opened stream with
    `encoding=` :attr:`Drawing.encoding` and `mode='wt'`. For DXF version R2007 (AC1021) and later use
    `encoding='utf-8'`.

.. method:: Drawing.cleanup(groups=True)

    Cleanup drawing. Call it before saving the drawing but only if necessary, the process could take a while.

    :param groups: removes deleted and invalid entities from groups

.. method:: Drawing.compress_binary_data()

    If you don't need access to binary data of DXF entities, you can compress them in memory for a lower
    memory footprint, you can set :code:`ezdxf.options.compress_binray_data = True` to compress binary data
    for every drawing you open, but data compression cost time, so this option isn't active by default.

.. _low_level_access_to_dxf_entities:

Low Level Access to DXF entities
--------------------------------

.. method:: Drawing.get_dxf_entity(handle)

    Get entity by *handle* from entity database. Low level access to DXF entities database.
    Raises *KeyError* if *handle* doesn't exist. Returns :class:`DXFEntity` or inherited.

If you just need the raw DXF tags use::

    tags = Drawing.entitydb[handle]  # raises KeyError, if handle does not exist
    tags = Drawing.entitydb.get(handle)  # returns a default value, if handle does not exist (None by default)

type of tags: :class:`ClassifiedTags`

