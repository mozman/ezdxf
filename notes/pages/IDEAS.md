- This page contains ideas for possible new features in future versions of `ezdxf`.
-
- # Add-ons
	- ## `drawing` add-on improvements
		- LATER Support for `Layout.dxf.plot_layout_options` in export mode of class `RenderContext`
			- plot with plot-styles
				- disable loading of the ctb-table in `set_current_layout()`
			- plot entity lineweights
				- if disabled which linewidth should be used instead?
			- scale lineweights
				- scale by what?
			- plot transparencies
				- hide paperspace entities (`DXFGraphic.dxf.paperspace` attribute is `True`)
				- VIEWPORT borders are not plotted at all by the `drawing` add-on
		- LATER clipping path support for block references
		- LATER improve linetype rendering of wide patterns, see [#906](https://github.com/mozman/ezdxf/issue/906)
		-
	- ## DWG loader add-on
		- #maybe a DWG loader for simple documents
			- useful for scenarios where the [[ODA File Converter]] is not available
			- can not replace the [[ODA File Converter]] application, but maybe good enough for simple documents
			- Cython will be required for the low level stuff, no pure Python implementation.
		-
- # Render Tools
	- #unlikely tool to create proxy graphic
	- #unlikely `ACAD_TABLE` tool to render content as DXF primitives to create the content of the anonymous block `*T...`
	- #unlikely factory methods to create `ACAD_TABLE` entities
- # DXF Entities
	- LATER `GEODATA` version 1 support, see mpolygon examples and DXF reference R2009
	- #unlikely `FIELD`, used by `ACAD_TABLE` and `MTEXT`
	- LATER explode `HATCH` pattern into `LINE` entities, points are represented by zero-length `LINE` entities, because the `POINT` entity has a special meaning.
	- LATER `HATCH` - shift hatch pattern origin
		- examples/entities/hatch_pattern_modify_origin.py
		- see discussion [#769](https://github.com/mozman/ezdxf/discussions/769)
	- #maybe extend ACIS support
		- `transform()` method support, each ACIS entity has a transformation matrix which can be modified
			- but this is expensive
			- the ACIS data has to be parsed
			- the transformation matrix modified
			- ACIS data recompiled
			- this is expensive and therfore the transformation feature has to be enabled manually for each DXF document by `doc.enable_acis_transfromation()`
	- LATER clipping path support for block references
	  id:: 65508de8-19be-495f-b83c-94600d9556bc
		- see XCLIP command
		- discussion [#760](https://github.com/mozman/ezdxf/discussions/760)
	- LATER add support for multi-line `ATTRIB` entities in `Insert.add_auto_attribs()`
	- #unlikely `ACAD_TABLE` entity load and export support beyond `AcadTableBlockContent`
	- #unlikely `ACAD_TABLE` tool to manage content at table and cell basis
	- LATER ACIS `copy()` method support
		- ACIS data does not reference any DXF resources and copying is not expensive, all copies share the same immutable ACIS data.
		- This feature allows loading ACIS entities from external references by the `xref` module.
	- #maybe Adding a `transform_matrix` attribute to entities which do not have transformation support (yet) like ACIS entities which enables to add support for the `transform()` method.
		- A new method `apply_transform_martix()` has to be called to apply the `transform_matrix` to the entity itself before export or it should raise a `NotImplementedError` exception.
		- This could be implemented for
			- ACIS entities inherited from base class `BODY`
			- `ACAD_PROXY_ENTITY`
			- `ACAD_TABLE`
			- `OLE2FRAME`
			- all unknown entities stored as `DXFTagStorage`
	-
- # Selection Module
	- LATER A module to select entities based on their spatial location and shape like in CAD applications, but using the bounding box of the entities instead their real geometry for simplicity.
	- Selection methods
		- rectangle selection
			- entity bbox inside a rectangular window
		- rectangle crossing
			- entity bbox inside or crossing a rectangular window
		- circle selection
			- entity bbox inside a circular window
		- circle crossing
			- entity bbox inside or crossing a circular window
		- polygon selection
			- entity bbox inside a polygonal window
		- polygon crossing
			- entity bbox inside or crossing a polygonal window
		- fence selection
			- entity bboxes crossing an arbitrary polyline
		- cluster selection
			- entity bboxes located near together (k_means, dbscan)
		- chain selection
			- linked (overlapping) bounding boxes starting at a given point or entity (RTree)
	- The selection geometry should be an object
		- Rectangle
		- Circle
		- Polygon
		- Fence
	- Returns an `EntityQuery` container as result, which already has `Set` operations to combine multiple selections
		- union of selections
		- subtract selected entities from a previous selection
		- intersection of selection
		-
	- The selection methods should support a bounding box cache as an optional parameter to improve the performance for multiple selections for the same base entities.
	- Usage:
	  
	  ```python
	  from ezdxf import select
	  from ezdxf import bbox
	  
	  ...
	  
	  entities = doc.modelspace()
	  
	  # optional bounding box cache for faster processing of multiple queries:
	  bbox_cache = bbox.Cache()
	  
	  rect = select.Rectangle(x0=0, y0=0, x1=10, y1=10)
	  circle = select.Circle(x=30, y=30, radius=10)
	  
	  # union:
	  selection0 = select.inside(entities, rect, cache=bbox_cache)
	  selection1 = select.crossing(entities, circle, cache=bbox_cache)
	  result = selection0 | selection1
	  
	  # subtraction:
	  selection = select.inside(entities, rect, cache=bbox_cache)
	  ignore = select.crossing(selection, circle, cache=bbox_cache)
	  result = selection - ignore
	  ```
	- #unlikely Extended entity geometry for selection
		- `ezdxf` uses the `disassemble` module for the bounding box calculation, which deconstructs DXF entities into path and/or mesh primitives.
		- This data could be used to select entities not only by their bounding box, but also by their vertices for mesh primitives and by their control points or flattened vertices for path entities.
		- `EntityGeometry` enum
			- `BBOX`
			- `CONTROL_POINTS`
			- `VERTICES`
		- This feature would require a different caching strategy, because the bounding box cache does not contain the disassembled primitives and reusing an existing bounding box cache is not possible.
		- Issues
			- How to handle 2D/3D selections?
			- 2D selections always in top-view mode?
			- Using special box- and sphere selections for 3D selection?
			-
- # Boundary Path Constructor
	- LATER A module to create boundary paths for `HATCH` and `MPOLYGON` entities.
	- The input data are DXF entities e.g. the result of a selection or an entity query, the module functions and classes help to detect closed path in the entity collection and returns one or more `BoundaryPaths` instances.
	- Although `HATCH` and `MPOLYGON` can contain multiple separated areas in a single entity this module should create a boundary path for each separated area.
	- All entities have to be located in the xy-plane and in a later version maybe in the same spatial plan defined by the extrusion vector and elevation.
	- When the entities are located in the xy-plane the extrusion vector of `CIRCLE`, `ARC` and `ELLIPSE` can be inverted.
	- Simple closed paths
		- `CIRCLE`
		- full 360° `ARC`
		- full 360° `ELLIPSE`
		- closed `LWPOLYLINE` or 2d `POLYLINE`
		- closed `SPLINE`
		- `SOLID`, `TRACE`, `3DFACE`
	- #maybe subtract `TEXT`, `ATTRIB` and `MTEXT` as text box paths
	- Complex connected paths are build from multiple entities, input entities can be
		- `LINE`
		- open `ARC`
		- open `ELLIPSE`
		- open `LWPOLYLINE` or 2d `POLYLINE`
		- open `SPLINE`
	- The path detection
		- try to connect path elements by their closest end points
		- by ambiguity the differnt possible paths are tracked recursively and the shortest 
		  or longest path will be taken.
		- A gap tolerance is given by the user to connect end points that are not coincident and the algorithm adds connection lines between these gaps.
		-
- # DXF Document
	- LATER copy DXF document by serializing and reloading the document in memory or by file-system, this is not efficient but safe.
	-
- # Increase Minimal Required Python Version
	- In general `numpy` defines the minimal required Python version.
	-
	- Python 3.9 in late 2023, after release of Python 3.12
		- https://docs.python.org/3/whatsnew/3.9.html
		- type hinting generics in standard collections
			- `dict[tuple[int, str], list[str]]` can be used in regular code outside of annotations, import of `List`, `Dict` or `Tuple` is not required anymore
		-
	- Python 3.10 in late 2024, after release of Python 3.13
		- https://docs.python.org/3/whatsnew/3.10.html
		- structural pattern matching?
		- typing: union operator `|`, outside of annotations (type aliases)
		- dataclasses: `__slots__`
		- `itertools.pairwise()` replaces `ezdxf.tools.take2()`
		-
	- Python 3.11 in late 2025, after release of Python 3.14
		- https://docs.python.org/3/whatsnew/3.11.html
		- exception groups?
		- `typing.Self`
		-
	- Apply minimal Python version update to
		- README.md
		- setup.py
		- toplevel index.rst
		- introduction.rst
		- setup.rst