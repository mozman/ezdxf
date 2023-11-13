## Copying Undocumented DXF Entities
	- Copying is the basic requirement for importing entities by the `xref` module.
	- What are the requirements to support copying of undocumented entities?
		- Pointer tags can be identified by their tag type
			- Targets of hard pointers have to be registered for copying
			- Soft pointers have to be mapped to copied entities
		- `CLASS` entries in the `CLASSES` section have to be copied
		- The handling of pointer tags in the `XDATA` section of entities could be a template.