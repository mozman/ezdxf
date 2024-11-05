.. _get_extended_data:

Get Extended Data from DXF Entities
===================================

HEADER Variables
----------------

.. code-block:: Python

    i1 = doc.header["$USERI1"]  # integer
    r1 = doc.header["$USERR1"]  # float


XDATA Section
-------------

The structure of XDATA is arbitrary and only some structures used by AutoCAD are
documented in the DXF reference. Use the :ref:`browse_command` command to explore these
structures directly in DXF files.

.. code-block:: Python

    my_app_id = "MY_APP_1"
    if line.has_xdata(my_app_id):
        tags = line.get_xdata(my_app_id)
        print(f"{str(line)} has {len(tags)} tags of XDATA for AppID {my_app_id!r}")
        for tag in tags:
            print(tag)

- :meth:`ezdxf.entities.DXFEntity.get_xdata`

Extension Dictionaries
----------------------

Like XDATA the structure of extension dictionaries is arbitrary and not documented by
the DXF reference.

.. code-block:: Python

    for line in msp.query("LINE"):
        if line.has_extension_dict:
            # get the extension dictionary
            xdict = line.get_extension_dict()

- :meth:`ezdxf.entities.DXFEntity.get_extension_dict`

.. seealso::

    **Tasks:**

    - :ref:`add_custom_data`
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
    