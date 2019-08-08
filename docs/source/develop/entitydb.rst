.. module:: ezdxf.entitydb

Entity Database
===============

The :class:`EntityDB` is a simple key/value database to store :class:`~ezdxf.entities.DXFEntity` objects by it's handle,
every :class:`~ezdxf.drawing.Drawing` has its own :class:`EntityDB`, stored in the :class:`~ezdxf.drawing.Drawing`
attribute :attr:`~ezdxf.drawing.Drawing.entitydb`.

Every DXF entity/object, except tables and sections, are represented as :class:`~ezdxf.entities.dxfentity.DXFEntity` or
inherited types, this entities are stored in the :class:`EntityDB`, database-key is the :attr:`dxf.handle` as plain hex
string (group code 5 or 105).


.. class:: EntityDB

    .. automethod:: __getitem__(handle: str) -> DXFEntity

    .. automethod:: __setitem__(handle: str, entity: DXFEntity) -> None

    .. automethod:: __delitem__

    .. automethod:: __contains__(item: Union[str, DXFEntity]) -> bool

    .. automethod:: __len__

    .. automethod:: __iter__

    .. automethod:: get(handle: str) -> Optional[DXFEntity]

    .. automethod:: next_handle

    .. automethod:: keys

    .. automethod:: values() -> Iterable[DXFEntity]

    .. automethod:: items()  -> Iterable[Tuple[str, DXFEntity]]

    .. automethod:: add(entity: DXFEntity) -> None

    .. automethod:: delete_entity(entity: DXFEntity) -> None

    .. automethod:: duplicate_entity(entity: DXFEntity) -> DXFEntity

Entity Space
============

.. autoclass:: EntitySpace

    .. automethod:: __iter__() -> Iterable[DXFEntity]

    .. automethod:: __getitem__(index) -> DXFEntity

    .. automethod:: __len__

    .. automethod:: has_handle

    .. automethod:: purge

    .. automethod:: reorder

    .. automethod:: add(entity: DXFEntity) -> None

    .. automethod:: extend(entities: Iterable[DXFEntity]) -> None

    .. automethod:: remove(entity: DXFEntity) -> None

    .. automethod:: clear