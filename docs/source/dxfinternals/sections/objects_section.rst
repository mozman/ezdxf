.. _objects_section_internals:

OBJECTS Section
===============

Objects in the OBJECTS section are organized in a hierarchical tree order, starting with the
`named objects dictionary` as the first entity in the OBJECTS section (:attr:`Drawing.rootdict`).

Not all entities in the OBJECTS section are included in this tree, :ref:`extension_dict_internals` and XRECORD data of
graphical entities are also stored in the OBJECTS section.
