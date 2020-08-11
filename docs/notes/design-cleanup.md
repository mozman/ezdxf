Setup Process
=============

The idea is to create a new setup design:

1. There are two basic scenarios:
    - Load structures from file: `LOAD`
    - Create new structures by ezdxf: `CREATE`
1. Binding a virtual entity to a DXF document is different for the 2 scenarios:
    - `LOAD`: all required resources should be loaded at the time of binding the
      entity, als handles are set and can be validated
    - `CREATE`: some resources should be present (e.g. linetypes, text-styles)
      and some required resources should be created (e.g. ImageDefReactor, 
      SEQEND)

The new setup process should also consider the following loading scenarios:

- `dwg` loader add-on
- `iterdxf` add-on

Which means the `factory` module should provide the necessary functions to 
create/load entities for these add-ons.

## Terminology

### Virtual Entity

- `UNBOUND`: not stored in the entity database of a document: 
   DXF attribute `handle` is `None`
- `UNLINKED`: not linked to a layout/owner: 
  DXF attribute `owner` is `None`
- `doc` can be `None`

### Unlinked Entity

- `BOUND`: stored in an entity database, which means bound to a document:
  DXF attribute `handle` is not `None` and `doc` has a reference to the 
  DXF document
- `UNLINKED`: not linked to a layout/owner: 
  DXF attribute `owner` is `None`

## DXFEntity Design

CHANGE: remove dependency to the DXF document from DXF entities:

- remove `dxffactory` attribute 
- remove `entitydb` attribute

I also tried to remove the `doc` attribute of `DXFEntity`, but this was not a 
great success, this just added additional `doc` arguments to many methods, and
in the worst case changed also top level interfaces (INSERT) to be unusable
by the current design, so I reverted everything. 

But nonetheless could reduce at least some dependencies.
 
## LOAD

The loading process has two stages:

### First Stage

- `LOAD` content from file/stream into a DXF structure database: 
  `loader.load_dxf_structure()`
- Convert tag structures into DXFEntity objects: `loader.load_dxf_entities()`
- `BIND` entities to an EntityDB: `fill_database()`

Because of the missing DXF document structures, a complete validation is not 
possible at this stage, only validation at DXF-Tag level is already done.

### Second Stage

Parse DXF structure database:

- Create sections: HEADER, CLASSES, TABLES, BLOCKS and OBJECTS
- Create layouts: Blocks, Layouts
    - `LINK` entities to a layout

The ENTITIES section is a relict from older DXF versions and has to be exported 
including the modelspace and active paperspace entities, but all entities 
reside in a BLOCK definition, even modelspace and paperspace layouts are only 
BLOCK definitions and ezdxf has no explicit ENTITIES section.

## CREATE

A new entity is always a virtual entity after instantiation:

- DXF owner is `None`
- DXF handle is `None`
- `doc` attribute is maybe `None`

## BIND

Binding the entity to a document means:

- `BOUND`: entity is stored in the document entity database, `handle`is set
  and `doc` attribute is set
- Check or create required resources
- `UNLINKED`: `owner` is still `None`

## LINK

This makes an entity to a real DXF entity, which will be exported 
at the saving process. Any DXF entity can only be linked to **one** parent
entity like DICTIONARY or BLOCK_RECORD.

DXF Objects:

- `LINK` to OBJECTS section by adding entity to a parent entity in the OBJECTS 
  section, most likely a DICTIONARY object and store entity in the entity 
  space of the OBJECTS section, the root-dict is the only entity in the objects 
  section with an invalid owner handle "0".
- Extension dictionaries of graphical- or table entities can also own entities 
  in the OBJECTS section.  

DXF Entities:

- `LINK` entity to a layout by `BlockRecord.link(entity)`, which set the `owner`
  handle to BLOCK_RECORD handle (= layout key) and store entity in entity space 
  of the BLOCK_RECORD
- set paperspace flag

# Factory module

Removed `EntityFactory()`, this was a relict from the older ezdxf design until 
v0.9, where each DXF version had its own factory class.

## Factory functions

- `new(dxftype, dxfattribs)`, create a new virtual DXF object/entity
- `load(tags)`, load (create) virtual DXF object/entity from DXF tags
- `bind(entity, doc)`, bind an entity to a document, create required 
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
     including resources exist the `importer` add-on.
     
  Create an `Auditor()` and repair the entity, if unrecoverable errors exist:
  log the problem and kill the entity. Log applied fixes.
  This requires an fully initialized and valid DXF document.
- Bootstrap problem for binding loaded table entries and objects in the OBJECTS 
  section! Can't use `Auditor()` to repair this objects, because the DXF 
  document is not fully initialized.
- `is_bound(entity, doc)` returns True if `entity` is bound to document `doc`
- `cls(dxftype)`, returns the class
- `register_entity()`, registration decorator  
- `replace_entity()`, registration decorator

## Class Interfaces

### Entities

1. `CREATE` interface as class method
1. `LOAD` interface as class method
1. `DESTROY` interface to kill an entity, set entity `STATE` to "dead", which 
   means `entity.is_alive` returns False. All entity iterators like 
   `EntitySpace`, `EntityQuery`,  and `EntityDB` must filter (ignore) "dead" 
   entities. Calling `DXFEntity.destroy()` is the normal way to delete entities.
1. `UNBIND` interface to remove an entity from a document and set state 
   to a virtual entity, which should also `UNLINK` the entity, because an 
   layout can not store a virtual entity.

```Python
from ezdxf.entities.dxfentity import DXFNamespace

class DXFEntity:
    def __init__(self):
        self.dxf = DXFNamespace()

    @classmethod
    def new(cls, dxfattribs):
        """ CREATE interface """

    @classmethod
    def load(cls, tags):
        """ LOAD interface """

    @property
    def is_alive(self):
        """ STATE interface """
        return hasattr(self, "dxf")

    @property
    def is_virtual(self):
        """ STATE interface """
        return self.dxf.handle is None

    @property
    def is_bound(self):
        """ STATE interface """
        return self.dxf.handle is not None

    @property
    def is_linked(self):
        """ STATE interface """
        return self.dxf.owner is not None

    def unbind(self):
        """ UNBIND interface """

    def destroy(self):
        """ DESTROY interface """

```

### Layouts

1. `LINK` interface to assign a layout to an entity 
1. `UNLINK` interface to remove a layout assignment from an entity
1. Layouts have back-link `doc` to the DXF document
1. Support for a virtual layout, which can store virtual entities
1. It is not possible to move or copy layouts between documents, 
   maybe use `importer` add-on

```Python
from ezdxf.entities import factory
from ezdxf import audit

class Layout:
    doc: 'Drawing' = None  # back-link to DXF document

    def add_entity(self, entity):
        """ LINK interface """

    def unlink(self, entity):
        """ UNLINK interface """

    def add_foreign_entity(self, entity):
        """ LINK foreign entity """
        auditor = audit.audit(entity, self.doc)
        if not auditor.has_errors:
            factory.bind(entity, self.doc)
            self.add_entity(entity)
    
    def refresh(self):
        """ Remove dead entities. """

```

### Database

1. `BIND` interface to add an entity to the database of a document
1. remove/deprecate `delete_entity()` interface, which is the same as `UNBIND` 
   and `DESTROY` entity

```Python
class EntityDB:
    def add(self, entity):
        """ BIND interface """

    def delete_entity(self, entity):
        """ deprecated """
        entity.destroy()  # replacement

    def refresh(self):
        """ Remove dead entities. """

```