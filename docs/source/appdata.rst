
.. _application_defined_data:

Application-Defined Data (AppData)
==================================

The application-defined data feature is not very well documented in the DXF
reference, so usage as custom data store is not recommended. AutoCAD
uses these feature to store the handle to the extension dictionary
(:class:`~ezdxf.entities.xdict.ExtensionDict`) of a DXF entity and the handles
to the persistent reactors (:class:`~ezdxf.entities.appdata.Reactors`) of a
DXF entity.

Use the high level methods of :class:`~ezdxf.entities.DXFEntity` to manage
application-defined data tags.

- :meth:`~ezdxf.entities.DXFEntity.has_app_data`
- :meth:`~ezdxf.entities.DXFEntity.get_app_data`
- :meth:`~ezdxf.entities.DXFEntity.set_app_data`
- :meth:`~ezdxf.entities.DXFEntity.discard_app_data`

.. hint::

    Ezdxf uses special classes to manage the extension dictionary and the
    reactor handles. These features cannot be accessed by the methods above.

Set application-defined data::

    entity.set_app_data("YOURAPPID", [(1, "DataString")]))

Setting the content tags can contain the opening structure tag
(102, "{YOURAPPID") and the closing tag (102, "}"), but doesn't have to.
The returned :class:`~ezdxf.lldxf.tags.Tags` objects does not contain these
structure tags. Which tags are valid for application-defined data is not
documented.

The AppID has to have an entry in the AppID table.

Get application-defined data::

    if entity.has_app_data("YOURAPPID"):
        tags = entity.get_app_data("YOURAPPID")

    # tags content is [DXFTag(1, 'DataString')]

.. seealso::

    - Internals about :ref:`app_data_internals`
    - Internal AppData management class: :class:`~ezdxf.entities.appdata.AppData`


