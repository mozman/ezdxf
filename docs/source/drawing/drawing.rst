Drawing Class
=============

.. module:: ezdxf.document

The :class:`Drawing` class is the central management structure of a DXF document.

Access Layouts
--------------

- :meth:`Drawing.modelspace`
- :meth:`Drawing.paperspace`

Access Resources
----------------

- Application ID Table: :attr:`Drawing.appids`
- Block Definition Table: :attr:`Drawing.blocks`
- Dimension Style Table: :attr:`Drawing.dimstyles`
- Layer Table: :attr:`Drawing.layers`
- Linetype Table: :attr:`Drawing.linetypes`
- MLeader Style Table: :attr:`Drawing.mleader_styles`
- MLine Style Table: :attr:`Drawing.mline_styles`
- Material Table: :attr:`Drawing.materials`
- Text Style Table: :attr:`Drawing.styles`
- UCS Table: :attr:`Drawing.ucs`
- VPort Table: :attr:`Drawing.viewports`
- View Table: :attr:`Drawing.views`

- Classes Section: :attr:`Drawing.classes`
- Object Section: :attr:`Drawing.objects`

- Entity Database: :attr:`Drawing.entitydb`
- Entity Groups: :attr:`Drawing.groups`
- Header Variables: :attr:`Drawing.header`


Drawing Class
-------------

.. class:: Drawing

    The :class:`Drawing` class is the central management structure of a DXF document.

    .. attribute:: dxfversion

        Actual DXF version like ``'AC1009'``, set by :func:`ezdxf.new` or
        :func:`ezdxf.readfile`.

        For supported DXF versions see :ref:`dwgmanagement`

    .. attribute:: acad_release

        The AutoCAD release name like ``'R12'`` or ``'R2000'`` for actual
        :attr:`dxfversion`.

    .. attribute:: encoding

        Text encoding of :class:`Drawing`, the default encoding for new drawings
        is ``'cp1252'``. Starting with DXF R2007 (AC1021), DXF files are written
        as UTF-8 encoded text files, regardless of the attribute
        :attr:`encoding`.
        The text encoding can be changed to encodings listed below.

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

    .. attribute:: output_encoding

        Returns required output encoding for saving to filesystem or encoding
        to binary data.

    .. attribute:: filename

        :class:`Drawing` filename, if loaded by :func:`ezdxf.readfile` else ``None``.

    .. attribute:: rootdict

        Reference to the root dictionary of the OBJECTS section.


    .. attribute:: header

        Reference to the :class:`~ezdxf.sections.header.HeaderSection`, get/set
        drawing settings as header variables.

    .. attribute:: entities

        Reference to the :class:`EntitySection` of the drawing, where all
        graphical entities are stored, but only from modelspace and the
        *active* paperspace layout. Just for your information: Entities of other
        paperspace layouts are stored as :class:`~ezdxf.layouts.BlockLayout`
        in the :class:`~ezdxf.sections.blocks.BlocksSection`.

    .. attribute:: objects

        Reference to the objects section, see also :class:`~ezdxf.sections.objects.ObjectsSection`.

    .. attribute:: blocks

        Reference to the blocks section, see also :class:`~ezdxf.sections.blocks.BlocksSection`.

    .. attribute:: tables

        Reference to the tables section, see also :class:`~ezdxf.sections.tables.TablesSection`.

    .. attribute:: classes

        Reference to the classes section, see also :class:`~ezdxf.sections.classes.ClassesSection`.

    .. attribute:: layouts

        Reference to the layout manager, see also :class:`~ezdxf.layouts.Layouts`.

    .. attribute:: groups

        Collection of all groups, see also :class:`~ezdxf.entities.dxfgroups.GroupCollection`.

        requires DXF R13 or later

    .. attribute:: layers

        Shortcut for :attr:`Drawing.tables.layers`

        Reference to the layers table, where you can create, get and
        remove layers, see also :class:`~ezdxf.sections.table.Table` and
        :class:`~ezdxf.entities.Layer`

    .. attribute:: styles

        Shortcut for :attr:`Drawing.tables.styles`

        Reference to the styles table, see also :class:`~ezdxf.entities.Textstyle`.

    .. attribute:: dimstyles

        Shortcut for :attr:`Drawing.tables.dimstyles`

        Reference to the dimstyles table, see also :class:`~ezdxf.entities.DimStyle`.

    .. attribute:: linetypes

        Shortcut for :attr:`Drawing.tables.linetypes`

        Reference to the linetypes table, see also :class:`~ezdxf.entities.Linetype`.

    .. attribute:: views

        Shortcut for :attr:`Drawing.tables.views`

        Reference to the views table, see also :class:`~ezdxf.entities.View`.

    .. attribute:: viewports

        Shortcut for :attr:`Drawing.tables.viewports`

        Reference to the viewports table, see also :class:`~ezdxf.entities.VPort`.

    .. attribute:: ucs

        Shortcut for :attr:`Drawing.tables.ucs`

        Reference to the ucs table, see also :class:`~ezdxf.entities.UCSTableEntry`.

    .. attribute:: appids

        Shortcut for :attr:`Drawing.tables.appids`

        Reference to the appids table, see also :class:`~ezdxf.entities.AppID`.

    .. attribute:: materials

        :class:`~ezdxf.entities.MaterialCollection` of all
        :class:`~ezdxf.entities.Material` objects.

    .. attribute:: mline_styles

        :class:`~ezdxf.entities.MLineStyleCollection` of all
        :class:`~ezdxf.entities.MLineStyle` objects.

    .. attribute:: mleader_styles

        :class:`~ezdxf.entities.MLeaderStyleCollection` of all
        :class:`~ezdxf.entities.MLeaderStyle` objects.

    .. autoattribute:: units

    .. automethod:: save

    .. automethod:: saveas

    .. automethod:: write

    .. automethod:: encode_base64

    .. automethod:: encode

    .. automethod:: query

    .. automethod:: groupby

    .. automethod:: modelspace

    .. automethod:: paperspace

    .. automethod:: layout

    .. automethod:: active_layout

    .. automethod:: layout_names

    .. automethod:: layout_names_in_taborder

    .. automethod:: new_layout

    .. automethod:: page_setup

    .. automethod:: delete_layout

    .. automethod:: add_image_def

    .. automethod:: set_raster_variables

    .. automethod:: set_wipeout_variables

    .. automethod:: add_underlay_def

    .. automethod:: add_xref_def

    .. automethod:: layouts_and_blocks

    .. automethod:: chain_layouts_and_blocks

    .. automethod:: reset_fingerprint_guid

    .. automethod:: reset_version_guid

    .. automethod:: set_modelspace_vport

    .. automethod:: audit

    .. automethod:: validate

    .. automethod:: ezdxf_metadata
