Drawing Object
==============

.. module:: ezdxf.drawing

.. class:: Drawing

    The :class:`Drawing` class manages all entities and tables related to a DXF drawing. Every drawing has its own
    character :attr:`encoding` which is only important for saving to disk.

    .. attribute:: dxfversion

        contains the DXF version as string like ``'AC1009'``, set by the
        :func:`~ezdxf.new` or the :func:`~ezdxf.readfile` function.

    .. attribute:: acad_release

        The AutoCAD release number string like ``'R12'`` or ``'R2000'`` for actual DXF version of this drawing.

    .. attribute:: encoding

        DXF drawing text encoding, the default encoding for new drawings is
        ``'cp1252'``. Starting with DXF version R2007 (AC1021) DXF files are written
        as UTF-8 encoded text files, regardless of the attribute :attr:`encoding` (read/write)
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

    .. attribute:: filename

        Contains the drawing filename, if the drawing was opened with the
        :func:`readfile` function else set to `None`. (read/write)

    .. attribute:: dxffactory

        DXF entity creation factory, see also :class:`DXFFactory` (read only).

    .. attribute:: header

        Reference to the :class:`HeaderSection` of the drawing, where
        you can change the drawing settings.

    .. attribute:: entities

        Reference to the :class:`EntitySection` of the drawing, where all graphical entities are stored, but only from
        model space and the *active* layout (paper space). Just for your information: Entities of other layouts are stored
        as blocks in the :class:`BlocksSection`.

    .. attribute:: objects

        Reference to the objects section, see also :class:`ObjectsSection`.

    .. attribute:: blocks

        Reference to the blocks section, see also :class:`BlocksSection`.

    .. attribute:: tables

        Reference to the tables section, see also :class:`TablesSection`.

    .. attribute:: classes

        Reference to the classes section, see also :class:`ClassesSection`.

    .. attribute:: layouts

        Reference to the layout management object, see also :class:`Layouts`.

    .. attribute:: groups

        requires DXF version R13 or later

        Table (dict) of all groups used in this drawing, see also :class:`DXFGroupTable`.

    .. attribute:: layers

        Shortcut for :attr:`Drawing.tables.layers`

        Reference to the layers table, where you can create, get and
        remove layers, see also :class:`Table` and :class:`Layer`

    .. attribute:: styles

        Shortcut for :attr:`Drawing.tables.styles`

        Reference to the styles table, see also :class:`Style`.

    .. attribute:: dimstyles

        Shortcut for :attr:`Drawing.tables.dimstyles`

        Reference to the dimstyles table, see also :class:`DimStyle`.

    .. attribute:: linetypes

        Shortcut for :attr:`Drawing.tables.linetypes`

        Reference to the linetypes table, see also :class:`Linetype`.

    .. attribute:: views

        Shortcut for :attr:`Drawing.tables.views`

        Reference to the views table, see also :class:`View`.

    .. attribute:: viewports

        Shortcut for :attr:`Drawing.tables.viewports`

        Reference to the viewports table, see also :class:`Viewport`.

    .. attribute:: ucs

        Shortcut for :attr:`Drawing.tables.ucs`

        Reference to the ucs table, see also :class:`UCS`.

    .. attribute:: appids

        Shortcut for :attr:`Drawing.tables.appids`

        Reference to the appids table, see also :class:`AppID`.

    .. automethod:: save

    .. automethod:: saveas

    .. automethod:: write

    .. automethod:: query

    .. automethod:: groupby

    .. automethod:: modelspace

    .. automethod:: layout

    .. automethod:: active_layout

    .. automethod:: layout_names

    .. automethod:: layout_names_in_taborder

    .. automethod:: new_layout

    .. automethod:: delete_layout

    .. automethod:: add_image_def

    .. automethod:: set_raster_variables

    .. automethod:: add_underlay_def

    .. automethod:: add_xref_def

    .. automethod:: cleanup

    .. automethod:: layouts_and_blocks

    .. automethod:: chain_layouts_and_blocks

    .. automethod:: reset_fingerprint_guid

    .. automethod:: reset_version_guid