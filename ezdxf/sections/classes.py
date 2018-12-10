# Created: 13.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterator, Iterable, Union
from collections import Counter, OrderedDict

from ezdxf.lldxf.types import DXFTag
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.const import DXFStructureError
from ezdxf.modern.dxfobjects import DXFClass

if TYPE_CHECKING:  # import forward declarations
    from ezdxf.drawing import Drawing
    from ezdxf.lldxf.tagwriter import TagWriter


class ClassesSection:
    name = 'CLASSES'

    def __init__(self, entities: Iterable[DXFTag] = None, drawing: 'Drawing' = None):
        self.classes = OrderedDict()  # DXFClasses are not stored in the entities database, because CLASS has no handle
        self.drawing = drawing
        if entities is not None:
            self._build(iter(entities))

    def __iter__(self) -> Iterable[DXFClass]:
        return (cls for cls in self.classes.values())

    def _build(self, entities: Iterator[DXFTag]) -> None:
        section_head = next(entities)
        if section_head[0] != (0, 'SECTION') or section_head[1] != (2, 'CLASSES'):
            raise DXFStructureError("Critical structure error in CLASSES section.")

        for class_tags in entities:
            self.register(ExtendedTags(class_tags))

    def register(self, classes: Union[ExtendedTags, Iterable[ExtendedTags]]):
        if classes is None:
            return

        if isinstance(classes, ExtendedTags):
            classes = (classes,)
        for class_tags in classes:
            dxftype = class_tags.noclass.get_first_value(1)
            if dxftype not in self.classes:
                self.classes[dxftype] = DXFClass(class_tags, self.drawing)

    def write(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_str("  0\nSECTION\n  2\nCLASSES\n")
        for dxfclass in self.classes.values():
            tagwriter.write_tags(dxfclass.tags)
        tagwriter.write_str("  0\nENDSEC\n")

    def update_instance_counters(self) -> None:
        if self.drawing.dxfversion < 'AC1018':
            return  # instance counter not supported
        counter = Counter()
        # count all entities in the entity database
        for xtags in self.drawing.entitydb.values():
            counter[xtags.dxftype()] += 1

        for dxfclass in self.classes.values():
            dxfclass.dxf.instance_count = counter[dxfclass.dxf.name]
