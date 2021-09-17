.. _extension_dictionary:

.. module:: ezdxf.entities.xdict

Extension Dictionary
====================

Every entity can have an extension dictionary, which can reference arbitrary
DXF objects from the OBJECTS section but not graphical entities. Using this
mechanism, several applications can attach data to the same entity.
The usage of extension dictionaries is more complex than :ref:`extended_data`
but also more flexible with higher capacity for adding data.

Use the high level methods of :class:`~ezdxf.entities.DXFEntity` to manage
extension dictionaries.

- :meth:`~ezdxf.entities.DXFEntity.has_extension_dict`
- :meth:`~ezdxf.entities.DXFEntity.get_extension_dict`
- :meth:`~ezdxf.entities.DXFEntity.new_extension_dict`
- :meth:`~ezdxf.entities.DXFEntity.discard_extension_dict`

The main data storage objects referenced by extension dictionaries are:

- :class:`~ezdxf.entities.Dictionary`, structural container
- :class:`~ezdxf.entities.DictionaryVar`, stores a single string
- :class:`~ezdxf.entities.XRecord`, stores arbitrary data

.. seealso::

    - Tutorial: :ref:`tut_custom_data`

.. class:: ExtensionDict

    Internal management class for extension dictionaries.

    .. seealso::

        - Underlying DXF :class:`~ezdxf.entities.Dictionary` class
        - DXF Internals: :ref:`extension_dict_internals`
        - `DXF R2018 Reference`_

    .. autoproperty:: is_alive

    .. automethod:: __contains__

    .. automethod:: __getitem__

    .. automethod:: __setitem__

    .. automethod:: __delitem__

    .. automethod:: __len__

    .. automethod:: get

    .. automethod:: keys

    .. automethod:: items

    .. automethod:: discard

    .. automethod:: add_dictionary

    .. automethod:: add_dictionary_var

    .. automethod:: add_xrecord

    .. automethod:: link_dxf_object

    .. automethod:: destroy

.. _DXF R2018 Reference: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-A55D4A3D-67CF-417E-B63F-3124CD8027FD