DXF Entity Base Class
=====================

.. module:: ezdxf.entities.dxfentity

.. class:: DXFEntity

    Common base class for all DXF entities.

    .. warning::

        Do not instantiate entity classes by yourself - always use the provided factory functions!

    .. attribute:: dxf

        The DXF attributes namespace, access DXF attributes by this attribute, like :code:`entity.dxf.layer = 'MyLayer'`.
        Just the :attr:`dxf` attribute is read only, the DXF attributes are read- and writeable.

    .. attribute:: doc

        Get the associated :class:`~ezdxf.drawing.Drawing`. (read only)

        .. versionchanged:: 0.10

            renamed from ``drawing``

    .. autoattribute:: is_alive

    .. automethod:: dxftype

    .. automethod:: __str__

    .. automethod:: __repr__

    .. automethod:: get_dxf_attrib

    .. automethod:: set_dxf_attrib

    .. automethod:: del_dxf_attrib

    .. automethod:: has_dxf_attrib

    .. automethod:: is_supported_dxf_attrib

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

    .. automethod:: discard_xdata

    .. automethod:: has_reactors

    .. automethod:: get_reactors

    .. automethod:: set_reactors

    .. automethod:: append_reactor_handle

    .. automethod:: discard_reactor_handle

.. _Common DXF attributes for DXF R12:

Common DXF Attributes for DXF R12
---------------------------------

    .. attribute:: DXFEntity.dxf.handle

        DXF handle (feature for experts), unique identifier as plain hex string like ``F000``.

.. _Common DXF attributes for DXF R13 or later:

Common DXF Attributes for DXF R13 or later
------------------------------------------

    .. attribute:: DXFEntity.dxf.handle

        DXF handle (feature for experts), unique identifier as plain hex string like ``F000``.

    .. attribute:: DXFEntity.dxf.owner

        Handle to owner (feature for experts)

