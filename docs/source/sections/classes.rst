Classes Section
===============

The CLASSES section in DXF files holds the information for application-defined classes
whose instances appear in :class:`~ezdxf.layouts.Layout` objects. As usual package user
there is no need to bother about CLASSES.

.. seealso::

    DXF Internals: :ref:`classes_section_internals`

.. module:: ezdxf.sections.classes

.. class:: ClassesSection

    .. attribute:: classes

        Storage of all :class:`~ezdxf.entities.DXFClass` objects, they are not stored in
        the entities database, because CLASS instances do not have a handle attribute.

    .. method:: register

    .. automethod:: add_class

    .. automethod:: get

    .. automethod:: add_required_classes

    .. automethod:: update_instance_counters

.. module:: ezdxf.entities
    :noindex:

.. class:: DXFClass

    Information about application-defined classes.

    .. attribute:: dxf.name

        Class DXF record name.

    .. attribute:: dxf.cpp_class_name

        C++ class name. Used to bind with software that defines object class behavior.

    .. attribute:: dxf.app_name

        Application name. Posted in Alert box when a class definition listed in this section is not currently loaded.

    .. attribute:: dxf.flags

        Proxy capabilities flag

        ======= =========================
        0       No operations allowed (0)
        1       Erase allowed (0x1)
        2       Transform allowed (0x2)
        4       Color change allowed (0x4)
        8       Layer change allowed (0x8)
        16      Linetype change allowed (0x10)
        32      Linetype scale change allowed (0x20)
        64      Visibility change allowed (0x40)
        128     Cloning allowed (0x80)
        256     Lineweight change allowed (0x100)
        512     Plot Style Name change allowed (0x200)
        895     All operations except cloning allowed (0x37F)
        1023    All operations allowed (0x3FF)
        1024    Disables proxy warning dialog (0x400)
        32768   R13 format proxy (0x8000)
        ======= =========================

    .. attribute:: dxf.instance_count

        Instance count for a custom class.

    .. attribute:: dxf.was_a_proxy

        Set to ``1`` if class was not loaded when this DXF file was created, and ``0`` otherwise.

    .. attribute:: dxf.is_an_entity

        Set to ``1`` if class was derived from the :class:`DXFGraphic` class and can reside in layouts.
        If ``0``, instances may appear only in the OBJECTS section.

    .. attribute:: key

        Unique name as ``(name, cpp_class_name)`` tuple.