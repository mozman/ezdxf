#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import TYPE_CHECKING, Optional
from ezdxf.lldxf import const
from . import factory
from .dxfgfx import DXFGraphic
from .dxfentity import SubclassProcessor
from ezdxf.math import BoundingBox, Vec3

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFNamespace, TagWriter, Tags


@factory.register_entity
class OLE2Frame(DXFGraphic):
    DXFTYPE = "OLE2FRAME"
    MIN_DXF_VERSION_FOR_EXPORT = const.DXF2000

    def __init__(self):
        super().__init__()
        self.acdb_ole2frame: Optional["Tags"] = None

    def copy(self) -> "DXFGraphic":
        raise const.DXFTypeError(f"Cloning of {self.dxftype()} not supported.")

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        dxf = super().load_dxf_attribs(processor)
        if processor:
            self.acdb_ole2frame = processor.subclass_by_index(2)
        return dxf

    def export_entity(self, tagwriter: "TagWriter") -> None:
        """Export entity specific data as DXF tags. (internal API)"""
        # Base class and AcDbEntity export is done by parent class
        super().export_entity(tagwriter)
        if self.acdb_ole2frame is not None:
            tagwriter.write_tags(self.acdb_ole2frame)
        # XDATA export is done by the parent class

    def bbox(self) -> BoundingBox:
        if self.acdb_ole2frame is not None:
            v10 = self.acdb_ole2frame.get_first_value(10, None)
            v11 = self.acdb_ole2frame.get_first_value(11, None)
            if v10 is not None and v11 is not None:
                return BoundingBox([Vec3(v10), Vec3(v11)])
        return BoundingBox()

    def binary_data(self) -> bytes:
        if self.acdb_ole2frame is not None:
            return b"".join(
                value for code, value in self.acdb_ole2frame if code == 310
            )
        return b""
