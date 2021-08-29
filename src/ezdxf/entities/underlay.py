# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Union, Tuple, Iterable, List, Optional
from ezdxf.lldxf import validator
from ezdxf.lldxf.attributes import (
    DXFAttr,
    DXFAttributes,
    DefSubclass,
    XType,
    RETURN_DEFAULT,
    group_code_mapping,
)
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2000, DXFTypeError
from ezdxf.lldxf import const
from ezdxf.lldxf.tags import Tags
from ezdxf.math import NULLVEC, Z_AXIS
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .dxfobj import DXFObject
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace, Vertex, Drawing

__all__ = [
    "PdfUnderlay",
    "DwfUnderlay",
    "DgnUnderlay",
    "PdfDefinition",
    "DgnDefinition",
    "DwfDefinition",
    "Underlay",
    "UnderlayDefinition",
]

acdb_underlay = DefSubclass(
    "AcDbUnderlayReference",
    {
        # Hard reference to underlay definition object
        "underlay_def_handle": DXFAttr(340),
        "insert": DXFAttr(10, xtype=XType.point3d, default=NULLVEC),
        # Scale x factor:
        "scale_x": DXFAttr(
            41,
            default=1,
            validator=validator.is_not_zero,
            fixer=RETURN_DEFAULT,
        ),
        # Scale y factor:
        "scale_y": DXFAttr(
            42,
            default=1,
            validator=validator.is_not_zero,
            fixer=RETURN_DEFAULT,
        ),
        # Scale z factor:
        "scale_z": DXFAttr(
            43,
            default=1,
            validator=validator.is_not_zero,
            fixer=RETURN_DEFAULT,
        ),
        # Rotation angle in degrees:
        "rotation": DXFAttr(50, default=0),
        "extrusion": DXFAttr(
            210,
            xtype=XType.point3d,
            default=Z_AXIS,
            optional=True,
            validator=validator.is_not_null_vector,
            fixer=RETURN_DEFAULT,
        ),
        # Underlay display properties:
        # 1 = Clipping is on
        # 2 = Underlay is on
        # 4 = Monochrome
        # 8 = Adjust for background
        "flags": DXFAttr(280, default=2),
        # Contrast value (20-100; default = 100)
        "contrast": DXFAttr(
            281,
            default=100,
            validator=validator.is_in_integer_range(20, 101),
            fixer=validator.fit_into_integer_range(20, 101),
        ),
        # Fade value (0-80; default = 0)
        "fade": DXFAttr(
            282,
            default=0,
            validator=validator.is_in_integer_range(0, 81),
            fixer=validator.fit_into_integer_range(0, 81),
        ),
    },
)
acdb_underlay_group_codes = group_code_mapping(acdb_underlay)


