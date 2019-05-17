# Created: 17.05.2019
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
"""
Translate DXF entities into Python code.

"""
from typing import TYPE_CHECKING, Iterable, List
import logging

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFGraphic

logger = logging.getLogger('ezdxf')

__all__ = ['entities_to_code']


def entities_to_code(entities: Iterable['DXFGraphic'], layout: str = 'layout') -> 'EntityTranslator':
    translator = EntityTranslator(layout=layout)
    for entity in entities:
        dxftype = entity.dxftype()
        try:
            entity_translator = getattr(translator, dxftype.lower())
        except AttributeError:
            logger.debug('entities_to_code() does not support {} entity'.format(dxftype))
        else:
            entity_translator(entity)
    return translator


HANDLE_ATTRIBUTES = {'handle', 'owner', 'paperspace', 'material_handle', 'visualstyle_handle', 'plotstyle_handle'}


def purge_handles(attribs: dict) -> dict:
    return {k: v for k, v in attribs.items() if k not in HANDLE_ATTRIBUTES}


class EntityTranslator:
    def __init__(self, layout: str = 'layout'):
        self.layout = layout
        self.source = []  # type: List[str]

    def line(self, entity: 'DXFGraphic') -> None:
        dxfattribs = purge_handles(entity.dxfattribs())
        start = dxfattribs.pop('start', '(0, 0, 0)')
        end = dxfattribs.pop('end', '(0, 0, 0)')

        code = '{}.add_line(start={}, end={}, dxfattribs={})'.format(
            self.layout,
            start,
            end,
            str(dxfattribs)
        )
        self.source.append(code)

    def point(self, entity: 'DXFGraphic') -> None:
        dxfattribs = purge_handles(entity.dxfattribs())
        location = dxfattribs.pop('location', '(0, 0, 0)')

        code = '{}.add_point(location={}, dxfattribs={})'.format(
            self.layout,
            location,
            str(dxfattribs)
        )
        self.source.append(code)

    def circle(self, entity: 'DXFGraphic') -> None:
        dxfattribs = purge_handles(entity.dxfattribs())
        center = dxfattribs.pop('center', '(0, 0, 0)')
        radius = dxfattribs.pop('radius', 1)

        code = '{}.add_circle(center={}, radius={}, dxfattribs={})'.format(
            self.layout,
            center,
            radius,
            str(dxfattribs)
        )
        self.source.append(code)

    def arc(self, entity: 'DXFGraphic') -> None:
        dxfattribs = purge_handles(entity.dxfattribs())
        center = dxfattribs.pop('center', '(0, 0, 0)')
        radius = dxfattribs.pop('radius', 1)
        start_angle = dxfattribs.pop('start_angle', 0)
        end_angle = dxfattribs.pop('end_angle', 360)

        code = '{}.add_arc(center={}, radius={}, start_angle={}, end_angle={}, dxfattribs={})'.format(
            self.layout,
            center,
            radius,
            start_angle,
            end_angle,
            str(dxfattribs)
        )
        self.source.append(code)

    def text(self, entity: 'DXFGraphic') -> None:
        dxfattribs = purge_handles(entity.dxfattribs())
        text = dxfattribs.pop('text', '')

        code = "{}.add_text(text='{}', dxfattribs={})".format(
            self.layout,
            text,
            str(dxfattribs)
        )
        self.source.append(code)

    def tostring(self, indent=0) -> str:
        lead_str = ' ' * indent
        return ''.join(lead_str + line for line in self.source)

    def __str__(self) -> str:
        return self.tostring()
