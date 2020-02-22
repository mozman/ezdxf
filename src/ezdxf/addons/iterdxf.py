# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Iterable, Optional, cast
from ezdxf.lldxf.validator import is_dxf_file
from ezdxf.lldxf.const import DXFStructureError
from ezdxf.lldxf.types import DXFTag
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.tagger import low_level_tagger, tag_compiler
from ezdxf.lldxf.tagwriter import TagWriter
from ezdxf.filemanagement import dxf_file_info
from ezdxf.entities import DXFGraphic, Polyline
from ezdxf.entities.factory import EntityFactory

VALID_TYPES = {
    'ARC', 'LINE', 'CIRCLE', 'ELLIPSE', 'POINT', 'LWPOLYLINE', 'SPLINE', '3DFACE', 'SOLID', 'TRACE',
    'POLYLINE', 'VERTEX', 'SEQEND', 'MESH', 'TEXT', 'MTEXT', 'HATCH',
}


class IterDXF:
    def __init__(self, name: str):
        self.name = str(name)
        if not is_dxf_file(name):
            raise DXFStructureError(f'File {name} is not a DXF file')
        info = dxf_file_info(name)
        self.encoding = info.encoding
        self.dxfversion = info.version
        self.file = open(name, mode='rt', encoding=self.encoding)
        self._fp_entities_section = None
        self._fp_objects_section = None

    def export(self, name: str) -> 'IterDXFWriter':
        doc = IterDXFWriter(name, self)
        for tag in self._iter_until_entities_section():
            doc.write_tag(tag)
        return doc

    def modelspace(self) -> Iterable[DXFGraphic]:
        if self._fp_entities_section is None:
            self._fp_entities_section = self._seek_to_section('ENTITIES')
        self.file.seek(self._fp_entities_section)
        tags = []
        factory = EntityFactory()
        polyline: Optional[Polyline] = None
        for tag in tag_compiler(low_level_tagger(self.file)):
            if tag.code == 0:  # start new entity
                if len(tags):
                    xtags = ExtendedTags(tags)
                    dxftype = xtags.dxftype()
                    if dxftype in VALID_TYPES:
                        entity = factory.entity(xtags)
                        if dxftype == 'SEQEND' and polyline is not None:
                            polyline.seqend = entity
                            yield polyline
                            polyline = None
                        elif dxftype == 'VERTEX' and polyline is not None:
                            polyline.vertices.append(entity)
                        elif dxftype == 'POLYLINE':
                            polyline = entity
                        else:
                            yield factory.entity(xtags)
                if tag == (0, 'ENDSEC'):
                    break
                tags = [tag]
            else:
                tags.append(tag)

    def _iter_until_entities_section(self) -> DXFTag:
        prev_tag = (0, None)
        self.file.seek(0)
        for tag in low_level_tagger(self.file):
            if tag != (2, 'ENTITIES'):
                yield tag
            else:
                if prev_tag == (0, 'SECTION'):
                    yield tag  # write (0, 'ENTITIES')
                    break
            prev_tag = tag

        self._fp_entities_section = self.file.tell()

    def _seek_to_section(self, name: str) -> int:
        prev_tag = (0, None)
        self.file.seek(0)
        find = DXFTag(2, name)
        section = DXFTag(0, 'SECTION')
        for tag in low_level_tagger(self.file):
            if tag == find and prev_tag == section:
                break
            prev_tag = tag
        return self.file.tell()

    def _iter_objects_section(self):
        if self._fp_objects_section is None:
            self._fp_objects_section = self._seek_to_section('OBJECTS')
        self.file.seek(self._fp_objects_section)
        for tag in low_level_tagger(self.file):
            if tag != DXFTag(0, 'ENDSEC'):
                yield tag
            else:
                yield tag
                break

    def close(self):
        self.file.close()


class IterDXFWriter:
    def __init__(self, name: str, loader: IterDXF):
        self.name = str(name)
        self.file = open(name, mode='wt', encoding=loader.encoding)
        self.entity_writer = TagWriter(self.file, loader.dxfversion)
        self.loader = loader

    def write_tag(self, tag: DXFTag):
        self.file.write(tag.dxfstr())

    def write_entity(self, entity: DXFGraphic):
        # remove all possible dependencies
        entity.xdata = None
        entity.appdata = None
        entity.extension_dict = None
        entity.embedded_objects = None
        entity.reactors = None
        entity.export_dxf(self.entity_writer)
        if entity.dxftype() == 'POLYLINE':
            polyline = cast('Polyline', entity)
            for vertex in polyline.vertices:
                vertex.export_dxf(self.entity_writer)
            polyline.seqend.export_dxf(self.entity_writer)

    def close(self):
        self.file.write('  0\nENDSEC\n')
        if self.loader.dxfversion > 'AC1009':
            self.file.write('  0\nSECTION\n  2\nOBJECTS\n')
            for tag in self.loader._iter_objects_section():
                self.write_tag(tag)
        self.file.write('  0\nEOF\n')
        self.file.close()


def opendxf(filename: str) -> IterDXF:
    return IterDXF(filename)
