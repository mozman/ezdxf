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
    DXF document. The new entity is a virtual or unbounded entity, which gets 
    a real entity by binding that entity to a DXF document.
1. Binding a virtual entity to a DXF document is different for the 2 scenarios:
    - `LOAD`: all required resources should be loaded at the time of binding the
        entity, als handles are set and can be validated
    - `CREATE`: some resources should be present (e.g. linetypes, text-styles)
        and some required resources should be created (e.g. ImageDef Reactor)

The new setup process should consider also the following loading scenarios:

- DWG loader add-on
- iterdxf add-on

## Terminology

*Unbounded Entity:*

- not bound to a document: `doc` attribute is `None`
- not stored in an entity database: DXF attribute `handle` is `None`
- not assigned to a layout/owner: DXF attribute `owner` is `None`


## LOAD

The loading process has two stages:

### First Stage

Load content from file/stream and store them in a DXF structure database. 

### Second Stage

Parse DXF structure database:

- create base structures: Header, Tables, Classes, Objects
- create layouts: Blocks, Layouts
- bind entities to document
- assign entities to layouts


## CREATE

A new entity is always a unbounded and virtual entity after instantiation:

- DXF owner is `None`
- DXF handle is `None`
- doc attribute is `None`

### Document Binding

Binding the entity to document does:

- set doc attribute: add entity to document
- set DXF handle: add entity to the document entity database 
- DXF owner is still `None`, does not reside in any layout

Without an assigned layout the entity is still a virtual entity, but bounded 
to a document, this means it is possible to check or create required 
resources.

### Assign Layout/Owner

This makes an entity to a real DXF entity, which will be exported at the saving 
process.

- set owner handle to parent object

DXF Entities:

- set owner handle to the BLOCK_RECORD handle of the assigned layout
- set paperspace flag
