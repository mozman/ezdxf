# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Iterable, Optional, cast, BinaryIO, Tuple
from io import StringIO
from ezdxf.lldxf.const import DXFStructureError
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.tagwriter import TagWriter
from ezdxf.entities import DXFGraphic, Polyline
from ezdxf.entities.factory import EntityFactory
from ezdxf.lldxf import fileindex

__all__ = ['opendxf']

SUPPORTED_DXF_TYPES = {
    'ARC', 'LINE', 'CIRCLE', 'ELLIPSE', 'POINT', 'LWPOLYLINE', 'SPLINE', '3DFACE', 'SOLID', 'TRACE',
    'POLYLINE', 'VERTEX', 'SEQEND', 'MESH', 'TEXT', 'MTEXT', 'HATCH',
}


class IterDXF:
    """ Iterator for DXF entities stored in the modelspace.

    Args:
         name: filename, has to be a seekable file.

    """

    def __init__(self, name: str):
        # raises DXFStructureError() for invalid or incomplete DXF files
        self.structure = fileindex.load(name)
        self.name = str(name)
        self.file: BinaryIO = open(name, mode='rb')
        try:
            self.index_entities = self.structure.get(2, 'ENTITIES')
        except ValueError:
            raise DXFStructureError('No ENTITIES section found.')
        if self.structure.version > 'AC1009':
            try:
                # index of (0, SECTION) before (2, OBJECTS)
                self.index_objects = self.structure.get(2, 'OBJECTS', self.index_entities) - 1
            except ValueError:
                raise DXFStructureError('No OBJECTS section found.')
        else:
            self.index_objects = None

    @property
    def encoding(self):
        return self.structure.encoding

    @property
    def dxfversion(self):
        return self.structure.version

    def export(self, name: str) -> 'IterDXFWriter':
        """
        Returns a companion object to export parts from the source DXF file into another DXF file, the new file will
        have the same HEADER, CLASSES, TABLES, BLOCKS and OBJECTS sections, which guarantees all necessary dependencies
        are present in the new file.

        Args:
            name: filename, no special requirements

        """
        doc = IterDXFWriter(name, self)
        # file location of first entity
        location = self.structure.index[self.index_entities + 1].location
        self.file.seek(0)
        data = self.file.read(location)
        doc.write_data(data)
        return doc

    def copy_objects_section(self, f: BinaryIO) -> None:
        start_index = self.index_objects
        try:
            end_index = self.structure.get(0, 'ENDSEC', start_index)
        except ValueError:
            raise DXFStructureError(f'ENDSEC of OBJECTS section not found.')

        start_location = self.structure.index[start_index].location
        end_location = self.structure.index[end_index + 1].location
        count = end_location - start_location
        self.file.seek(start_location)
        data = self.file.read(count)
        f.write(data)

    def modelspace(self) -> Iterable[DXFGraphic]:
        """

        Returns an iterator for all supported DXF entities in the modelspace. These entities are regular
        :class:`~ezdxf.entities.DXFGraphic` objects but without a valid document assigned. It is **not**
        possible to add these entities to other `ezdxf` documents.

        It is only possible to recreate the objects by factory functions base on attributes of the source entity.
        For MESH, POLYMESH and POLYFACE it is possible to use the :class:`~ezdxf.render.MeshTransformer` class to
        render (recreate) this objects as new entities in another document.

        """
        factory = EntityFactory()
        polyline: Optional[Polyline] = None
        for index_entry, text in self.entities_as_str(self.index_entities + 1):
            dxftype = index_entry.value
            if dxftype in SUPPORTED_DXF_TYPES:
                xtags = ExtendedTags.from_text(text)
                # do not process paperspace entities
                if xtags.noclass.get_first_value(67, 0) == 1:
                    continue
                entity = factory.entity(xtags)
                if dxftype == 'SEQEND':
                    if polyline is not None:
                        polyline.seqend = entity
                        yield polyline
                        polyline = None
                    # suppress all other SEQEND entities -> ATTRIB
                elif dxftype == 'VERTEX' and polyline is not None:
                    # vertices without POLYLINE are DXF structure errors, but here just ignore it.
                    polyline.vertices.append(entity)
                elif dxftype == 'POLYLINE':
                    polyline = cast(Polyline, entity)
                else:
                    # POLYLINE without SEQEND is a DXF structure error, but here just ignore it.
                    # By using this add-on be sure to get valid DXF files.
                    polyline = None
                    yield entity

    def entities_as_str(self, start: int) -> Iterable[Tuple[fileindex.IndexEntry, str]]:
        def to_str(data: bytes) -> str:
            return data.decode(self.encoding).replace('\r\n', '\n')

        index = start
        entry = self.structure.index[index]
        self.file.seek(entry.location)
        while entry.value != 'ENDSEC':
            while True:
                index += 1
                next_entry = self.structure.index[index]
                if next_entry.code == 0:
                    break
            size = next_entry.location - entry.location
            yield entry, to_str(self.file.read(size))
            entry = next_entry

    def close(self):
        """ Safe closing source DXF file. """
        self.file.close()


class IterDXFWriter:
    def __init__(self, name: str, loader: IterDXF):
        self.name = str(name)
        self.file: BinaryIO = open(name, mode='wb')
        self.text = StringIO()
        self.entity_writer = TagWriter(self.text, loader.dxfversion)
        self.loader = loader

    def write_data(self, data: bytes):
        self.file.write(data)

    def write(self, entity: DXFGraphic):
        """ Write a DXF entity from the source DXF file to the export file.

        Don't write entities from different documents than the source DXF file, dependencies and resources will not
        match, maybe it will work once, but not in a reliable way for different DXF documents.

        """
        # remove all possible dependencies
        entity.xdata = None
        entity.appdata = None
        entity.extension_dict = None
        entity.reactors = None
        # reset text stream
        self.text.seek(0)
        self.text.truncate()

        entity.export_dxf(self.entity_writer)
        if entity.dxftype() == 'POLYLINE':
            polyline = cast('Polyline', entity)
            for vertex in polyline.vertices:
                vertex.export_dxf(self.entity_writer)
            polyline.seqend.export_dxf(self.entity_writer)
        data = self.text.getvalue().encode(self.loader.encoding)
        self.file.write(data)

    def close(self):
        """
        Safe closing of exported DXF file. Copying of OBJECTS section happens only at closing the file,
        without closing the new DXF file is invalid.
        """
        self.file.write(b'  0\r\nENDSEC\r\n')  # for ENTITIES section
        if self.loader.dxfversion > 'AC1009':
            self.loader.copy_objects_section(self.file)
        self.file.write(b'  0\r\nEOF\r\n')
        self.file.close()


def opendxf(filename: str) -> IterDXF:
    """ Open DXF file for iterating, be sure to open valid DXF files, no DXF structure checks will be applied.

    Args:
        filename: DXF filename of a seekable file.

    """
    return IterDXF(filename)
