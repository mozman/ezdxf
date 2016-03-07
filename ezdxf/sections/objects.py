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
        return self.create_new_dxf_entity('DICTIONARY', dxfattribs={'owner': 0})

    def setup_objects_management_tables(self, rootdict):
        def setup_plot_style_name_table():
            placeholder = self.create_new_dxf_entity('ACDBPLACEHOLDER', dxfattribs={})
            placeholder_handle = placeholder.dxf.handle

            plot_style_name_dict = self.create_new_dxf_entity('ACDBDICTIONARYWDFLT', dxfattribs={
                'owner': rootdict.dxf.handle,
                'default': placeholder_handle
            })
            plot_style_name_dict_handle = plot_style_name_dict.dxf.handle
            plot_style_name_dict['Normal'] = placeholder_handle
            placeholder.dxf.owner = plot_style_name_dict_handle  # link to owner

            rootdict['ACAD_PLOTSTYLENAME'] = plot_style_name_dict_handle

        for name in _OBJECT_TABLE_NAMES:
            if name in rootdict:
                continue  # just create not existing tables
            if name == "ACAD_PLOTSTYLENAME":
                setup_plot_style_name_table()
            else:
                rootdict.add_new_dict(name)

    def groups(self):
        try:
            group_table_handle = self.rootdict()['ACAD_GROUP']
        except KeyError:
            raise DXFInternalEzdxfError("Table ACAD_GROUP should already exist in root dict.")
        else:
            group_table = self.dxffactory.wrap_handle(group_table_handle)
        return DXFGroupTable(group_table)

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
