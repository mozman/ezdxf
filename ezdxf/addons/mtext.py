# Purpose: The MText entity is a composite entity, consisting of basic TEXT entities.
# Created: 09.03.2010, adapted 2018 for ezdxf
# Copyright (c) 2010-2018, Manfred Moitzi
# License: MIT License
"""
MText -- MultiLine-Text-Entity, created by simple TEXT-Entities.

MTEXT was introduced in R13, so this is a replacement with multiple simple
TEXT entities. Supports valign (TOP, MIDDLE, BOTTOM), halign (LEFT, CENTER,
RIGHT), rotation for an arbitrary (!) angle and mirror.

"""
from typing import TYPE_CHECKING
import math
from .mixins import SubscriptAttributes
import ezdxf
from ezdxf.lldxf import const

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, GenericLayoutType


class MText(SubscriptAttributes):
    """
    MultiLine-Text buildup with simple Text-Entities.


    Caution: align point is always the insert point, I don't need a second
    alignpoint because horizontal alignment FIT, ALIGN, BASELINE_MIDDLE is not
    supported.

    linespacing -- linespacing in percent of height, 1.5 = 150% = 1+1/2 lines

    supported align values:
        'BOTTOM_LEFT', 'BOTTOM_CENTER', 'BOTTOM_RIGHT'
        'MIDDLE_LEFT', 'MIDDLE_CENTER', 'MIDDLE_RIGHT'
        'TOP_LEFT',    'TOP_CENTER',    'TOP_RIGHT'

    """
    MIRROR_X = const.MIRROR_X
    MIRROR_Y = const.MIRROR_Y
    TOP = const.TOP
    MIDDLE = const.MIDDLE
    BOTTOM = const.BOTTOM
    LEFT = const.LEFT
    CENTER = const.CENTER
    RIGHT = const.RIGHT
    VALID_ALIGN = frozenset([
        'BOTTOM_LEFT',
        'BOTTOM_CENTER',
        'BOTTOM_RIGHT',
        'MIDDLE_LEFT',
        'MIDDLE_CENTER',
        'MIDDLE_RIGHT',
        'TOP_LEFT',
        'TOP_CENTER',
        'TOP_RIGHT',
    ])

    def __init__(self, text: str, insert: 'Vertex', linespacing: float = 1.5, **kwargs):
        self.textlines = text.split('\n')
        self.insert = insert
        self.linespacing = linespacing
        if 'align' in kwargs:
            self.align = kwargs.get('align', 'TOP_LEFT').upper()
        else:  # support for compatibility: valign, halign
            halign = kwargs.get('halign', 0)
            valign = kwargs.get('valign', 3)
            self.align = const.TEXT_ALIGNMENT_BY_FLAGS.get((halign, valign), 'TOP_LEFT')

        if self.align not in MText.VALID_ALIGN:
            raise ezdxf.DXFValueError('Invalid align parameter: {}'.format(self.align))

        self.height = kwargs.get('height', 1.0)
        self.style = kwargs.get('style', 'STANDARD')
        self.oblique = kwargs.get('oblique', 0.0)  # in degree
        self.rotation = kwargs.get('rotation', 0.0)  # in degree
        self.xscale = kwargs.get('xscale', 1.0)
        self.mirror = kwargs.get('mirror', 0)  # renamed to text_generation_flag in ezdxf
        self.layer = kwargs.get('layer', '0')
        self.color = kwargs.get('color', const.BYLAYER)

    @property
    def lineheight(self) -> float:
        """ Absolute linespacing in drawing units. 
        """
        return self.height * self.linespacing

    def render(self, layout: 'GenericLayoutType') -> None:
        """ Create the DXF-TEXT entities. 
        """
        textlines = self.textlines
        if len(textlines) > 1:
            if self.mirror & const.MIRROR_Y:
                textlines.reverse()
            for linenum, text in enumerate(textlines):
                alignpoint = self._get_align_point(linenum)
                layout.add_text(
                    text,
                    dxfattribs=self._dxfattribs(alignpoint),
                )
        elif len(textlines) == 1:
            layout.add_text(
                textlines[0],
                dxfattribs=self._dxfattribs(self.insert),
            )

    def _get_align_point(self, linenum: int) -> 'Vertex':
        """ Calculate the align point depending on the line number. 
        """
        x = self.insert[0]
        y = self.insert[1]
        try:
            z = self.insert[2]
        except IndexError:
            z = 0.
        # rotation not respected

        if self.align.startswith('TOP'):
            y -= linenum * self.lineheight
        elif self.align.startswith('MIDDLE'):
            y0 = linenum * self.lineheight
            fullheight = (len(self.textlines) - 1) * self.lineheight
            y += (fullheight / 2) - y0
        else:  # BOTTOM
            y += (len(self.textlines) - 1 - linenum) * self.lineheight
        return self._rotate((x, y, z))  # consider rotation

    def _rotate(self, alignpoint: 'Vertex') -> 'Vertex':
        """
        Rotate alignpoint around insert point about rotation degrees.
        """
        dx = alignpoint[0] - self.insert[0]
        dy = alignpoint[1] - self.insert[1]
        beta = math.radians(self.rotation)
        x = self.insert[0] + dx * math.cos(beta) - dy * math.sin(beta)
        y = self.insert[1] + dy * math.cos(beta) + dx * math.sin(beta)
        return round(x, 6), round(y, 6), alignpoint[2]

    def _dxfattribs(self, alignpoint: 'Vertex') -> dict:
        """
        Build keyword arguments for TEXT entity creation.
        """
        halign, valign = const.TEXT_ALIGN_FLAGS.get(self.align)
        return {
            'insert': alignpoint,
            'align_point': alignpoint,
            'layer': self.layer,
            'color': self.color,
            'style': self.style,
            'height': self.height,
            'width': self.xscale,
            'text_generation_flag': self.mirror,
            'rotation': self.rotation,
            'oblique': self.oblique,
            'halign': halign,
            'valign': valign,
        }
