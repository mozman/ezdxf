XRecord
=======

.. module:: ezdxf.entities
    :noindex:

Important class for storing application defined data in DXF files.

`XRECORD`_ objects are used to store and manage arbitrary data. They are
composed of DXF group codes ranging from 1 through 369. This object is
similar in concept to XDATA but is not limited by size or order.

To reference a XRECORD by an DXF entity, store the handle of the XRECORD in the
XDATA section, application defined data or the :class:`ExtensionDict` of the
DXF entity.

.. seealso::

    - :ref:`extended_data`
    - :ref:`extension_dictionary`
    - :ref:`tut_custom_data`

.. _XRECORD: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-24668FAF-AE03-41AE-AFA4-276C3692827F

======================== ===========================================================
Subclass of              :class:`ezdxf.entities.DXFObject`
DXF type                 ``'XRECORD'``
Factory function         :meth:`ezdxf.sections.objects.ObjectsSection.add_xrecord`
======================== ===========================================================

.. warning::

    Do not instantiate object classes by yourself - always use the provided factory functions!

.. class:: XRecord

    .. attribute:: dxf.cloning

        Duplicate record cloning flag (determines how to merge duplicate entries, ignored by `ezdxf`):

        === ==================
        0   not applicable
        1   keep existing
        2   use clone
        3   <xref>$0$<name>
        4   $0$<name>
        5   Unmangle name
        === ==================

    .. attribute:: tags

        Raw DXF tag container :class:`~ezdxf.lldxf.tags.Tags`. Be careful `ezdxf` does not validate the content of
        XRECORDS.

    .. automethod:: clear

    .. automethod:: reset

    .. automethod:: extend
