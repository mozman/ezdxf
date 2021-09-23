Dictionary
==========

.. module:: ezdxf.entities
    :noindex:

The `DICTIONARY`_ is a general storage entity.

AutoCAD maintains items such as MLINE_STYLES and GROUP definitions as objects in
dictionaries. Other applications are free to create and use their own
dictionaries as they see fit. The prefix ``'ACAD_'`` is reserved for use by
AutoCAD applications.

Dictionary entries are (key, :class:`DXFEntity`) pairs for fully loaded or
new created DXF documents. The referenced entities are owned by the dictionary
and cannot be graphical entities that always belong to the layout in which they
are located.

Loading DXF files is done in two passes, because at the first loading stage not
all referenced objects are already stored in the entity database. Therefore the
entities are stored as handles strings at the first loading stage and have to
be replaced by the real entity at the second loading stage.
If the entity is still a handle string after the second loading stage, the
entity does not exist.

Dictionary keys are handled case insensitive by AutoCAD, but not by `ezdxf`,
in doubt use an uppercase key. AutoCAD stores all keys in uppercase.

======================== =============================================================
Subclass of              :class:`ezdxf.entities.DXFObject`
DXF type                 ``'DICTIONARY'``
Factory function         :meth:`ezdxf.sections.objects.ObjectsSection.add_dictionary`
======================== =============================================================

.. warning::

    Do not instantiate object classes by yourself - always use the provided
    factory functions!

.. class:: Dictionary

    .. attribute:: dxf.hard_owned

        If set to ``1``, indicates that elements of the dictionary are to be
        treated as hard-owned.

    .. attribute:: dxf.cloning

        Duplicate record cloning flag (determines how to merge duplicate entries,
        ignored by `ezdxf`):

        === ==================
        0   not applicable
        1   keep existing
        2   use clone
        3   <xref>$0$<name>
        4   $0$<name>
        5   Unmangle name
        === ==================


    .. autoattribute:: is_hard_owner

    .. automethod:: __len__

    .. automethod:: __contains__

    .. automethod:: __getitem__(key: str) -> DXFEntity

    .. automethod:: __setitem__(key: str, value: DXFEntity) -> None

    .. automethod:: __delitem__

    .. automethod:: keys() -> KeysView

    .. automethod:: items() -> ItemsView

    .. automethod:: count

    .. automethod:: get(key: str, default: DXFEntity = None) -> Optional[DXFEntity]

    .. automethod:: add(key: str, value: DXFEntity) -> None

    .. automethod:: remove

    .. automethod:: discard

    .. automethod:: clear

    .. automethod:: add_new_dict(key: str, hard_owned: bool = False) -> Dictionary

    .. automethod:: get_required_dict(key: str) -> Dictionary

    .. automethod:: add_dict_var(key: str, value: str) -> DictionaryVar

    .. automethod:: add_xrecord(key: str) -> XRecord

    .. automethod:: link_dxf_object(name: str, obj: DXFEntity) -> None


.. _DICTIONARY: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-40B92C63-26F0-485B-A9C2-B349099B26D0

DictionaryWithDefault
=====================

======================== =========================================================================
Subclass of              :class:`ezdxf.entities.Dictionary`
DXF type                 ``'ACDBDICTIONARYWDFLT'``
Factory function         :meth:`ezdxf.sections.objects.ObjectsSection.add_dictionary_with_default`
======================== =========================================================================

.. class:: DictionaryWithDefault

    .. attribute:: dxf.default

        Handle to default entry as hex string like ``FF00``.

    .. automethod:: get(key: str) -> DXFEntity

    .. automethod:: set_default


DictionaryVar
=============

======================== =========================================================================
Subclass of              :class:`ezdxf.entities.DXFObject`
DXF type                 ``'DICTIONARYVAR'``
Factory function         :meth:`ezdxf.entities.Dictionary.add_dict_var`
======================== =========================================================================

.. class:: DictionaryVar

    .. attribute:: dxf.schema

        Object schema number (currently set to ``0``)

    .. attribute:: dxf.value

        Value as string.

    .. autoproperty:: value