# Created: 13.03.2011
# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Tuple, cast, Iterator
import logging

from ezdxf.entities.dictionary import Dictionary
from ezdxf.lldxf.const import DXFStructureError, DXFValueError, RASTER_UNITS, DXFKeyError
from ezdxf.entitydb import EntitySpace
from ezdxf.query import EntityQuery

if TYPE_CHECKING:
    from ezdxf.eztypes import GeoData
    from ezdxf.eztypes2 import Drawing, DXFEntity, EntityFactory, TagWriter, EntityDB, DXFTagStorage

logger = logging.getLogger('ezdxf')


class ObjectsSection:
    def __init__(self, doc: 'Drawing', entities: Iterable['DXFEntity'] = None):
        self.doc = doc
        self._entity_space = EntitySpace()
        if entities is not None:
            self._build(iter(entities))

    def __iter__(self) -> Iterable['DXFEntity']:
        return iter(self._entity_space)

    @property
    def dxffactory(self) -> 'EntityFactory':
        return self.doc.dxffactory

    @property
    def entitydb(self) -> 'EntityDB':
        return self.doc.entitydb

    def get_entity_space(self) -> 'EntitySpace':
        return self._entity_space

    def _build(self, entities: Iterator['DXFEntity']) -> None:
        section_head = next(entities)  # type: DXFTagStorage

        if section_head.dxftype() != 'SECTION' or section_head.base_class[1] != (2, 'OBJECTS'):
            raise DXFStructureError("Critical structure error in 'OBJECTS' section.")

        for entity in entities:
            self._entity_space.add(entity)

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_str("  0\nSECTION\n  2\nOBJECTS\n")
        self._entity_space.export_dxf(tagwriter)
        tagwriter.write_tag2(0, "ENDSEC")

    def create_new_dxf_entity(self, _type: str, dxfattribs: dict) -> 'DXFEntity':
        """
        Create new DXF entity add it to the entity database and add it to the entity space.

        """
        dxf_entity = self.dxffactory.create_db_entry(_type, dxfattribs)
        self._entity_space.add(dxf_entity)
        return dxf_entity

    def delete_entity(self, entity: 'DXFEntity') -> None:
        self._entity_space.remove(entity)
        self.entitydb.delete_entity(entity)

    # start of public interface

    def __len__(self) -> int:
        return len(self._entity_space)

    def __contains__(self, entity: 'DXFEntity') -> bool:
        return entity in self._entity_space

    def query(self, query: str = '*') -> EntityQuery:
        return EntityQuery(iter(self), query)

    def delete_all_entities(self) -> None:
        """ Delete all entities. """
        db = self.entitydb
        for entity in self._entity_space:
            db.delete_entity(entity)
        self._entity_space.clear()

    # end of public interface

    @property
    def rootdict(self) -> Dictionary:
        if len(self):
            return self._entity_space[0]  # type: Dictionary
        else:
            return self.setup_rootdict()

    def setup_rootdict(self) -> Dictionary:
        """
        Create a root dictionary. Has to be the first object in the objects section.
        """
        if len(self):
            raise DXFStructureError("Can not create root dictionary in none empty objects section.")
        logger.debug('Creating ROOT dictionary.')
        # root directory has no owner
        return self.add_dictionary(owner='0')

    def setup_objects_management_tables(self, rootdict: Dictionary) -> None:
        def setup_plot_style_name_table():
            plot_style_name_dict = self.add_dictionary_with_default(owner=rootdict.dxf.handle)
            placeholder = self.add_placeholder(owner=plot_style_name_dict.dxf.handle)
            plot_style_name_dict.set_default(placeholder)
            plot_style_name_dict['Normal'] = placeholder
            rootdict['ACAD_PLOTSTYLENAME'] = plot_style_name_dict

        for name in _OBJECT_TABLE_NAMES:
            if name in rootdict:
                continue  # just create not existing tables
            logger.info('creating {} dictionary'.format(name))
            if name == "ACAD_PLOTSTYLENAME":
                setup_plot_style_name_table()
            else:
                rootdict.add_new_dict(name)

    def add_object(self, entity: 'DXFEntity') -> None:
        self._entity_space.add(entity)

    def add_dxf_object_with_reactor(self, dxftype: str, dxfattribs: dict) -> 'DXFEntity':
        dxfobject = self.create_new_dxf_entity(dxftype, dxfattribs)
        dxfobject.set_reactors([dxfattribs['owner']])
        return dxfobject

    def add_dictionary(self, owner: str = '0', hard_owned: bool = False) -> Dictionary:
        entity = self.create_new_dxf_entity('DICTIONARY', dxfattribs={
            'owner': owner,
            'hard_owned': hard_owned,
        })
        return cast(Dictionary, entity)

    def add_dictionary_with_default(self, owner='0', default='0', hard_owned: bool = False) -> 'Dictionary':
        entity = self.create_new_dxf_entity('ACDBDICTIONARYWDFLT', dxfattribs={
            'owner': owner,
            'default': default,
            'hard_owned': hard_owned,
        })
        return cast(Dictionary, entity)

    def add_xrecord(self, owner: str = '0') -> 'DXFEntity':
        return self.create_new_dxf_entity('XRECORD', dxfattribs={'owner': owner})

    def add_placeholder(self, owner: str = '0') -> 'DXFEntity':
        return self.create_new_dxf_entity('ACDBPLACEHOLDER', dxfattribs={'owner': owner})

    def set_raster_variables(self, frame: int = 0, quality: int = 1, units: str = 'm') -> None:
        units = RASTER_UNITS.get(units, 0)
        try:
            raster_vars = self.rootdict.get_entity('ACAD_IMAGE_VARS')
        except DXFKeyError:
            raster_vars = self.add_dxf_object_with_reactor('RASTERVARIABLES', dxfattribs={
                'owner': self.rootdict.dxf.handle,
                'frame': frame,
                'quality': quality,
                'units': units,
            })
            self.rootdict['ACAD_IMAGE_VARS'] = raster_vars.dxf.handle
        else:
            raster_vars.dxf.frame = frame
            raster_vars.dxf.quality = quality
            raster_vars.dxf.units = units

    def set_wipeout_variables(self, frame: int = 0) -> None:
        try:
            wipeout_vars = self.rootdict.get_entity('ACAD_WIPEOUT_VARS')
        except DXFKeyError:
            wipeout_vars = self.add_dxf_object_with_reactor('WIPEOUTVARIABLES', dxfattribs={
                'owner': self.rootdict.dxf.handle,
                'frame': int(frame),
            })
            self.rootdict['ACAD_WIPEOUT_VARS'] = wipeout_vars.dxf.handle
        else:
            wipeout_vars.dxf.frame = int(frame)

    def add_image_def(self, filename: str, size_in_pixel: Tuple[int, int], name=None) -> 'DXFEntity':
        # removed auto-generated name
        # use absolute image paths for filename and AutoCAD loads images automatically
        if name is None:
            name = filename
        image_dict = self.rootdict.get_required_dict('ACAD_IMAGE_DICT')
        image_def = self.add_dxf_object_with_reactor('IMAGEDEF', dxfattribs={
            'owner': image_dict.dxf.handle,
            'filename': filename,
            'image_size': size_in_pixel,
        })
        image_dict[name] = image_def.dxf.handle
        return image_def

    def add_image_def_reactor(self, image_handle: str) -> 'DXFEntity':
        return self.create_new_dxf_entity('IMAGEDEF_REACTOR', dxfattribs={
            'owner': image_handle,
            'image': image_handle,
        })

    def add_underlay_def(self, filename: str, format: str = 'pdf', name: str = None) -> 'DXFEntity':
        fmt = format.upper()
        if fmt in ('PDF', 'DWF', 'DGN'):
            underlay_dict_name = 'ACAD_{}DEFINITIONS'.format(fmt)
            underlay_def_entity = "{}DEFINITION".format(fmt)
        else:
            raise DXFValueError("Unsupported file format: '{}'".format(fmt))

        if name is None:
            if fmt == 'PDF':
                name = '1'  # Display first page by default
            elif fmt == 'DGN':
                name = 'default'
            else:
                name = 'Model'  # Display model space for DWF ???

        underlay_dict = self.rootdict.get_required_dict(underlay_dict_name)
        underlay_def = self.create_new_dxf_entity(underlay_def_entity, dxfattribs={
            'owner': underlay_dict.dxf.handle,
            'filename': filename,
            'name': name,
        })

        # auto-generated underlay key
        key = self.dxffactory.next_underlay_key(lambda k: k not in underlay_dict)
        underlay_dict[key] = underlay_def.dxf.handle
        return underlay_def

    def add_geodata(self, owner: str = '0', dxfattribs: dict = None) -> 'GeoData':
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['owner'] = owner
        return cast('GeoData', self.add_dxf_object_with_reactor('GEODATA', dxfattribs))


_OBJECT_TABLE_NAMES = [
    "ACAD_COLOR",
    "ACAD_GROUP",
    "ACAD_LAYOUT",
    "ACAD_MATERIAL",
    "ACAD_MLEADERSTYLE",
    "ACAD_MLINESTYLE",
    "ACAD_PLOTSETTINGS",
    "ACAD_PLOTSTYLENAME",
    "ACAD_SCALELIST",
    "ACAD_TABLESTYLE",
    "ACAD_VISUALSTYLE",
]
