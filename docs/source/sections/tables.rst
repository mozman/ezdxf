Tables Section
==============

.. module:: ezdxf.sections.tables

The TABLES section is the home of all TABLE objects of a DXF document.

.. seealso::

    DXF Internals: :ref:`tables_section_internals`

.. class:: TablesSection

    .. attribute:: layers

        :class:`~ezdxf.sections.table.LayerTable` object for :class:`~ezdxf.entities.Layer` objects

    .. attribute:: linetypes

        Generic :class:`~ezdxf.sections.table.Table` object for :class:`~ezdxf.entities.Linetype` objects

    .. attribute:: styles

        :class:`~ezdxf.sections.table.StyleTable` object for :class:`~ezdxf.entities.Textstyle` objects

    .. attribute:: dimstyles

        Generic :class:`~ezdxf.sections.table.Table` object for :class:`~ezdxf.entities.DimStyle` objects

    .. attribute:: appids

        Generic :class:`~ezdxf.sections.table.Table` object for :class:`~ezdxf.entities.AppID` objects

    .. attribute:: ucs

        Generic :class:`~ezdxf.sections.table.Table` object for :class:`~ezdxf.entities.UCSTable` objects

    .. attribute:: views

        Generic :class:`~ezdxf.sections.table.Table` object for :class:`~ezdxf.entities.View` objects

    .. attribute:: viewports

        :class:`~ezdxf.sections.table.ViewportTable` object for :class:`~ezdxf.entities.VPort` objects

    .. attribute:: block_records

        Generic :class:`~ezdxf.sections.table.Table` object for :class:`~ezdxf.entities.BlockRecord` objects