class Underlay(DXFGraphic):
    """Virtual UNDERLAY entity."""

    # DXFTYPE = 'UNDERLAY'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_underlay)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000

    def __init__(self):
        super().__init__()
        self._boundary_path: List["Vertex"] = []
        self._underlay_def: Optional["UnderlayDefinition"] = None

    def copy(self):
        raise DXFTypeError("Copying of underlay not supported.")

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.subclass_by_index(2)

            if tags:
                tags = Tags(self.load_boundary_path(tags))
                processor.fast_load_dxfattribs(
                    dxf, acdb_underlay_group_codes, subclass=tags
                )
                if len(self.boundary_path) < 2:
                    self.dxf = dxf
                    self.reset_boundary_path()
            else:
                raise const.DXFStructureError(
                    f"missing 'AcDbUnderlayReference' subclass in "
                    f"{self.DXFTYPE}(#{dxf.handle})"
                )
        return dxf

    def load_boundary_path(self, tags: "Tags") -> Iterable:
        path = []
        for tag in tags:
            if tag.code == 11:
                path.append(tag.value)
            else:
                yield tag
        self._boundary_path = path

    def post_load_hook(self, doc: "Drawing") -> None:
        super().post_load_hook(doc)
        db = doc.entitydb
        self._underlay_def = db.get(self.dxf.get("underlay_def_handle", None))

    def export_entity(self, tagwriter: "TagWriter") -> None:
        """Export entity specific data as DXF tags."""
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_underlay.name)
        self.dxf.export_dxf_attribs(
            tagwriter,
            [
                "underlay_def_handle",
                "insert",
                "scale_x",
                "scale_y",
                "scale_z",
                "rotation",
                "extrusion",
                "flags",
                "contrast",
                "fade",
            ],
        )
        self.export_boundary_path(tagwriter)

    def export_boundary_path(self, tagwriter: "TagWriter"):
        for vertex in self.boundary_path:
            tagwriter.write_vertex(11, vertex[:2])

    def set_underlay_def(self, underlay_def: "UnderlayDefinition") -> None:
        self._underlay_def = underlay_def
        self.dxf.underlay_def_handle = underlay_def.dxf.handle
        underlay_def.append_reactor_handle(self.dxf.handle)

    def get_underlay_def(self) -> Optional["UnderlayDefinition"]:
        return self._underlay_def

    @property
    def boundary_path(self):
        return self._boundary_path

    @boundary_path.setter
    def boundary_path(self, vertices: Iterable["Vertex"]) -> None:
        self.set_boundary_path(vertices)

    @property
    def clipping(self) -> bool:
        return bool(self.dxf.flags & const.UNDERLAY_CLIPPING)

    @clipping.setter
    def clipping(self, state: bool) -> None:
        self.set_flag_state(const.UNDERLAY_CLIPPING, state)

    @property
    def on(self) -> bool:
        return bool(self.dxf.flags & const.UNDERLAY_ON)

    @on.setter
    def on(self, state: bool) -> None:
        self.set_flag_state(const.UNDERLAY_ON, state)

    @property
    def monochrome(self) -> bool:
        return bool(self.dxf.flags & const.UNDERLAY_MONOCHROME)

    @monochrome.setter
    def monochrome(self, state: bool) -> None:
        self.set_flag_state(const.UNDERLAY_MONOCHROME, state)

    @property
    def adjust_for_background(self) -> bool:
        return bool(self.dxf.flags & const.UNDERLAY_ADJUST_FOR_BG)

    @adjust_for_background.setter
    def adjust_for_background(self, state: bool):
        self.set_flag_state(const.UNDERLAY_ADJUST_FOR_BG, state)

    @property
    def scaling(self) -> Tuple[float, float, float]:
        return self.dxf.scale_x, self.dxf.scale_y, self.dxf.scale_z

    @scaling.setter
    def scaling(self, scale: Union[float, Tuple]):
        if isinstance(scale, (float, int)):
            x, y, z = scale, scale, scale
        else:
            x, y, z = scale
        self.dxf.scale_x = x
        self.dxf.scale_y = y
        self.dxf.scale_z = z

    def set_boundary_path(self, vertices: Iterable["Vertex"]) -> None:
        # path coordinates as drawing coordinates but unscaled
        vertices = list(vertices)
        if len(vertices):
            self._boundary_path = vertices
            self.clipping = True
        else:
            self.reset_boundary_path()

    def reset_boundary_path(self) -> None:
        """Removes the clipping path."""
        self._boundary_path = []
        self.clipping = False

    def destroy(self) -> None:
        if not self.is_alive:
            return

        if self._underlay_def:
            self._underlay_def.discard_reactor_handle(self.dxf.handle)
        del self._boundary_path
        super().destroy()


@register_entity
class PdfUnderlay(Underlay):
    """DXF PDFUNDERLAY entity - BricsCAD export PDFREFERENCE"""

    DXFTYPE = "PDFUNDERLAY"


@register_entity
class DwfUnderlay(Underlay):
    """DXF DWFUNDERLAY entity"""

    DXFTYPE = "DWFUNDERLAY"


@register_entity
class DgnUnderlay(Underlay):
    """DXF DGNUNDERLAY entity"""

    DXFTYPE = "DGNUNDERLAY"


acdb_underlay_def = DefSubclass(
    "AcDbUnderlayDefinition",
    {
        "filename": DXFAttr(1),  # File name of underlay
        "name": DXFAttr(2),
        # underlay name - pdf=page number to display; dgn=default; dwf=????
    },
)
acdb_underlay_def_group_codes = group_code_mapping(acdb_underlay_def)


# (PDF|DWF|DGN)DEFINITION - requires entry in objects table ACAD_(PDF|DWF|DGN)DEFINITIONS,
# ACAD_(PDF|DWF|DGN)DEFINITIONS do not exist by default
class UnderlayDefinition(DXFObject):
    """Virtual UNDERLAY DEFINITION entity."""

    DXFTYPE = "UNDERLAYDEFINITION"
    DXFATTRIBS = DXFAttributes(base_class, acdb_underlay_def)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.fast_load_dxfattribs(
                dxf, acdb_underlay_def_group_codes, subclass=1
            )
        return dxf

    def export_entity(self, tagwriter: "TagWriter") -> None:
        """Export entity specific data as DXF tags."""
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_underlay_def.name)
        self.dxf.export_dxf_attribs(tagwriter, ["filename", "name"])

    @property
    def entity_name(self):
        return self.DXFTYPE[:3] + "UNDERLAY"

    def post_new_hook(self):
        self.set_reactors([self.dxf.owner])


@register_entity
class PdfDefinition(UnderlayDefinition):
    """DXF PDFDEFINITION entity  - BricsCAD export PDFREFERENCE"""

    DXFTYPE = "PDFDEFINITION"


@register_entity
class DwfDefinition(UnderlayDefinition):
    """DXF DWFDEFINITION entity"""

    DXFTYPE = "DWFDEFINITION"


@register_entity
class DgnDefinition(UnderlayDefinition):
    """DXF DGNDEFINITION entity"""

    DXFTYPE = "DGNDEFINITION"
