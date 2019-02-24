Changes Log for ezdxf v0.10
===========================

Entity System
-------------

Complete rewrite of the entity system by keeping the high level interface unchanged, changes for users should be 
minimal, but there are some greater changes that could impact users too. 

Entities are no more stored as tag lists, instead as proper Python objects like the wrapper classes in previous ezdxf 
versions, by overhauling the complete system I decided to use a unified entity system for __ALL__ DXF versions. 

Advantage is a faster and __easier__ internal processing, and you can save as any DXF version you want by the cost
of loosing data and attributes if you choose to save in an older DXF version,  because _ezdxf_ is still not a DXF 
converter or CAD application, but I have in mind to do simple conversions like LWPOLINE to POLYLINE, but surly not 
MTEXT or HATCH. Otherwise saving an older DXF versions as a newer DXF version should work properly e.g. open a 
DXF R12 and save it as DXF R2018.

Creating new drawings by `exdxf.new()` is about 6x faster than before, because no templates from file system are needed 
anymore, new drawings are build from scratch in memory.

Disadvantage, I have to interpret all group codes of supported entities and Autodesk do not document __all__ group 
codes in the official DXF reference, this unknown group codes will be lost by saving a modified DXF drawing, 
unsupported and unknown entities are still stored an preserved as dumb tag lists (unsupported is my term for documented 
entities just stored for preservation). I try to log unknown tags, but I don't have the time and will to research the 
functionality of these unknown tags.

SOME DATA MAYBE LOST BY MODIFYING EXISTING DXF FILES.

Simple Transformation Interface
-------------------------------

Added a simple transformation interface for graphical entities, but don't expect too much, I only implement
features which could be done easily and ACIS entities will never be supported.

- `transform(direction)`: move entity in `direction` 
- `scale(factor)`: scale entity uniform about `factor`
- `scale_xyz(sx, sy, sz)`: scale entity none uniform about `sx` in x-axis, `sy` ...
- `rotate(angle, ucs)`: rotated entity `angle` degrees about the x-axis of the given `ucs`
- `transform(matrix)`: apply transformation `matrix` to entity
- `to_wcs(ucs)`: transform entity coordinates from ucs into WCS, required OCS transformation for 2D entities included.

Not every entity will support all transformations and will raise `DXFUnsupportedFeature` for unsupported features or 
use argument`ignore=True` to silently skip entity, if transformation is not supported. 

And _ezdxf_ is still not a CAD application.

Changes in Detail
-----------------

- unified entity system for all DXF versions
- save as any DXF version you want, independent of the source DXF version, maybe data loss if saving as older DXF 
  version than source DXF version (no converter)
- `templates` no more needed and removed from package but preserved in repository
- renamed central data object in entities from `DXFEntity.drawing` to `DXFEntity.doc`, this should not impact users
  because they have to save the `Drawing` object in an own variable, else it would be removed by th GC.
- DXFEntity: get_xdata() keyword `xdata_tag` renamed to `tags`
- DXFEntity: set_xdata() keyword `xdata_tag` renamed to `tags`
- DXFEntity: `remove_reactor_handle()` renamed to `discard_reactor_handle()`
- LAYER: renamed DXF atributes:
    - removed `line_weight` as synonym for `lineweight`
    - `plot_style_name` renamed to `plotstyle_handle` 
    - `material` renamed to `material_handle` 
- VIEWPORT: same treatment for all DXF versions
- POLYLINE: `Polyline.vertices()` is now an attribute `Polyline.vertices`, implemented as regular Python list.
- INSERT: `Insert.attribs()` is now an attribute `Insert.attribs`, implemented as regular Python list.
- Options:
    - removed `template_dir`, no more needed
    - new `log_unprocessed_tags` to log unprocessed (unknown) DXF tags 
- restructured package, module and tests file organization