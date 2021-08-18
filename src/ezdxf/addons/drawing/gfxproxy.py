#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

from typing import Iterable, TYPE_CHECKING
from ezdxf.entities import DXFGraphic, DXFEntity
from ezdxf.lldxf import const

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter


class DXFGraphicProxy(DXFGraphic):
    """DO NOT USE THIS WRAPPER AS REAL DXF ENTITY OUTSIDE THE DRAWING ADD-ON!"""

    def __init__(self, entity: DXFEntity):
        super().__init__()
        self.entity = entity
        self.dxf = self._setup_dxf_namespace(entity)

    def _setup_dxf_namespace(self, entity):
        # copy DXF namespace - modifications do not effect the wrapped entity
        dxf = entity.dxf.copy(self)
        # setup mandatory DXF attributes without default values like layer:
        for k, v in self.DEFAULT_ATTRIBS.items():
            if not dxf.hasattr(k):
                dxf.set(k, v)
        return dxf

    def dxftype(self) -> str:
        return self.entity.dxftype()

    def __virtual_entities__(self) -> Iterable[DXFGraphic]:
        """Implements the SupportsVirtualEntities protocol."""
        if hasattr(self.entity, "virtual_entities"):
            return self.entity.virtual_entities()  # type: ignore
        return []

    def virtual_entities(self) -> Iterable[DXFGraphic]:
        return self.__virtual_entities__()

    def copy(self) -> "DXFGraphicProxy":
        raise const.DXFTypeError(f"Cloning of DXFGraphicProxy() not supported.")

    def preprocess_export(self, tagwriter: "TagWriter") -> bool:
        # prevent dxf export
        return False
