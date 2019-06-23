DXF Entity Base Class
=====================

.. module:: ezdxf.entities

Common base class for all DXF entities and objects.

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: DXFEntity

    .. attribute:: dxf

        The DXF attributes namespace::

            # set attribute value
            entity.dxf.layer = 'MyLayer'

            # get attribute value
            linetype = entity.dxf.linetype

            # delete attribute
            del entity.dxf.linetype



    .. attribute:: DXFEntity.dxf.handle

        DXF `handle` is a unique identifier as plain hex string like ``F000``. (feature for experts)

    .. attribute:: DXFEntity.dxf.owner

        Handle to `owner` as plain hex string like ``F000``. (feature for experts)

    .. attribute:: doc

        Get the associated :class:`~ezdxf.drawing.Drawing` instance.

        .. versionchanged:: 0.10

            renamed from ``drawing``

    .. attribute:: priority

        Integer value defining order of entities: highest value first ``100`` (top) before ``0`` (default) before
        ``-100`` (bottom), priority support not implemented yet, setting :attr:`priority` has no effect.

    .. autoattribute:: is_alive

    .. automethod:: dxftype

    .. automethod:: __str__

    .. automethod:: __repr__

    .. automethod:: has_dxf_attrib

    .. automethod:: is_supported_dxf_attrib

    .. automethod:: get_dxf_attrib

    .. automethod:: set_dxf_attrib

    .. automethod:: del_dxf_attrib

    .. automethod:: dxfattribs

    .. automethod:: update_dxf_attribs

    .. automethod:: set_flag_state

    .. automethod:: get_flag_state

    .. automethod:: has_extension_dict

    .. automethod:: get_extension_dict() -> ExtensionDict

    .. automethod:: has_app_data

    .. automethod:: get_app_data(appid: str) -> Tags

    .. automethod:: set_app_data(appid: str, tags: Iterable)

    .. automethod:: discard_app_data

    .. automethod:: has_xdata

    .. automethod:: get_xdata(appid: str) -> Tags

    .. automethod:: set_xdata(appid: str, tags: Iterable)

    .. automethod:: has_xdata_list

    .. automethod:: get_xdata_list(appid: str, name: str) -> Tags

    .. automethod:: set_xdata_list(appid: str, name: str, tags: Iterable)

    .. automethod:: discard_xdata_list

    .. automethod:: replace_xdata_list(appid: str, name: str, tags: Iterable)

    .. automethod:: has_reactors

    .. automethod:: get_reactors

    .. automethod:: set_reactors

    .. automethod:: append_reactor_handle

    .. automethod:: discard_reactor_handle

