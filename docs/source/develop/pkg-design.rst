.. _pkg-design:

Package Design for Developers
=============================

The complete DXF document is stored in a :class:`~ezdxf.drawing.Drawing` object.
For each section of the DXF document exist a corresponding attribute in the
:class:`Drawing` object.
Resource entities are stored in tables in the TABLES section.
All graphical entities are stored in layouts.
All non-graphical entities are stored in the OBJECTS section.
All entities are stored in the entities database.

Terminology
+++++++++++

Virtual Entity
--------------

- UNBOUND: not stored in the entity database of a document; DXF attribute `handle` is ``None``
- UNLINKED: not linked to a layout/owner; DXF attribute `owner` is ``None``
- Attribute `doc` can be ``None``

Unlinked Entity
---------------

- BOUND: stored in an entity database, which means bound to a document:
  DXF attribute `handle` is not ``None`` and `doc` has a reference to the
  DXF document
- UNLINKED: not linked to a layout/owner: DXF attribute `owner` is ``None``

Bound Entity
------------

- BOUND: stored in an entity database, which means bound to a document:
  DXF attribute `handle` is not ``None`` and `doc` has a reference to the
  DXF document
- LINKED: linked to a layout/owner: DXF attribute `owner` is not ``None``

Loading DXF Documents
+++++++++++++++++++++

The loading process has two stages:

First Loading Stage
-------------------

- LOAD content from file/stream into a DXF structure database:
  :func:`loader.load_dxf_structure`
- Convert tag structures into DXFEntity objects: :func:`loader.load_dxf_entities`
- BIND entities to an EntityDB: :func:`load_and_bind_dxf_content`

Because of the missing DXF document structures, a complete validation is not
possible at this stage, only validation at the tag level is already done.

Second Loading Stage
--------------------

Parse DXF structure database:

- Create sections: HEADER, CLASSES, TABLES, BLOCKS and OBJECTS
- Create layouts: Blocks, Layouts
    - LINK entities to a layout

The ENTITIES section is a relict from older DXF versions and has to be exported
including the modelspace and active paperspace entities, but all entities
reside in a BLOCK definition, even modelspace and paperspace layouts are only
BLOCK definitions and ezdxf has no explicit ENTITIES section.

Creating New DXF Entities
+++++++++++++++++++++++++

The default constructor of each entity type creates a new virtual entity:

- DXF attribute `owner` is ``None``
- DXF attribute `handle` is ``None``
- Attribute `doc` is ``None``

The :meth:`DXFEntity.new` constructor creates entities with given `owner`,
`handle` and `doc` attributes, if `doc` is not ``None`` and entity is not
already bound to a document, the :meth:`new` constructor automatically bind the
entity to the given document `doc`.

There exist only two scenarios:

1. UNBOUND: `doc` is ``None`` and `handle` is ``None``
2. BOUND: `doc` is not ``None`` and `handle` is not ``None``

BIND
----

Binding the entity to a document means:

- BOUND: entity is stored in the document entity database, `handle`is set
  and `doc` attribute is set
- Check or create required resources
- UNLINKED: `owner` is still ``None``

LINK
----

This makes an entity to a real DXF entity, which will be exported
at the saving process. Any DXF entity can only be linked to **one** parent
entity like DICTIONARY or BLOCK_RECORD.

DXF Objects
-----------

- LINK to OBJECTS section by adding entity to a parent entity in the OBJECTS
  section, most likely a DICTIONARY object and store entity in the entity
  space of the OBJECTS section, the root-dict is the only entity in the objects
  section with an invalid owner handle "0".
- Extension dictionaries of graphical- or table entities can also own entities
  in the OBJECTS section.

DXF Entities
------------

- LINK entity to a layout by :meth:`BlockRecord.link`, which set the `owner`
  handle to BLOCK_RECORD handle (= layout key) and store entity in entity space
  of the BLOCK_RECORD
- set paperspace flag

Factory functions
+++++++++++++++++

- :func:`new`, create a new virtual DXF object/entity
- :func:`load`, load (create) virtual DXF object/entity from DXF tags
- :func:`bind`, bind an entity to a document, create required
  resources if necessary (e.g. ImageDefReactor, SEQEND) and raise exceptions for
  non-existing resources.
  For adding loaded or foreign entities see below, for entities created by a
  package-user raise an exception to informed about the invalid package usage.
- bind loaded and foreign entities:

  1. bind entity loaded from a file to a document, all referenced resources must
     exist, but try to repair as many flaws as possible, because this issues
     were created by another application and are not the responsibility of the
     package-user.

  2. bind an entity from another document, all invalid resources will be
     removed silently or created (e.g. SEQEND). This is a simple import from
     another document without resource import for a more advanced import
     including resources exist the :mod:`importer` add-on.

  Create an :class:`Auditor` and repair the entity, if unrecoverable errors exist:
  log the problem and kill the entity. Log applied fixes.
  This requires an fully initialized and valid DXF document.
- Bootstrap problem for binding loaded table entries and objects in the OBJECTS
  section! Can't use :class:`Auditor` to repair this objects, because the DXF
  document is not fully initialized.
- :func:`is_bound` returns True if `entity` is bound to document `doc`
- :func:`unbind` function to remove an entity from a document and set state
  to a virtual entity, which should also `UNLINK` the entity from layout,
  because an layout can not store a virtual entity.
- :func:`cls`, returns the class
- :func:`register_entity`, registration decorator
- :func:`replace_entity`, registration decorator

Class Interfaces
++++++++++++++++

Entities
--------

1. NEW interface as class method
2. LOAD interface as class method
3. DESTROY interface to kill an entity, set entity state to `dead`, which
   means :attr:`entity.is_alive` returns False. All entity iterators like
   :class:`EntitySpace`, :class:`EntityQuery`,  and :class:`EntityDB` must
   filter (ignore) `dead` entities.
   Calling :func:`DXFEntity.destroy()` is the normal way to delete entities.

Layouts
-------

1. LINK interface to assign a layout to an entity
1. UNLINK interface to remove a layout assignment from an entity
1. Layouts have back-link `doc` to the DXF document
1. Support for a virtual layout, which can store virtual entities
1. It is not possible to move or copy layouts between documents, maybe use :mod:`importer` add-on

Database
--------

1. BIND interface to add an entity to the database of a document
1. :func:`delete_entity` interface, which is the same as `UNBIND` and `DESTROY` entity
