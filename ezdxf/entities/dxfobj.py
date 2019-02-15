# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
#
# DXFObject - non graphical entities stored in OBJECTS section
from typing import TYPE_CHECKING, Optional, Tuple, List
from .dxfentity import DXFEntity

if TYPE_CHECKING:
    from ezdxf.eztypes import Auditor

__all__ = ['DXFObject']


class DXFObject(DXFEntity):
    def audit(self, auditor: 'Auditor') -> None:
        auditor.check_pointer_target_exists(self, zero_pointer_valid=False)
