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

Linetype Table
--------------

Generic table class  of :class:`Table`.

Collection of :class:`~ezdxf.entities.Linetype` objects.


Style Table
-----------

.. class:: StyleTable

    Subclass of :class:`Table`.

    Collection of :class:`~ezdxf.entities.Textstyle` objects.

    .. automethod:: get_shx(shxname: str) -> Textstyle

    .. automethod:: find_shx(shxname: str) -> Optional[Textstyle]


DimStyle Table
--------------

Generic table class of :class:`Table`.

Collection of :class:`~ezdxf.entities.DimStyle` objects.


AppID Table
-----------

Generic table class of :class:`Table`.

Collection of :class:`~ezdxf.entities.AppID` objects.

UCS Table
---------

Generic table class of :class:`Table`.

Collection of :class:`~ezdxf.entities.UCSTable` objects.

View Table
----------

Generic table class of :class:`Table`.

Collection of :class:`~ezdxf.entities.View` objects.


Viewport Table
--------------

.. class:: ViewportTable

    The viewport table stores the modelspace viewport configurations. A viewport configuration is a tiled view of
    multiple viewports or just one viewport. In contrast to other tables the viewport table can have multiple entries
    with the same name, because all viewport entries of a multi-viewport configuration are having the same name - the
    viewport configuration name.

    The name of the actual displayed viewport configuration is ``'*ACTIVE'``.

    Duplication of table entries is not supported: :meth:`duplicate_entry` raises :class:`NotImplementedError`

    .. automethod:: get_config(self, name: str) -> List[Viewport]

    .. automethod:: delete_config


Block Record Table
------------------

Generic table class of :class:`Table`.

Collection of :class:`~ezdxf.entities.BlockRecord` objects.
