# Purpose: default chunk
# Created: 12.03.2011
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Sequence, Iterable

if TYPE_CHECKING:
    from ezdxf.drawing import Drawing
    from ezdxf.dxffactory import DXFFactoryType
    from ezdxf.lldxf.tagwriter import TagWriter
    from ezdxf.lldxf.tags import Tags, DXFTag


class UnsupportedSection:
    def __init__(self, entities: Sequence['Tags'], drawing: 'Drawing'):
        self.entities = entities
        self._drawing = drawing

    @property
    def dxffactory(self) -> 'DXFFactoryType':
        return self._drawing.dxffactory

    @property
    def name(self) -> str:
        return self.entities[0][1].value

    def write(self, tagwriter: 'TagWriter') -> None:
        for entity in self.entities:
            tagwriter.write_tags(entity)
        tagwriter.write_str('  0\nENDSEC\n')

    def __iter__(self) -> Iterable['Tags']:
        for entity in self.entities:
            yield entity

    def tags(self) -> Iterable['DXFTag']:
        for entity in self.entities:
            for tag in entity:
                yield tag
