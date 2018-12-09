# Purpose: dxf-factory-factory
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from ezdxf.legacy import DXFFactory
from ezdxf.modern import ModernDXFFactory


def dxffactory(drawing):
    dxfversion = drawing.dxfversion
    factory_class = DXFFactory if dxfversion <= 'AC1009' else ModernDXFFactory
    return factory_class(drawing)


