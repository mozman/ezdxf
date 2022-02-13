.. module:: ezdxf.entitydb

Entity Database
===============

The :class:`EntityDB` is a simple key/value database to store
:class:`~ezdxf.entities.DXFEntity` objects by it's handle,
every :class:`~ezdxf.document.Drawing` has its own :class:`EntityDB`, stored in
the :class:`Drawing` attribute :attr:`~ezdxf.document.Drawing.entitydb`.

Every DXF entity/object, except tables and sections, are represented as
:class:`DXFEntity` or inherited types, this entities are stored in the
:class:`EntityDB`, database-key is the :attr:`dxf.handle` as plain hex
string.

All iterators like :meth:`keys`, :meth:`values`, :meth:`items` and :meth:`__iter__`
do not yield destroyed entities.

.. warning::

    The :meth:`get` method and the index operator ``[]``, return destroyed
    entities and entities from the trashcan.

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

    .. automethod:: new_trashcan

    .. automethod:: trashcan

    .. automethod:: purge

    .. automethod:: query

Entity Space
============

.. autoclass:: EntitySpace

    .. automethod:: __iter__() -> Iterable[DXFEntity]

    .. automethod:: __getitem__(index) -> DXFEntity

    .. automethod:: __len__

    .. automethod:: has_handle

    .. automethod:: purge

    .. automethod:: add(entity: DXFEntity) -> None

    .. automethod:: extend(entities: Iterable[DXFEntity]) -> None

    .. automethod:: remove(entity: DXFEntity) -> None

    .. automethod:: clear