
Block Reference Management
==========================

The package `ezdxf` is not designed as a CAD library and does not automatically
monitor all internal changes. This enables faster entity processing at the cost
of an unknown state of the DXF document.

In order to carry out precise BLOCK reference management, i.e. to handle
dependencies or to delete unused BLOCK definition, the block reference status
(counter) must be acquired explicitly by the package user.
All block reference management structures must be explicitly recreated each time
the document content is changed. This is not very efficient, but it is safe.

.. warning::

    And even with all this careful approach, it is always possible to destroy a
    DXF document by deleting an absolutely necessary block definition.

Always remember that `ezdxf` is not intended or suitable as a basis for a CAD
application!


.. module:: ezdxf.blkrefs

.. autoclass:: BlockDefinitionIndex

    .. autoproperty:: block_records

    .. automethod:: rebuild

    .. automethod:: has_handle

    .. automethod:: by_handle

    .. automethod:: has_name

    .. automethod:: by_name

.. autoclass:: BlockReferenceCounter

    .. automethod:: by_handle

    .. automethod:: by_name
