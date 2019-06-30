.. automodule:: ezdxf.lldxf.tags

.. autoclass:: Tags(list)
    :members:


.. module:: ezdxf.lldxf.extendedtags

.. class:: ExtendedTags(tags: Iterable[DXFTag]=None, legacy=False)

    Represents the extended DXF tag structure introduced with DXF R13.

    Args:
        tags: iterable of :class:`~ezdxf.lldxf.types.DXFTag`
        legacy: flag for DXF R12 tags

    .. attribute:: appdata

        Application defined data as list of :class:`Tags`

    .. attribute:: subclasses

        Subclasses as list of :class:`Tags`

    .. attribute:: xdata

        XDATA as list of :class:`Tags`

    .. attribute:: embedded_objects

        embedded objects as list of :class:`Tags`

    .. autoattribute:: noclass

    .. automethod:: get_handle

    .. automethod:: dxftype

    .. automethod:: replace_handle

    .. automethod:: legacy_repair

    .. automethod:: clone() -> ExtendedTags

    .. automethod:: flatten_subclasses

    .. automethod:: get_subclass(name: str, pos: int = 0) -> Tags

    .. automethod:: has_xdata

    .. automethod:: get_xdata(appid: str) -> Tags

    .. automethod:: set_xdata

    .. automethod:: new_xdata(appid: str, tags: 'IterableTags' = None) -> Tags

    .. automethod:: has_app_data

    .. automethod:: get_app_data(appid: str) -> Tags

    .. automethod:: get_app_data_content(appid: str) -> Tags

    .. automethod:: set_app_data_content

    .. automethod:: new_app_data(appid: str, tags: 'IterableTags' = None, subclass_name: str = None) -> Tags

    .. automethod:: from_text(text: str, legacy: bool = False) -> ExtendedTags


.. module:: ezdxf.lldxf.packedtags

Packed DXF Tags
---------------

Store DXF tags in compact data structures as ``list`` or :class:`array.array` to reduce memory usage.

.. class:: TagList(data: Iterable = None)

    Store data in a standard Python ``list``.

    Args:
        data: iterable of DXF tag values.

    .. attribute:: values

        Data storage as ``list``.

    .. automethod:: clone() -> TagList

    .. automethod:: from_tags(tags: Tags, code: int) -> TagList

    .. automethod:: clear

.. class:: TagArray(data: Iterable = None)

    :class:`TagArray` is a subclass of :class:`TagList`, which store data in an :class:`array.array`.
    Array type is defined by class variable ``DTYPE``.

    Args:
        data: iterable of DXF tag values.

    .. attribute:: DTYPE

        :class:`array.array` type as string

    .. attribute:: values

        Data storage as :class:`array.array`

    .. automethod:: set_values

.. class:: VertexArray(data: Iterable = None)

    Store vertices in an ``array.array('d')``.
    Vertex size is defined by class variable :attr:`VERTEX_SIZE`.

    Args:
        data: iterable of vertex values as linear list e.g. :code:`[x1, y1, x2, y2, x3, y3, ...]`.

    .. attribute:: VERTEX_SIZE

        Size of vertex (2 or 3 axis).

    .. automethod:: __len__

    .. automethod:: __getitem__

    .. automethod:: __setitem__

    .. automethod:: __delitem__

    .. automethod:: __iter__

    .. automethod:: __str__

    .. automethod:: insert

    .. automethod:: append

    .. automethod:: extend

    .. automethod:: set

    .. automethod:: clear

    .. automethod:: clone() -> VertexArray

    .. automethod:: from_tags(tags: Iterable[DXFTag], code: int = 10) -> VertexArray

    .. automethod:: export_dxf

