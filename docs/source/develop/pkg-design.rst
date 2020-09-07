**!!! UNDER CONSTRUCTION !!!**

.. _pkg-design:

Package Design for Developers
=============================

.. Overall Design:

A DXF document is divided into several sections, this sections are managed by
the :class:`~ezdxf.drawing.Drawing` object. For each section exist a
corresponding attribute in the :class:`Drawing` object:

======== ==========================
Section  Attribute
======== ==========================
HEADER   :attr:`Drawing.header`
CLASSES  :attr:`Drawing.classes`
TABLES   :attr:`Drawing.tables`
BLOCKS   :attr:`Drawing.blocks`
ENTITIES :attr:`Drawing.entities`
OBJECTS  :attr:`Drawing.objects`
======== ==========================

Resource entities (LAYER, STYLE, LTYPE, ...) are stored in tables in the
TABLES section. A table owns the table entries, the owner handle of table
entry is the handle of the table. Each table has a shortcut in the
:class:`Drawing` object:

============ ==========================
Table        Attribute
============ ==========================
APPID        :attr:`Drawing.appids`
BLOCK_RECORD :attr:`Drawing.block_records`
DIMSTYLE     :attr:`Drawing.dimstyles`
LAYER        :attr:`Drawing.layers`
LTYPE        :attr:`Drawing.linetypes`
STYLE        :attr:`Drawing.styles`
UCS          :attr:`Drawing.ucs`
VIEW         :attr:`Drawing.views`
VPORT        :attr:`Drawing.viewports`
============ ==========================

Graphical entities are stored in layouts:
:class:`~ezdxf.layouts.Modelspace`, :class:`~ezdxf.layouts.Paperspace` layouts
and :class:`~ezdxf.layouts.BlockLayout`.
The core management object of this layouts is the BLOCK_RECORD entity
(:class:`~ezdxf.entities.BlockRecord`),
the BLOCK_RECORD is the real owner of the entities,
the owner handle of the entities is the handle of the BLOCK_RECORD and the
BLOCK_RECORD also owns and manages the entity space of the layout which
contains all entities of the layout.

For more information about layouts
see also: :ref:`Layout Management Structures`

For more information about blocks
see also: :ref:`Block Management Structures`

Non-graphical entities (objects) are stored in the OBJECTS section.
Every object has a parent object in the OBJECTS section, most likely a
DICTIONARY object, and is stored in the entity space of the OBJECTS section.

For more information about the OBJECTS section
see also: :ref:`objects_section_internals`

All table entries, DXF entities and DXF objects are stored in the entities
database accessible as :attr:`Drawing.entitydb`. The entity database is a simple
key, value storage, key is the entity handle, value is the DXF object.

For more information about the DXF data model
see also: :ref:`Data Model`

Terminology
+++++++++++

States
------

DXF entities and objects can have different states:

UNBOUND
    Entity is not stored in the :class:`Drawing` entity database and
    DXF attribute :attr:`handle` is ``None`` and
    attribute :attr:`doc` can be ``None``

BOUND
    Entity is stored in the :class:`Drawing` entity database,
    attribute :attr:`doc` has a reference to :class:`Drawing` and
    DXF attribute :attr:`handle` is not ``None``

UNLINKED
    Entity is not linked to a layout/owner,
    DXF attribute :attr:`owner` is ``None``

LINKED
    Entity is linked to a layout/owner,
    DXF attribute :attr:`owner` is not ``None``

Virtual Entity
    State: UNBOUND & UNLINKED

Unlinked Entity
    State: BOUND & UNLINKED

Bound Entity
    State: BOUND & LINKED

Actions
-------

NEW
    Create a new DXF document

LOAD
    Load a DXF document from an external source

CREATE
    Create DXF structures from NEW or LOAD data

DESTROY
    Delete DXF structures

BIND
    Bind an entity to a :class:`Drawing`, set entity state to BOUND &
    UNLINKED and check or create required resources

UNBIND
    unbind ...

