Tables Section
==============

.. module:: ezdxf.sections.tables

The TABLES section is the home of all TABLE objects of a DXF document.

.. seealso::

    DXF Internals: :ref:`tables_section_internals`

.. class:: TablesSection

    .. attribute:: layers

        :class:`~ezdxf.sections.table.LayerTable` maintaining the
        :class:`~ezdxf.entities.Layer` objects

    .. attribute:: linetypes

        :class:`~ezdxf.sections.table.LinetypeTable` maintaining the
        :class:`~ezdxf.entities.Linetype` objects

    .. attribute:: styles

        :class:`~ezdxf.sections.table.TextstyleTable` maintaining the
        :class:`~ezdxf.entities.Textstyle` objects

    .. attribute:: dimstyles

        :class:`~ezdxf.sections.table.DimStyleTable` maintaining the
        :class:`~ezdxf.entities.DimStyle` objects

    .. attribute:: appids

        :class:`~ezdxf.sections.table.AppIDTable` maintaining the
        :class:`~ezdxf.entities.AppID` objects

    .. attribute:: ucs

        :class:`~ezdxf.sections.table.UCSTable` maintaining the
        :class:`~ezdxf.entities.UCSTable` objects

    .. attribute:: views

        :class:`~ezdxf.sections.table.ViewTable` maintaining the
        :class:`~ezdxf.entities.View` objects

    .. attribute:: viewports

        :class:`~ezdxf.sections.table.ViewportTable` maintaining the
        :class:`~ezdxf.entities.VPort` objects

    .. attribute:: block_records

        :class:`~ezdxf.sections.table.BlockRecordTable` maintaining the
        :class:`~ezdxf.entities.BlockRecord` objects


