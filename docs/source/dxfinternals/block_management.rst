.. _Block Management Structures:

Block Management Structures
===========================

Tag (330, ...): (Autodesk says: Soft-pointer ID/handle to owner BLOCK_RECORD object)

I call this tag 'owner' tag. Every graphic entity is associated to a specific layout,
a layout can be the model space, a paper space or a block definition.

The owner tag is the link from the DXF entity to the associated layout.

The owner tag is the handle of the block record entry of the layout.

A layout consists of a BLOCK definition (e. g. *Model_Space) in the BLOCKS section
and a LAYOUT entry in the OBJECTS section.

Every BLOCK definition requires also a BLOCK_RECORD entry in the BLOCK_RECORDS
table in the TABLES section.

The handle (5, ...) of the BLOCK_RECORD is the owner tag for all entities in that layout.
I call this value also layout key in the context of layouts and owner tag in the context of DXF entities.
