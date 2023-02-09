DXF Entity Base Class
=====================

.. module:: ezdxf.entities
    :noindex:

Common base class for all DXF entities and objects.

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. if adding features - also update DXFObject

.. class:: DXFEntity

    .. attribute:: dxf

        The DXF attributes namespace::

            # set attribute value
            entity.dxf.layer = 'MyLayer'

            # get attribute value
            linetype = entity.dxf.linetype

            # delete attribute
            del entity.dxf.linetype



    .. attribute:: dxf.handle

        DXF `handle` is a unique identifier as plain hex string like ``F000``. (feature for experts)

    .. attribute:: dxf.owner

        Handle to `owner` as plain hex string like ``F000``. (feature for experts)

    .. attribute:: doc

        Get the associated :class:`~ezdxf.document.Drawing` instance.

    .. autoproperty:: is_alive

    .. autoproperty:: is_virtual

    .. autoproperty:: is_bound

    .. autoproperty:: is_copy

    .. autoproperty:: uuid

    .. autoproperty:: source_of_copy

    .. autoproperty:: origin_of_copy

    .. autoproperty:: has_source_block_reference

    .. autoproperty:: source_block_reference

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

    .. autoattribute:: has_extension_dict

    .. automethod:: get_extension_dict

    .. automethod:: new_extension_dict

    .. automethod:: discard_extension_dict

    .. automethod:: has_app_data

    .. automethod:: get_app_data

    .. automethod:: set_app_data

    .. automethod:: discard_app_data

    .. automethod:: has_xdata

    .. automethod:: get_xdata

    .. automethod:: set_xdata

    .. automethod:: discard_xdata

    .. automethod:: has_xdata_list

    .. automethod:: get_xdata_list

    .. automethod:: set_xdata_list

    .. automethod:: discard_xdata_list

    .. automethod:: replace_xdata_list

    .. automethod:: has_reactors

    .. automethod:: get_reactors

    .. automethod:: set_reactors

    .. automethod:: append_reactor_handle

    .. automethod:: discard_reactor_handle