LINK
    Link an entity to an owner/layout.
    This makes an entity to a real DXF entity, which will be exported
    at the saving process. Any DXF entity can only be linked to **one** parent
    entity like DICTIONARY or BLOCK_RECORD.

UNLINK
    unlink ...


Loading a DXF Document
++++++++++++++++++++++

Loading a DXF document from an external source, creates a new
:class:`Drawing` object. This loading process has two stages:

First Loading Stage
-------------------

- LOAD content from external source as :class:`SectionDict`:
  :func:`loader.load_dxf_structure`
- LOAD tag structures as :class:`DXFEntity` objects:
  :func:`loader.load_dxf_entities`
- BIND entities: :func:`loader.load_and_bind_dxf_content`;
  Special handling of the BIND process, because the :class:`Drawing` is not full
  initialized, a complete validation is not possible at this stage.

Second Loading Stage
--------------------

Parse :class:`SectionDict`:

- CREATE sections: HEADER, CLASSES, TABLES, BLOCKS and OBJECTS
- CREATE layouts: Blocks, Layouts
- LINK entities to a owner/layout

The ENTITIES section is a relict from older DXF versions and has to be exported
including the modelspace and active paperspace entities, but all entities
reside in a BLOCK definition, even modelspace and paperspace layouts are only
BLOCK definitions and ezdxf has no explicit ENTITIES section.

Source Code: as developer start your journey at :meth:`ezdxf.document.Drawing.read`,
which has no public documentation, because package-user should use
:func:`ezdxf.read` and :func:`ezdxf.readfile`.

New DXF Document
++++++++++++++++

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

Factory functions
+++++++++++++++++

- :func:`new`, create a new virtual DXF object/entity
- :func:`load`, load (create) virtual DXF object/entity from DXF tags
- :func:`bind`, bind an entity to a document, create required
  resources if necessary (e.g. ImageDefReactor, SEQEND) and raise exceptions for
  non-existing resources.

  - Bind entity loaded from an external source to a document, all referenced
    resources must exist, but try to repair as many flaws as possible because
    errors were created by another application and are not the responsibility
    of the package-user.

  - Bind an entity from another DXF document, all invalid resources will be
    removed silently or created (e.g. SEQEND). This is a simple import from
    another document without resource import, for a more advanced import
    including resources exist the :mod:`importer` add-on.

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

DXF Entities
------------

- NEW constructor to create an entity from scratch
- LOAD constructor to create an entity loaded from an external source
- DESTROY interface to kill an entity, set entity state to `dead`, which
  means :attr:`entity.is_alive` returns False. All entity iterators like
  :class:`EntitySpace`, :class:`EntityQuery`,  and :class:`EntityDB` must
  filter (ignore) `dead` entities.
  Calling :func:`DXFEntity.destroy()` is a regular way to delete entities.
- LINK an entity to a layout by :meth:`BlockRecord.link`, which set the `owner`
  handle to BLOCK_RECORD handle (= layout key) and add the entity to the entity
  space of the BLOCK_RECORD and set/clear the paperspace flag.

DXF Objects
-----------

- NEW, LOAD, DESTROY see DXF entities
- LINK: Linking an DXF object means adding the entity to a parent object in the
  OBJECTS section, most likely a DICTIONARY object, and adding the object to the
  entity space of the OBJECTS section, the root-dict is the only entity in the
  OBJECTS section which has an invalid owner handle "0". Any other object with
  an invalid or destroyed owner is an orphaned entity.
  The audit process destroys and removes orphaned objects.
- Extension dictionaries (ACAD_XDICTIONARY) are DICTIONARY objects
  located in the OBJECTS sections and can reference/own other entities of the
  OBJECTS section.
- The root-dictionary is the only entity in the OBJECTS section which has an
  invalid owner handle "0". Any other object with an invalid or destroyed owner
  is an orphaned entity.

Layouts
-------

- LINK interface to link an entity to a layout
- UNLINK interface to remove an entity from a layout

Database
--------

- BIND interface to add an entity to the database of a document
- :func:`delete_entity` interface, same as UNBIND and DESTROY an entity
