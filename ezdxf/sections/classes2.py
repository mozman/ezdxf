# Created: 13.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterator, Iterable, Union, cast, List
from collections import Counter, OrderedDict

from ezdxf.lldxf.const import DXFStructureError, DXF2004
from ezdxf.entities.dxfclass import DXFClass
from ezdxf.entities.dxfentity import DXFEntity

if TYPE_CHECKING:  # import forward declarations
    from ezdxf.entities.dxfentity import DXFEntity, DXFTagStorage
    from ezdxf.drawing2 import Drawing
    from ezdxf.eztypes import TagWriter

# name: cpp_class_name, app_name, flags, was_a_proxy, is_an_entity
CLASS_DEFINITIONS = {
    'ACDBDICTIONARYWDFLT': ['AcDbDictionaryWithDefault', 'ObjectDBX Classes', 0, 0, 0],
    'DICTIONARYVAR': ['AcDbDictionaryVar', 'ObjectDBX Classes', 0, 0, 0],
    'TABLESTYLE': ['AcDbTableStyle', 'ObjectDBX Classes', 4095, 0, 0],
    'MATERIAL': ['AcDbMaterial', 'ObjectDBX Classes', 1153, 0, 0],
    'VISUALSTYLE': ['AcDbVisualStyle', 'ObjectDBX Classes', 4095, 0, 0],
    'SCALE': ['AcDbScale', 'ObjectDBX Classes', 1153, 0, 0],
    'MLEADERSTYLE': ['AcDbMLeaderStyle', 'ACDB_MLEADERSTYLE_CLASS', 4095, 0, 0],
    'MLEADER': ['AcDbMLeader', 'ACDB_MLEADER_CLASS', 1025, 0, 1],
    'CELLSTYLEMAP': ['AcDbCellStyleMap', 'ObjectDBX Classes', 1152, 0, 0],
    'EXACXREFPANELOBJECT': ['ExAcXREFPanelObject', 'EXAC_ESW', 1025, 0, 0],
    'NPOCOLLECTION': ['AcDbImpNonPersistentObjectsCollection', 'ObjectDBX Classes', 1153, 0, 0],
    'LAYER_INDEX': ['AcDbLayerIndex', 'ObjectDBX Classes', 0, 0, 0],
    'SPATIAL_INDEX': ['AcDbSpatialIndex', 'ObjectDBX Classes', 0, 0, 0],
    'IDBUFFER': ['AcDbIdBuffer', 'ObjectDBX Classes', 0, 0, 0],
    'DIMASSOC': ['AcDbDimAssoc',
                 '"AcDbDimAssoc|Product Desc:     AcDim ARX App For Dimension|Company:          Autodesk, Inc.|WEB Address:      www.autodesk.com"',
                 0, 0, 0],
    'ACDBSECTIONVIEWSTYLE': ['AcDbSectionViewStyle', 'ObjectDBX Classes', 1025, 0, 0],
    'ACDBDETAILVIEWSTYLE': ['AcDbDetailViewStyle', 'ObjectDBX Classes', 1025, 0, 0],
    'IMAGEDEF': ['AcDbRasterImageDef', 'ISM', 0, 0, 0],
    'RASTERVARIABLES': ['AcDbRasterVariables', 'ISM', 0, 0, 0],
    'IMAGEDEF_REACTOR': ['AcDbRasterImageDefReactor', 'ISM', 1, 0, 0],
    'IMAGE': ['AcDbRasterImage', 'ISM', 2175, 0, 1],
    'PDFDEFINITION': ['AcDbPdfDefinition', 'ObjectDBX Classes', 1153, 0, 0],
    'PDFUNDERLAY': ['AcDbPdfReference', 'ObjectDBX Classes', 4095, 0, 1],
    'DWFDEFINITION': ['AcDbDwfDefinition', 'ObjectDBX Classes', 1153, 0, 0],
    'DWFUNDERLAY': ['AcDbDwfReference', 'ObjectDBX Classes', 1153, 0, 1],
    'DGNDEFINITION': ['AcDbDgnDefinition', 'ObjectDBX Classes', 1153, 0, 0],
    'DGNUNDERLAY': ['AcDbDgnReference', 'ObjectDBX Classes', 1153, 0, 1],
}


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

    def add_class(self, name: str):
        if (name in self.classes) or (name not in CLASS_DEFINITIONS):
            return
        cls_data = CLASS_DEFINITIONS[name]
        cls = DXFClass(self.doc)
        cpp, app, flags, proxy, entity = cls_data
        cls.update_dxf_attribs({
            'cpp_class_name': cpp,
            'app_name': app,
            'flags': flags,
            'was_a_proxy': proxy,
            'is_an_entity': entity,
        })
        self.classes[name] = cls

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
