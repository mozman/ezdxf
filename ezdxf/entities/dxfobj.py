# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
#
# DXFObject - non graphical entities stored in OBJECTS section
from typing import TYPE_CHECKING
from ezdxf.lldxf.const import DXF2000
from .dxfentity import DXFEntity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes2 import Auditor

__all__ = ['DXFObject', 'AcDbPlaceholder']


class DXFObject(DXFEntity):
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000



@register_entity
class AcDbPlaceholder(DXFObject):
    DXFTYPE = 'ACDBPLACEHOLDER'

