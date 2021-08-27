Table Classes
=============

.. module:: ezdxf.sections.table

Generic Table Class
-------------------

.. class:: Table

    Generic collection of table entries. Table entry names are case insensitive: ``'Test' == 'TEST'``.

    .. automethod:: key(entity: Union[str, DXFEntity]) -> str

    .. automethod:: has_entry(name: Union[str, DXFEntity]) -> bool

    .. automethod:: __contains__(name: Union[str, DXFEntity]) -> bool

    .. automethod:: __len__

    .. automethod:: __iter__() -> Iterable[DXFEntity]

    .. automethod:: new(name: str, dxfattribs: dict = None) -> DXFEntity

    .. automethod:: get(name: str) -> DXFEntity

    .. automethod:: remove

    .. automethod:: duplicate_entry(name: str, new_name: str) -> DXFEntity

Layer Table
-----------

.. class:: LayerTable

    Subclass of :class:`Table`.

    Collection of :class:`~ezdxf.entities.Layer` objects.

    .. automethod:: add

Linetype Table
--------------

.. class:: LineTypeTable

    Subclass of :class:`Table`.

    Collection of :class:`~ezdxf.entities.Linetype` objects.

    .. automethod:: add

Style Table
-----------

.. class:: StyleTable

    Subclass of :class:`Table`.

    Collection of :class:`~ezdxf.entities.Textstyle` objects.

    .. automethod:: add

    .. automethod:: add_shx

    .. automethod:: get_shx

    .. automethod:: find_shx


DimStyle Table
--------------



.. class:: DimStyleTable

    Subclass of :class:`Table`.

    Collection of :class:`~ezdxf.entities.DimStyle` objects.

    .. automethod:: add

AppID Table
-----------

.. class:: AppIDTable

    Subclass of :class:`Table`.

    Collection of :class:`~ezdxf.entities.AppID` objects.

    .. automethod:: add

UCS Table
---------

.. class:: UCSTable

    Subclass of :class:`Table`.

    Collection of :class:`~ezdxf.entities.UCSTableEntry` objects.

    .. automethod:: add

View Table
----------

.. class:: ViewTable

    Subclass of :class:`Table`.

    Collection of :class:`~ezdxf.entities.View` objects.

    .. automethod:: add

Viewport Table
--------------

.. class:: ViewportTable

    The viewport table stores the modelspace viewport configurations. A viewport configuration is a tiled view of
    multiple viewports or just one viewport. In contrast to other tables the viewport table can have multiple entries
    with the same name, because all viewport entries of a multi-viewport configuration are having the same name - the
    viewport configuration name.

    The name of the actual displayed viewport configuration is ``'*ACTIVE'``.

    Duplication of table entries is not supported: :meth:`duplicate_entry` raises :class:`NotImplementedError`

    .. automethod:: add

    .. automethod:: get_config(self, name: str) -> List[VPort]

    .. automethod:: delete_config



Block Record Table
------------------

.. class:: BlockRecordTable

    Subclass of :class:`Table`.

    Collection of :class:`~ezdxf.entities.BlockRecord` objects.

    .. automethod:: add