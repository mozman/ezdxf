# Purpose: entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .classes import ClassesSection
from ..lldxf.const import DXFStructureError, DXFInternalEzdxfError
from ..modern.groups import DXFGroupTable


class ObjectsSection(ClassesSection):
    name = 'objects'

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
        """Create a root dictionary. Has to be the first object in the objects section.
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
        group_table = self.rootdict.get_required_dict('ACAD_GROUP')
        return DXFGroupTable(group_table)

    def add_dictionary(self, owner='0'):
        return self.create_new_dxf_entity('DICTIONARY', dxfattribs={'owner': owner})

    def add_dictionary_with_default(self, owner='0', default="0"):
        return self.create_new_dxf_entity('ACDBDICTIONARYWDFLT', dxfattribs={
            'owner': owner,
            'default': default,
        })

    def add_image_def(self, filename, size_in_pixel, key=None):
        image_dict = self.rootdict.get_required_dict('ACAD_IMAGE_DICT')

        # auto-generated image key
        if key is None:
            key = self.dxffactory.next_image_key(lambda k: k not in image_dict)

        image_def = self.create_new_dxf_entity('IMAGEDEF', dxfattribs={
            'owner': image_dict.dxf.handle,
            'filename': filename,
            'image_size': size_in_pixel,
        })
        image_dict[key] = image_def.dxf.handle
        return image_def

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
