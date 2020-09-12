Header Section
==============

.. module:: ezdxf.sections.header

The drawing settings are stored in the HEADER section, which is accessible by the :attr:`~ezdxf.document.Drawing.header`
attribute of the :class:`~ezdxf.document.Drawing` object. See the online documentation from Autodesk for available
`header variables`_.

.. seealso::

    DXF Internals: :ref:`header_section_internals`

.. class:: HeaderSection

    .. attribute:: custom_vars

       Stores the custom drawing properties in a :class:`CustomVars` object.

    .. automethod:: __len__

    .. automethod:: __contains__

    .. automethod:: varnames

    .. automethod:: get

    .. automethod:: __getitem__

    .. automethod:: __setitem__

    .. automethod:: __delitem__


.. autoclass:: CustomVars

    .. attribute:: properties

       List of custom drawing properties, stored as string tuples ``(tag, value)``. Multiple occurrence of the same custom
       tag is allowed, but not well supported by the interface. This is a standard python list and it is save to change this
       list as long you store just tuples of strings in the format ``(tag, value)``.

    .. automethod:: __len__

    .. automethod:: __iter__

    .. automethod:: clear

    .. automethod:: get

    .. automethod:: has_tag

    .. automethod:: append

    .. automethod:: replace

    .. automethod:: remove


.. _header variables: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-A85E8E67-27CD-4C59-BE61-4DC9FADBE74A