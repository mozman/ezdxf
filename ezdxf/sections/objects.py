# Purpose: entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <me@mozman.at>"

from .abstract import AbstractSection
from ..lldxf.const import DXFStructureError, DXFValueError, RASTER_UNITS, DXFKeyError
from ..modern.groups import GroupManager
from ..modern.material import MaterialManager
from ..entityspace import EntitySpace


class ObjectsSection(AbstractSection):
    name = 'OBJECTS'

    def __init__(self, entities, drawing):
        entity_space = EntitySpace(drawing.entitydb)
        super(ObjectsSection, self).__init__(entity_space, entities, drawing)

    def __iter__(self):
        for handle in self._entity_space:
            yield self.dxffactory.wrap_handle(handle)

    @property
    def roothandle(self):
        return self._entity_space[0]

    @property
    def rootdict(self):
        if len(self):
            return self.dxffactory.wrap_entity(self.entitydb[self.roothandle])
        else:
            return self.setup_rootdict()

    def setup_rootdict(self):
        """
        Create a root dictionary. Has to be the first object in the objects section.
        """
        if len(self):
            raise DXFStructureError("Can not create root dictionary in none empty objects section.")

        # root directory has no owner
        return self.add_dictionary(owner='0')

    def setup_objects_management_tables(self, rootdict):
        def setup_plot_style_name_table():
            plot_style_name_dict = self.add_dictionary_with_default(owner=rootdict.dxf.handle)
            plot_style_name_dict_handle = plot_style_name_dict.dxf.handle

            placeholder = self.add_placeholder(owner=plot_style_name_dict_handle)
            placeholder_handle = placeholder.dxf.handle

            plot_style_name_dict.dxf.default = placeholder_handle
            plot_style_name_dict['Normal'] = placeholder_handle
            rootdict['ACAD_PLOTSTYLENAME'] = plot_style_name_dict_handle

        for name in _OBJECT_TABLE_NAMES:
            if name in rootdict:
                continue  # just create not existing tables
            if name == "ACAD_PLOTSTYLENAME":
                setup_plot_style_name_table()
            else:
                rootdict.add_new_dict(name)

    def groups(self):
        return GroupManager(self.drawing)

    def materials(self):
        return MaterialManager(self.drawing)

    def add_dictionary(self, owner='0'):
        return self.create_new_dxf_entity('DICTIONARY', dxfattribs={'owner': owner})

    def add_dictionary_with_default(self, owner='0', default="0"):
        return self.create_new_dxf_entity('ACDBDICTIONARYWDFLT', dxfattribs={
            'owner': owner,
            'default': default,
        })

    def set_raster_variables(self, frame=0, quality=1, units='m'):
        units = RASTER_UNITS.get(units, 0)
        try:
            raster_vars = self.rootdict.get_entity('ACAD_IMAGE_VARS')
        except DXFKeyError:
            owner = self.rootdict.dxf.handle
            raster_vars = self.create_new_dxf_entity('RASTERVARIABLES', dxfattribs={
                'owner': owner,
                'frame': frame,
                'quality': quality,
                'units': units,
            })
            raster_vars.set_reactors([owner])
            self.rootdict['ACAD_IMAGE_VARS'] = raster_vars.dxf.handle
        else:
            raster_vars.dxf.frame = frame
            raster_vars.dxf.quality = quality
            raster_vars.dxf.units = units

    def add_image_def(self, filename, size_in_pixel, name=None):
        # removed auto-generated name
        # use absolute image paths for filename and AutoCAD loads images automatically
        if name is None:
            name = filename
        image_dict = self.rootdict.get_required_dict('ACAD_IMAGE_DICT')
        image_def = self.create_new_dxf_entity('IMAGEDEF', dxfattribs={
            'owner': image_dict.dxf.handle,
            'filename': filename,
            'image_size': size_in_pixel,
        })
        image_dict[name] = image_def.dxf.handle
        image_def.set_reactors([image_def.dxf.owner])
        return image_def

    def add_image_def_reactor(self, image_handle):
        return self.create_new_dxf_entity('IMAGEDEF_REACTOR', dxfattribs={
            'owner': image_handle,
            'image': image_handle,
        })

    def add_underlay_def(self, filename, format='pdf', name=None):
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

    def add_placeholder(self, owner='0'):
            return self.create_new_dxf_entity('ACDBPLACEHOLDER', dxfattribs={
                'owner': owner
            })

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
