# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFGraphic

CONTINUOUS_PATTERN = (1.0,)


class EntityContext:
    def resolve_color(self, entity: 'DXFGraphic'):
        raise NotImplementedError

    def resolve_linetype(self, entity: 'DXFGraphic'):
        raise NotImplementedError

    def resolve_lineweight(self, entity: 'DXFGraphic'):
        raise NotImplementedError


class Properties:
    """ An implementation agnostic representation of
    entity properties like color and linetype.
    """

    def __init__(self):
        self.color: str = '#ffffff'  # format #RRGGBB or #RRGGBBAA
        # color names should be resolved into a actual color value

        # Store linetype name for backends which don't have the ability to use user-defined linetypes,
        # but have some predefined linetypes, maybe matching most common AutoCAD linetypes is possible
        self.linetype_name: str = 'CONTINUOUS'  # default linetype

        # Linetypes: Complex DXF linetypes are not supported:
        # 1. Don't know if there are any backends which can use linetypes including text or shapes
        # 2. No decoder for SHX files available, which are the source for shapes in linetypes
        # 3. SHX files are copyrighted - including in ezdxf not possible
        #
        # Simplified DXF linetype definition:
        # all line elements >= 0.0, 0.0 = point
        # all gap elements > 0.0
        # Usage as alternating line - gap sequence: line-gap-line-gap .... (line could be a point 0.0)
        # line-line or gap-gap - makes no sense
        # Examples:
        # DXF: ("DASHED", "Dashed __ __ __ __ __ __ __ __ __ __ __ __ __ _", [0.6, 0.5, -0.1])
        # first entry 0.6 is the total pattern length = sum(linetype_pattern)
        # linetype_pattern: [0.5, 0.1] = line-gap
        # DXF: ("DASHDOTX2", "Dash dot (2x) ____  .  ____  .  ____  .  ____", [2.4, 2.0, -0.2, 0.0, -0.2])
        # linetype_pattern: [2.0, 0.2, 0.0, 0.2] = line-gap-point-gap
        # Stored as tuple, so pattern could be used as key for caching.
        # SVG dash-pattern does not support points, so a minimal line length has to be used, which alters
        # the overall line appearance a little bit - but linetype mapping will never be perfect.
        self.linetype_pattern: Tuple[float, ...] = CONTINUOUS_PATTERN
        self.linetype_scale: float = 1.0
        self.lineweight: float = 0.13  # line weight in mm
        self.layer: str = '0'

    @classmethod
    def resolve(cls, entity: 'DXFGraphic', ctx: EntityContext) -> 'Properties':
        p = cls()
        p.color = ctx.resolve_color(entity)
        p.linetype_name, p.linetype_pattern = ctx.resolve_linetype(entity)
        p.lineweight = ctx.resolve_lineweight(entity)
        p.linetype_scale = entity.dxf.ltscale
        p.layer = entity.dxf.layer
        return p

    def __eq__(self, other: 'Properties'):
        if not isinstance(other, Properties):
            raise TypeError()

        if self.color != other.color:
            return False
        if self.linetype_name != other.linetype_name:
            return False
        if self.layer != other.layer:
            return False
        if self.linetype_scale != other.linetype_scale:
            return False
        if self.linetype_pattern != other.linetype_pattern:
            return False
        return True

    def __str__(self):
        return f'({self.color}, {self.linetype_name}, {self.lineweight}, {self.layer})'
