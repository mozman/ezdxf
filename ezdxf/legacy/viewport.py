# Purpose: DXF 12 viewport entity
# Created: 10.10.2015
# Copyright (C) 2015, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from contextlib import contextmanager

from .graphics import make_attribs, GraphicEntity
from ..lldxf.extendedtags import ExtendedTags
from ..lldxf.attributes import DXFAttr
from ..lldxf.tags import DXFTag, Tags
from ..lldxf.const import DXFStructureError

_VPORT_TPL = """  0
VIEWPORT
  5
0
 10
0.0
 20
0.0
 30
0.0
 40
1.0
 41
1.0
 68
 1
1001
ACAD
1000
MVIEW
1002
{
1070
16
1010
0.0
1020
0.0
1030
0.0
1010
0.0
1020
0.0
1030
0.0
1040
0.0
1040
1.0
1040
0.0
1040
0.0
1040
50.0
1040
0.0
1040
0.0
1070
  0
1070
100
1070
  1
1070
  3
1070
  0
1070
  0
1070
  0
1070
  0
1040
0.0
1040
0.0
1040
0.0
1040
0.1
1040
0.1
1040
0.1
1040
0.1
1070
 0
1002
{
1002
}
1002
}
"""


class Viewport(GraphicEntity):
    TEMPLATE = ExtendedTags.from_text(_VPORT_TPL)
    DXFATTRIBS = make_attribs({
        'center': DXFAttr(10, xtype='Point2D/3D'),  # center point of entity in paper space coordinates)
        'width': DXFAttr(40),  # width in paper space units
        'height': DXFAttr(41),  # height in paper space units
        'status': DXFAttr(68),
        'id': DXFAttr(69),
    })

    viewport_id = 2  # notes to id:
    # The id of the first viewport has to be 1, which is the definition of
    # paper space. For the following viewports it seems only important, that
    # the id is greater than 1.

    @contextmanager
    def edit_data(self):
        viewport_data = self.get_viewport_data()
        yield viewport_data
        self.set_viewport_data(viewport_data)

    def get_viewport_data(self):
        try:
            extended_dxf_data = self.tags.get_xdata('ACAD')
        except ValueError:
            DXFStructureError("Invalid viewport entity - missing data")
        else:
            return ViewportData.from_tags(extended_dxf_data)

    def set_viewport_data(self, viewport_data):
        dxftags = viewport_data.dxftags()
        pos = None
        for index, xdata in enumerate(self.tags.xdata):
            if xdata[0].value == 'ACAD' and xdata[1].value == 'MVIEW':
                pos = index
        if pos is None:
            self.tags.xdata.insert(0, dxftags)  # insert viewport data as first extended data
        else:
            self.tags.xdata[pos] = dxftags

    def get_next_viewport_id(self):
        current_id = Viewport.viewport_id
        Viewport.viewport_id += 1
        return current_id


class ViewportData(object):
    """ Helper class for Viewport().

    This class defines the extended dxf tags, which can not be treated as DXFAttr()
    like the 'ordinary' dxf tags, because:
        - tags defined as extended DXF codes
        - the group codes of this tags are not unique
        - this tags must occur in a particular order, the order of their appearing,
          defines their meaning.

    """

    def __init__(self):
        # view_target_point & view_direction_vector defines the view direction
        # only important for 3D model views
        self.view_target_point = (0., 0., 0.)
        self.view_direction_vector = (0., 0., 0.)
        self.view_twist_angle = 0.  # in radians!!!
        self.view_height = 1.  # height of model space area
        self.view_center_point = (0., 0.)  # point in model space, which is displayed in the viewport center.
        self.perspective_lens_length = 50.
        self.front_clip_plane_z_value = 0.
        self.back_clip_plane_z_value = 0.
        self.view_mode = 0
        self.circle_zoom = 100
        self.fast_zoom = 1
        self.ucs_icon = 3
        self.snap = 0
        self.grid = 0
        self.snap_style = 0
        self.snap_isopair = 0
        self.snap_angle = 0.
        self.snap_base_point = (0., 0.)
        self.snap_spacing = (0.1, 0.1)
        self.grid_spacing = (0.1, 0.1)
        self.hidden_plot = 0
        self.frozen_layers = []  # add layer names as strings

    def dxftags(self):
        tags = [
            DXFTag(1001, 'ACAD'),
            DXFTag(1000, 'MVIEW'),
            DXFTag(1002, '{', ),
            DXFTag(1070, 16),  # extended data version, always 16 for R11/12
            DXFTag(1010, self.view_target_point),
            DXFTag(1010, self.view_direction_vector),
            DXFTag(1040, self.view_twist_angle),
            DXFTag(1040, self.view_height),
            DXFTag(1040, self.view_center_point[0]),
            DXFTag(1040, self.view_center_point[1],),
            DXFTag(1040, self.perspective_lens_length),
            DXFTag(1040, self.front_clip_plane_z_value),
            DXFTag(1040, self.back_clip_plane_z_value),
            DXFTag(1070, self.view_mode),
            DXFTag(1070, self.circle_zoom),
            DXFTag(1070, self.fast_zoom),
            DXFTag(1070, self.ucs_icon),
            DXFTag(1070, self.snap),
            DXFTag(1070, self.grid),
            DXFTag(1070, self.snap_style),
            DXFTag(1070, self.snap_isopair),
            DXFTag(1040, self.snap_angle),
            DXFTag(1040, self.snap_base_point[0]),
            DXFTag(1040, self.snap_base_point[1]),
            DXFTag(1040, self.snap_spacing[0]),
            DXFTag(1040, self.snap_spacing[1]),
            DXFTag(1040, self.grid_spacing[0]),
            DXFTag(1040, self.grid_spacing[1]),
            DXFTag(1070, self.hidden_plot),
            DXFTag(1002, '{'),  # start frozen layer list
        ]
        tags.extend(DXFTag(1003, layer_name) for layer_name in self.frozen_layers)
        tags.extend([
            DXFTag(1002, '}'),  # end of frozen layer list
            DXFTag(1002, '}'),  # end of viewport data
        ])
        return Tags(tags)

    @classmethod
    def from_tags(cls, tags):
        vp_data = cls()
        try:
            vp_data.view_target_point = tags[4].value
            vp_data.view_direction_vector = tags[5].value
            vp_data.view_twist_angle = tags[6].value
            vp_data.view_height = tags[7].value
            vp_data.view_center_point = tags[8].value, tags[9].value
            vp_data.perspective_lens_length = tags[10].value
            vp_data.front_clip_plane_z_value = tags[11].value
            vp_data.back_clip_plane_z_value = tags[12].value
            vp_data.view_mode = tags[13].value
            vp_data.circle_zoom = tags[14].value
            vp_data.fast_zoom = tags[15].value
            vp_data.ucs_icon = tags[16].value
            vp_data.snap = tags[17].value
            vp_data.grid = tags[18].value
            vp_data.snap_style = tags[19].value
            vp_data.snap_isopair = tags[20].value
            vp_data.snap_angle = tags[21].value
            vp_data.snap_base_point = tags[22].value, tags[23].value
            vp_data.snap_spacing = tags[24].value, tags[25].value
            vp_data.grid_spacing = tags[26].value, tags[27].value
            vp_data.hidden_plot = tags[28].value
        except IndexError:
            raise DXFStructureError("Invalid viewport entity - missing data")
        vp_data.frozen_layers = [frozen_layer_name.value for frozen_layer_name in tags[30:-2]]
        return vp_data
