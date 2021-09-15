.. _reactors:

Reactors
========

Persistent reactors are optional object handles of objects registering
themselves as reactors on an object. Any DXF object or DXF entity may have
reactors.

Use the high level methods of :class:`~ezdxf.entities.DXFEntity` to manage
persistent reactor handles.

- :meth:`~ezdxf.entities.DXFEntity.has_reactors`
- :meth:`~ezdxf.entities.DXFEntity.get_reactors`
- :meth:`~ezdxf.entities.DXFEntity.set_reactors`
- :meth:`~ezdxf.entities.DXFEntity.append_reactor_handle`
- :meth:`~ezdxf.entities.DXFEntity.discard_reactor_handle`

*Ezdxf* keeps these reactors only up to date, if this is absolute necessary
according to the DXF reference.

.. seealso::

    - Internals about :ref:`reactors_internals`
    - Internal Reactors management class: :class:`~ezdxf.entities.appdata.Reactors`
