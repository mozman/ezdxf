.. _extended_data:

Extended Data (XDATA)
=====================

Extended data (XDATA) is a DXF tags structure to store arbitrary data in DXF
entities. The XDATA is associated to an :class:`~ezdxf.entities.AppID` and only
one tag list is supported for each AppID per entity.

.. warning::

    Low level usage of XDATA is an advanced feature, it is the responsibility
    of the programmer to create valid XDATA structures. Any errors can
    invalidate the DXF file!

This section shows how to store DXF tags directly in DXF entity but there is
also a more user friendly and safer way to store custom XDATA in DXF entities:

- :class:`~ezdxf.entities.xdata.XDataUserList`
- :class:`~ezdxf.entities.xdata.XDataUserDict`

Use the high level methods of :class:`~ezdxf.entities.DXFEntity` to manage XDATA
tags.

- :meth:`~ezdxf.entities.DXFEntity.has_xdata`
- :meth:`~ezdxf.entities.DXFEntity.get_xdata`
- :meth:`~ezdxf.entities.DXFEntity.set_xdata`

Get XDATA tags as a :class:`ezdxf.lldxf.tags.Tags` data structure, **without**
the mandatory first tag (1001, AppID)::

    if entity.has_xdata("EZDXF"):
        tags = entity.get_xdata("EZDXF")

    # or use alternatively:
    try:
        tags = entity.get_xdata("EZDXF")
    except DXFValueError:
        # XDATA for "EZDXF" does not exist
        ...

Set DXF tags as list of (group code, value) tuples or as
:class:`ezdxf.lldxf.tags.Tags` data structure, valid DXF tags for XDATA are
documented in the section about the :ref:`xdata_internals` internals.
The mandatory first tag (1001, AppID) is inserted automatically if not present.

Set only new XDATA tags::

    if not entity.has_xdata("EZDXF"):
        entity.set_xdata("EZDXF", [(1000, "MyString")])

Replace or set new XDATA tags::

    entity.set_xdata("EZDXF", [(1000, "MyString")])


.. seealso::

    - Internals about :ref:`xdata_internals` tags
    - Internal XDATA management class: :class:`~ezdxf.entities.xdata.XData`
    - `DXF R2018 Reference <https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-A2A628B0-3699-4740-A215-C560E7242F63>`_