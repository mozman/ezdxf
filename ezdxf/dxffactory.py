# Purpose: dxf-factory-factory
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from typing import Union, TYPE_CHECKING
from ezdxf.legacy import DXFFactory
from ezdxf.modern import ModernDXFFactory

if TYPE_CHECKING:
    from ezdxf.drawing import Drawing

DXFFactoryType = Union[DXFFactory, ModernDXFFactory]


def dxffactory(drawing: 'Drawing') -> DXFFactoryType:
    dxfversion = drawing.dxfversion
    factory_class = DXFFactory if dxfversion <= 'AC1009' else ModernDXFFactory
    return factory_class(drawing)


