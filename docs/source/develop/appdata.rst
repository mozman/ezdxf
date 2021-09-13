
Application-Defined Data (AppData)
==================================

Starting at DXF R13, DXF objects can contain application-defined codes (AppData)
outside of XDATA.

All AppData is defined with a beginning (102, "{APPID") tag and according to the
DXF reference appear should appear before the first subclass marker.

There are two known use cases of this data structure in Autodesk products:

- ``ACAD_REACTORS``, store handles to persistent reactors in a DXF entity
- ``ACAD_XDICTIONARY``, store handle to the extension dictionary of a DXF entity

Both AppIDs are not defined/stored in the AppID table!

.. module:: ezdxf.entities.appdata

.. class:: AppData

    Internal management class for Application defined data.

    .. seealso::

        - User reference: :ref:`application_defined_data`
        - Internals about :ref:`app_data_internals` tags

    .. automethod:: __contains__

    .. automethod:: __len__

    .. automethod:: add

    .. automethod:: get

    .. automethod:: set

    .. automethod:: discard
