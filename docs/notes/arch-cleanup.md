New Setup Process
=================

The actual setup process of DXF structures for new documents or for loading 
DXF files is not well designed, because of the lack of understanding of this 
structures and dependencies between all the DXF types in the beginning of 
the development and the DXF reference is also not very helpful for this topic.

The idea is to create a new setup design:

1. There are two basic scenarios:
    - Load structures from file: `LOAD`
    - Create new structures by ezdxf: `CREATE`
1. The default constructor for entities do not get a reference to the actual 
    DXF document. The new entity is a virtual entity.
1. Binding a virtual entity to a DXF document is different for the 2 scenarios:
    - `LOAD`: all required resources should be loaded at the time of binding the
      entity, als handles are set and can be validated
    - `CREATE`: some resources should be present (e.g. linetypes, text-styles)
      and some required resources should be created (e.g. ImageDef Reactor, 
      SEQEND)

The new setup process should also consider the following loading scenarios:

- DWG loader add-on
- iterdxf add-on

Which means the `factory` module should provide the necessary functions to 
create/load entities for these add-ons.

## Terminology

### Virtual Entity

- not bound to a document: `doc` attribute is `None`
- not stored in an entity database: DXF attribute `handle` is `None`
- not assigned to a layout/owner: DXF attribute `owner` is `None`

### Unlinked Entity

- bound to a document
- stored in an entity database
- not assigned to a layout/owner: DXF attribute `owner` is `None`

```
    Virtual Entity == Unlinked Entity
    Unlinked Entity != Virtual Entity
```

## LOAD

The loading process has two stages:

### First Stage

Load content from file/stream and store them in a DXF structure database. 

### Second Stage

Parse DXF structure database:

- Create sections: HEADER, CLASSES, TABLES, BLOCKS and OBJECTS, the ENTITIES 
  section is a relict from older DXF versions and has to be exported including 
  the modelspace and active paperspace entities, but all entities reside in a 
  BLOCK definition, even modelspace and paperspace layouts are only BLOCK 
  definitions and ezdxf has no explicit ENTITIES section.
- Create layouts: Blocks, Layouts
    - Bind entities to the document: `factory.bind_loaded()`
    - Assign entities to a layout: `Layout.add_entity()`


## CREATE

A new entity is always a unbounded and virtual entity after instantiation:

- DXF owner is `None`
- DXF handle is `None`
- doc attribute is `None`

## BIND

Binding the entity to document does:

- set doc attribute: add entity to document
- set DXF handle: add entity to the document entity database 
- DXF owner is still `None`, does not reside in any layout

Without an assigned layout the entity is an unlinked entity, but bound 
to a document, this means it is possible to check or create required 
resources.

## LINK

This makes an entity to a real DXF entity, which will be exported 
at the saving process.

DXF Objects:

- set owner handle to parent object

DXF Entities:

- set owner handle to the BLOCK_RECORD handle of the assigned layout
- set paperspace flag

# Factory module

Decouple `EntityFactory()` from a specific document, this is a relict from the 
older ezdxf design until v0.9, where each DXF version had its own factory class.
In fact the `EntityFactory()` object is obsolete, `next_underlay_key()` should 
be moved to ..., `next_image_key()` is not used. The property `dxffactory` 
should be removed from all objects.

## Factory functions

- `new_entity(dxftype, dxfattribs)`, create a new virtual DXF object/entity
- `load_entity(tags)`, load (create) virtual DXF object/entity from DXF tags
- `bind_loaded(entity, doc)`, bind entity loaded from file to a document, 
  all referenced resources must exist.
- `bind_new(entity, doc)`, bind an entity created by ezdxf, create required 
  resources if necessary (e.g. ImageDefReactor, SEQEND)
- `bind_foreign(entity, doc)`, bind an entity from another document, all invalid 
  resources will be removed silently or created (e.g. SEQEND).
- `cls(dxftype)`, returns the class
- `register_entity()`, registration decorator  
- `replace_entity()`, registration decorator  