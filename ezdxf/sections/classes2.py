# Created: 13.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterator, Iterable, Union, cast
from collections import Counter, OrderedDict

from ezdxf.lldxf.const import DXFStructureError, DXF2004
from ezdxf.entities.dxfclass import DXFClass
from ezdxf.entities.dxfentity import DXFEntity

if TYPE_CHECKING:  # import forward declarations
    from ezdxf.entities.dxfentity import DXFEntity, DXFTagStorage
    from ezdxf.drawing2 import Drawing
    from ezdxf.eztypes import TagWriter


class ClassesSection:
    name = 'CLASSES'

    def __init__(self, doc: 'Drawing' = None, entities: Iterable[DXFEntity] = None):
        self.classes = OrderedDict()  # DXFClasses are not stored in the entities database, because CLASS has no handle
        self.doc = doc
        if entities is not None:
            self.load(iter(entities))

    def __iter__(self) -> Iterable[DXFClass]:
        return (cls for cls in self.classes.values())

    def load(self, entities: Iterator[DXFEntity]) -> None:
        section_head = next(entities)  # type: DXFTagStorage
        if section_head.dxftype() != 'SECTION' or section_head.base_class[1] != (2, self.name.upper()):
            raise DXFStructureError("Critical structure error in CLASSES section.")

        for cls_entity in entities:
            self.register(cast(DXFClass, cls_entity))

    def register(self, classes: Union[DXFClass, Iterable[DXFClass]] = None) -> None:
        if classes is None:
            return

        if isinstance(classes, DXFClass):
            classes = (classes,)

        for dxfclass in classes:
            dxftype = dxfclass.dxf.name
            if dxftype not in self.classes:
                self.classes[dxftype] = dxfclass

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_str("  0\nSECTION\n  2\nCLASSES\n")
        for dxfclass in self.classes.values():
            dxfclass.export_dxf(tagwriter)
        tagwriter.write_str("  0\nENDSEC\n")

    def update_instance_counters(self) -> None:
        if self.doc.dxfversion < DXF2004:
            return  # instance counter not supported
        counter = Counter()
        # count all entities in the entity database
        for entity in self.doc.entitydb.values():
            counter[entity.dxftype()] += 1

        for dxfclass in self.classes.values():
            dxfclass.dxf.instance_count = counter[dxfclass.dxf.name]
