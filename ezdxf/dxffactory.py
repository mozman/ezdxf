# Purpose: dxf-factory-factory
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
from ezdxf.legacy import LegacyDXFFactory
from ezdxf.modern import ModernDXFFactory

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFFactoryType, Drawing


def dxffactory(drawing: 'Drawing') -> 'DXFFactoryType':
    dxfversion = drawing.dxfversion
    factory_class = LegacyDXFFactory if dxfversion <= 'AC1009' else ModernDXFFactory
    return factory_class(drawing)


