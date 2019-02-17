# Created: 17.02.2019
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Union, Iterable, cast
import logging
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from ezdxf.lldxf.types import DXFTag
from ezdxf.lldxf.tags import Tags
from ezdxf.entities.dxfentity import base_class, SubclassProcessor, DXFEntity
from ezdxf.entities.layer import acdb_symbol_table_record
from ezdxf.tools.complex_ltype import lin_compiler

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter
    from ezdxf.entities.dxfentity import DXFNamespace
    from ezdxf.drawing2 import Drawing

__all__ = ['Linetype']

acdb_linetype = DefSubclass('AcDbLinetypeTableRecord', {
    'name': DXFAttr(2),
    'description': DXFAttr(3, default=''),
    'flags': DXFAttr(70, default=0),
    # 'length': DXFAttr(40),
    # 'items': DXFAttr(73),
})


class Linetype(DXFEntity):
    """ DXF LTYPE entity """
    DXFTYPE = 'LTYPE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_symbol_table_record, acdb_linetype)

    def __init__(self, doc: 'Drawing' = None):
        """ Default constructor """
        super().__init__(doc)
        self._pattern_tags = None

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        processor.load_dxfattribs_into_namespace(dxf, acdb_linetype)
        # store whole subclass
        self._pattern_tags = processor.find_subclass(acdb_linetype.name)[2:]  # remove subclass marker
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_symbol_table_record.name)
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_linetype.name)
        tagwriter.write_tags(self._pattern_tags)

    def _setup_pattern(self, pattern: Union[Iterable[float], str], length: float) -> None:
        complex_line_type = True if isinstance(pattern, str) else False
        if complex_line_type:  # a .lin like line type definition string
            self._setup_complex_pattern(pattern, length)
        else:
            # pattern: [2.0, 1.25, -0.25, 0.25, -0.25] - 1. element is total pattern length
            # pattern elements: >0 line, <0 gap, =0 point
            tags = Tags([
                DXFTag(2, self.dxf.name),
                DXFTag(70, self.dxf.flags),
                DXFTag(3, self.dxf.description),
                DXFTag(72, 65),  # letter 'A'
                DXFTag(73, len(pattern) - 1),
                DXFTag(40, float(pattern[0])),
            ])
            for element in pattern[1:]:
                tags.append(DXFTag(49, float(element)))
                tags.append(DXFTag(74, 0))
            self._pattern_tags = tags

    def _setup_complex_pattern(self, pattern: str, length: float) -> None:
        tokens = lin_compiler(pattern)
        tags = Tags([
            DXFTag(2, self.dxf.name),
            DXFTag(70, self.dxf.flags),
            DXFTag(3, self.dxf.description),
            DXFTag(72, 65),  # letter 'A'
        ])

        tags2 = [DXFTag(73, 0), DXFTag(40, length)]  # temp length of 0
        count = 0
        for token in tokens:
            if isinstance(token, DXFTag):
                if tags2[-1].code == 49:  # useless 74 only after 49 :))
                    tags2.append(DXFTag(74, 0))
                tags2.append(token)
                count += 1
            else:  # TEXT or SHAPE
                tags2.extend(cast('ComplexLineTypePart', token).complex_ltype_tags(self.doc))
        tags2.append(DXFTag(74, 0))  # useless 74 at the end :))
        tags2[0] = DXFTag(73, count)
        tags.extend(tags2)
        self._pattern_tags = tags
