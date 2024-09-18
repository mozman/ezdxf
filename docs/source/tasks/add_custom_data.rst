.. _add_custom_data:

Add Custom and Extended Data
============================

DXF supports storing custom data through various mechanisms.

Header Variables
----------------

Custom data can be stored in the HEADER section of a DXF file. Integer values are stored 
in variables named $USERI1 to $USERI5, while floating-point values are stored in 
variables named $USERR1 to $USERR5.

Example::

    doc.header["$USERI1"] = 17

XDATA Section
-------------

The XDATA section is a container for extended data associated with an entity. It's 
essentially a way to store additional information beyond the standard DXF properties for 
that particular entity. The XDATA section is divided into sub-sections, each associated 
with an AppID.

It's important that the AppID is registered in the AppID table::

    doc.appids.add("YOUR_ID")

- :meth:`ezdxf.sections.table.AppIDTable.add`

Example::

    point = msp.add_point((10, 10))
    point.set_xdata("YOUR_ID", (1040, 3.1415))

- :meth:`ezdxf.entities.DXFEntity.set_xdata`

Extension Dictionaries
----------------------

Each DXF entity can have an extension dictionary to attach custom data. 
The extension dictionary is a :class:`~ezdxf.entities.Dictionary` entity which stores 
references to other DXF entities in a key/value storage, mostly :class:`~ezdxf.entities.Dictionary` 
and :class:`~ezdxf.entities.XRecord` entities.

Example::

    point = msp.add_point((10, 10))
    xdict = point.new_extension_dict()

- :meth:`ezdxf.entities.DXFEntity.new_extension_dict`

Custom Data as XRECORD
----------------------

The XRECORD is used to store arbitrary data. It is composed of DXF group codes ranging 
from 1 through 369. This object is similar in concept to XDATA but is not limited by 
size or order.

Example::

    point = msp.add_point((10, 10))
    xdict = point.new_extension_dict()
    xrecord = xdict.add_xrecord("MyData")
    xrecord.extend([(1, "MyText"), (40, 3.1415)])

- :meth:`ezdxf.entities.xdict.ExtensionDict.add_xrecord`
- :meth:`ezdxf.entities.xdict.ExtensionDict.add_dictionary`
- :meth:`ezdxf.entities.xdict.ExtensionDict.add_dictionary_var`

.. seealso::

    **Tasks:**

    - :ref:`get_extended_data`
    - :ref:`modify_extended_data`
    - :ref:`delete_extended_data`
    
    **Tutorials:**

    - :ref:`tut_custom_data`

    **Basics:**
    
    - :ref:`xdata_internals`
    - :ref:`extension_dictionary`
    - :ref:`dxf_tags_internals`

    **Classes:**
    
    - :class:`ezdxf.entities.xdata.XData`
    - :class:`ezdxf.entities.xdict.ExtensionDict`
    - :class:`ezdxf.entities.XRecord`
    - :class:`ezdxf.entities.Dictionary`
    - :class:`ezdxf.entities.DictionaryVar`

    **Helper-Classes:**

    - :class:`ezdxf.entities.xdata.XDataUserList`
    - :class:`ezdxf.entities.xdata.XDataUserDict`
    - :class:`ezdxf.urecord.UserRecord`
    - :class:`ezdxf.urecord.BinaryRecord`
    