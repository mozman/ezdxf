tags:: ideas

- [[Unsorted Notes]]
- ## Copying Undocumented DXF Entities
  id:: 6568c568-6aed-4de2-83f0-7807a04d230b
	- Copying is the basic requirement for importing entities by the `xref` module.
	- What are the requirements to support copying of undocumented entities?
		- Pointer tags can be identified by their tag type
			- Targets of hard pointers have to be registered for copying
			- Soft pointers have to be mapped to copied entities
		- `CLASS` entries in the `CLASSES` section have to be copied
		- The handling of pointer tags in the `XDATA` section of entities could be a template.
- see also: [[Copying unsupported Entities]]