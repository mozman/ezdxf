# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, List, Iterable
from ezdxf.lldxf import validator
from ezdxf.lldxf import const
from ezdxf.lldxf.attributes import (
    DXFAttr, DXFAttributes, DefSubclass, XType, RETURN_DEFAULT,
    group_code_mapping,
)
from ezdxf.lldxf.types import DXFTag, DXFVertex
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.const import (
    DXF12, SUBCLASS_MARKER, DXFStructureError, DXFValueError,
    DXFTableEntryError,
)
from ezdxf.math import Vec3, Vec2, NULLVEC, X_AXIS, Y_AXIS
from ezdxf.tools import set_flag_state
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace, Drawing

__all__ = ['Viewport']

acdb_viewport = DefSubclass('AcDbViewport', {
    # DXF reference: Center point (in WCS)
    # Correction to the DXF reference:
    # This point represents the center of the viewport in paper space units
    # (DCS), but is stored as 3D point inclusive z-axis!
    'center': DXFAttr(10, xtype=XType.point3d, default=NULLVEC),

    # Width in paper space units:
    'width': DXFAttr(40, default=1),

    # Height in paper space units:
    'height': DXFAttr(41, default=1),

    # Viewport status field:
    # -1 = On, but is fully off screen, or is one of the viewports that is not
    #      active because the $MAXACTVP count is currently being exceeded.
    #  0 = Off
    # <positive value> = On and active. The value indicates the order of
    # stacking for the viewports, where 1 is the "active viewport", 2 is the
    # next, and so on:
    'status': DXFAttr(68, default=0),

    # Special VIEWPORT id == 1, this viewport defines the area of the layout
    # which is currently shown in the layout tab by the CAD application.
    # I guess this is meant by "active viewport" and therefore it is most likely
    # that this id is always 1.
    # This "active viewport" is mandatory for a valid DXF file.
    # BricsCAD set id to -1 if the viewport is off and 'status' (group code 68)
    # is not present.
    'id': DXFAttr(69, default=2),

    # DXF reference: View center point (in DCS):
    # Correction to the DXF reference:
    # This point represents the center point in model space (WCS) stored as
    # 2D point!
    'view_center_point': DXFAttr(12, xtype=XType.point2d, default=NULLVEC),
    'snap_base_point': DXFAttr(13, xtype=XType.point2d, default=NULLVEC),
    'snap_spacing': DXFAttr(14, xtype=XType.point2d, default=Vec2(10, 10)),
    'grid_spacing': DXFAttr(15, xtype=XType.point2d, default=Vec2(10, 10)),
    # View direction vector (WCS):
    'view_direction_vector': DXFAttr(16, xtype=XType.point3d, default=NULLVEC),
    # View target point (in WCS):
    'view_target_point': DXFAttr(17, xtype=XType.point3d, default=NULLVEC),
    'perspective_lens_length': DXFAttr(42, default=50),
    'front_clip_plane_z_value': DXFAttr(43, default=0),
    'back_clip_plane_z_value': DXFAttr(44, default=0),
    # View height (in model space units):
    'view_height': DXFAttr(45, default=1),
    'snap_angle': DXFAttr(50, default=0),
    'view_twist_angle': DXFAttr(51, default=0),
    'circle_zoom': DXFAttr(72, default=100),

    # 331: Frozen layer object ID/handle (multiple entries may exist) (optional)

    # Viewport status bit-coded flags:
    # 1 (0x1) = Enables perspective mode
    # 2 (0x2) = Enables front clipping
    # 4 (0x4) = Enables back clipping
    # 8 (0x8) = Enables UCS follow
    # 16 (0x10) = Enables front clip not at eye
    # 32 (0x20) = Enables UCS icon visibility
    # 64 (0x40) = Enables UCS icon at origin
    # 128 (0x80) = Enables fast zoom
    # 256 (0x100) = Enables snap mode
    # 512 (0x200) = Enables grid mode
    # 1024 (0x400) = Enables isometric snap style
    # 2048 (0x800) = Enables hide plot mode
    # 4096 (0x1000) = kIsoPairTop. If set and kIsoPairRight is not set, then
    #   isopair top is enabled. If both kIsoPairTop and kIsoPairRight are set,
    #   then isopair left is enabled
    # 8192 (0x2000) = kIsoPairRight. If set and kIsoPairTop is not set, then
    #   isopair right is enabled
    # 16384 (0x4000) = Enables viewport zoom locking
    # 32768 (0x8000) = Currently always enabled
    # 65536 (0x10000) = Enables non-rectangular clipping
    # 131072 (0x20000) = Turns the viewport off
    # 262144 (0x40000) = Enables the display of the grid beyond the drawing
    #   limits
    # 524288 (0x80000) = Enable adaptive grid display
    # 1048576 (0x100000) = Enables subdivision of the grid below the set grid
    #   spacing when the grid display is adaptive
    # 2097152 (0x200000) = Enables grid follows workplane switching
    'flags': DXFAttr(90, default=0),

    # Clipping viewports: the following handle point to a graphical entity
    # located in the paperspace. Known supported entities:
    # LWPOLYLINE (2D POLYLINE), CIRCLE, ELLIPSE, closed SPLINE
    # Extract bounding- or clipping path: ezdxf.render.make_path()
    'clipping_boundary_handle': DXFAttr(340, default='0', optional=True),

    # Plot style sheet name assigned to this viewport
    'plot_style_name': DXFAttr(1, default=''),

    # Render mode:
    # 0 = 2D Optimized (classic 2D)
    # 1 = Wireframe
    # 2 = Hidden line
    # 3 = Flat shaded
    # 4 = Gouraud shaded
    # 5 = Flat shaded with wireframe
    # 6 = Gouraud shaded with wireframe
    'render_mode': DXFAttr(
        281, default=0,
        validator=validator.is_in_integer_range(0, 7),
        fixer=RETURN_DEFAULT,
    ),
    'ucs_per_viewport': DXFAttr(
        71, default=0,
        validator=validator.is_integer_bool,
        fixer=RETURN_DEFAULT,
    ),
    'ucs_icon': DXFAttr(74, default=0),
    'ucs_origin': DXFAttr(110, xtype=XType.point3d, default=NULLVEC),
    'ucs_x_axis': DXFAttr(
        111, xtype=XType.point3d, default=X_AXIS,
        validator=validator.is_not_null_vector,
        fixer=RETURN_DEFAULT,
    ),
    'ucs_y_axis': DXFAttr(
        112, xtype=XType.point3d, default=Y_AXIS,
        validator=validator.is_not_null_vector,
        fixer=RETURN_DEFAULT,
    ),

    # Handle of AcDbUCSTableRecord if UCS is a named UCS.
    # If not present, then UCS is unnamed:
    'ucs_handle': DXFAttr(345),

    # Handle of AcDbUCSTableRecord of base UCS if UCS is orthographic (79 code
    # is non-zero). If not present and 79 code is non-zero, then base UCS is
    # taken to be WORLD:
    'ucs_base_handle': DXFAttr(346, optional=True),

    # UCS ortho type:
    # 0 = not orthographic
    # 1 = Top
    # 2 = Bottom
    # 3 = Front
    # 4 = Back
    # 5 = Left
    # 6 = Right
    'ucs_ortho_type': DXFAttr(
        79, default=0,
        validator=validator.is_in_integer_range(0, 7),
        fixer=RETURN_DEFAULT,
    ),
    'elevation': DXFAttr(146, default=0),

    # Shade plot mode:
    # 0 = As Displayed
    # 1 = Wireframe
    # 2 = Hidden
    # 3 = Rendered
    'shade_plot_mode': DXFAttr(
        170, dxfversion='AC1018',
        validator=validator.is_in_integer_range(0, 4),
        fixer=RETURN_DEFAULT,
    ),
    # Frequency of major grid lines compared to minor grid lines
    'grid_frequency': DXFAttr(61, dxfversion='AC1021'),
    'background_handle': DXFAttr(332, dxfversion='AC1021'),
    'shade_plot_handle': DXFAttr(333, dxfversion='AC1021'),
    'visual_style_handle': DXFAttr(348, dxfversion='AC1021'),
    'default_lighting_flag': DXFAttr(292, dxfversion='AC1021', default=1,
                                     optional=True),
    # Default lighting type:
    # 0 = One distant light
    # 1 = Two distant lights
    'default_lighting_type': DXFAttr(
        282, default=0, dxfversion='AC1021',
        validator=validator.is_integer_bool,
        fixer=RETURN_DEFAULT,
    ),
    'view_brightness': DXFAttr(141, dxfversion='AC1021'),
    'view_contrast': DXFAttr(142, dxfversion='AC1021'),

    # as AutoCAD Color Index
    'ambient_light_color_1': DXFAttr(
        63, dxfversion='AC1021',
        validator=validator.is_valid_aci_color,
    ),
    # as True Color:
    'ambient_light_color_2': DXFAttr(421, dxfversion='AC1021'),

    # as True Color:
    'ambient_light_color_3': DXFAttr(431, dxfversion='AC1021'),

    'sun_handle': DXFAttr(361, dxfversion='AC1021'),
    'ref_vp_object_1': DXFAttr(335, dxfversion='AC1021'),
    # unknown meaning, don't ask mozman
    'ref_vp_object_2': DXFAttr(343, dxfversion='AC1021'),
    # unknown meaning, don't ask mozman
    'ref_vp_object_3': DXFAttr(344, dxfversion='AC1021'),
    # unknown meaning, don't ask mozman
    'ref_vp_object_4': DXFAttr(91, dxfversion='AC1021'),
    # unknown meaning, don't ask mozman
})
acdb_viewport_group_codes = group_code_mapping(acdb_viewport)
# Note:
# The ZOOM XP factor is calculated with the following formula:
# group_41 / group_45 (or pspace_height / mspace_height).

FROZEN_LAYER_GROUP_CODE = 331


@register_entity
class Viewport(DXFGraphic):
    """ DXF VIEWPORT entity """
    DXFTYPE = 'VIEWPORT'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_viewport)
    viewport_id = 2

    # Notes to viewport_id:
    # The id of the first viewport has to be 1, which is the definition of
    # paper space. For the following viewports it seems only important, that
    # the id is greater than 1.

    def get_next_viewport_id(self) -> int:
        current_id = Viewport.viewport_id
        Viewport.viewport_id += 1
        return current_id

    def __init__(self):
        super().__init__()
        self._frozen_layers: List[str] = []

    def _copy_data(self, entity: 'Viewport') -> None:
        entity._frozen_layers = self._frozen_layers

    @property
    def frozen_layers(self) -> List[str]:
        """ Set/get frozen layers as list of layer names. """
        return self._frozen_layers

    @frozen_layers.setter
    def frozen_layers(self, names: Iterable[str]):
        self._frozen_layers = list(names)

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.fast_load_dxfattribs(
                dxf, acdb_viewport_group_codes, subclass=2, log=False)
            if processor.r12:
                self.load_xdata_into_dxf_namespace()
            else:
                if len(tags):
                    tags = self.load_frozen_layer_handles(tags)
                if len(tags):
                    processor.log_unprocessed_tags(
                        tags, subclass=acdb_viewport.name)
        return dxf

    def post_load_hook(self, doc: 'Drawing'):
        super().post_load_hook(doc)
        bag: List[str] = []
        db = doc.entitydb
        for handle in self._frozen_layers:
            try:
                bag.append(db[handle].dxf.name)
            except KeyError:  # ignore non-existing layers
                pass
        self._frozen_layers = bag

    def load_frozen_layer_handles(self, tags: Tags) -> Tags:
        unprocessed_tags = Tags()
        for tag in tags:
            if tag.code == FROZEN_LAYER_GROUP_CODE:
                self._frozen_layers.append(tag.value)
            else:
                unprocessed_tags.append(tag)
        return unprocessed_tags

    def load_xdata_into_dxf_namespace(self) -> None:
        try:
            tags = [v for c, v in self.xdata.get_xlist('ACAD', 'MVIEW')]
        except DXFValueError:
            return
        tags = tags[3:-2]
        dxf = self.dxf
        flags = 0
        flags = set_flag_state(flags, const.VSF_FAST_ZOOM, bool(tags[11]))
        flags = set_flag_state(flags, const.VSF_SNAP_MODE, bool(tags[13]))
        flags = set_flag_state(flags, const.VSF_GRID_MODE, bool(tags[14]))
        flags = set_flag_state(flags, const.VSF_ISOMETRIC_SNAP_STYLE,
                               bool(tags[15]))
        flags = set_flag_state(flags, const.VSF_HIDE_PLOT_MODE, bool(tags[24]))
        try:
            dxf.view_target_point = tags[0]
            dxf.view_direction_vector = tags[1]
            dxf.view_twist_angle = tags[2]
            dxf.view_height = tags[3]
            dxf.view_center_point = tags[4], tags[5]
            dxf.perspective_lens_length = tags[6]
            dxf.front_clip_plane_z_value = tags[7]
            dxf.back_clip_plane_z_value = tags[8]
            dxf.render_mode = tags[9]  # view_mode == render_mode ?
            dxf.circle_zoom = tags[10]
            # fast zoom flag : tag[11]
            dxf.ucs_icon = tags[12]
            # snap mode flag  = tags[13]
            # grid mode flag = tags[14]
            # isometric snap style = tags[15]
            # dxf.snap_isopair = tags[16] ???
            dxf.snap_angle = tags[17]
            dxf.snap_base_point = tags[18], tags[19]
            dxf.snap_spacing = tags[20], tags[21]
            dxf.grid_spacing = tags[22], tags[23]
            # hide plot flag  = tags[24]
        except IndexError:  # internal exception
            raise DXFStructureError("Invalid viewport entity - missing data")
        dxf.flags = flags
        self._frozen_layers = tags[26:]
        self.xdata.discard('ACAD')

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        super().export_entity(tagwriter)
        if tagwriter.dxfversion == DXF12:
            self.export_acdb_viewport_r12(tagwriter)
        else:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_viewport.name)
            self.dxf.export_dxf_attribs(tagwriter, [
                'center', 'width', 'height', 'status', 'id',
                'view_center_point', 'snap_base_point', 'snap_spacing',
                'grid_spacing', 'view_direction_vector', 'view_target_point',
                'perspective_lens_length', 'front_clip_plane_z_value',
                'back_clip_plane_z_value', 'view_height', 'snap_angle',
                'view_twist_angle', 'circle_zoom',
            ])
            if len(self.frozen_layers):
                layers = self.doc.layers
                for layer_name in self.frozen_layers:
                    try:
                        layer = layers.get(layer_name)
                    except DXFTableEntryError:
                        pass
                    else:
                        tagwriter.write_tag2(FROZEN_LAYER_GROUP_CODE,
                                             layer.dxf.handle)

            self.dxf.export_dxf_attribs(tagwriter, [
                'flags', 'clipping_boundary_handle', 'plot_style_name',
                'render_mode', 'ucs_per_viewport', 'ucs_icon', 'ucs_origin',
                'ucs_x_axis', 'ucs_y_axis', 'ucs_handle', 'ucs_base_handle',
                'ucs_ortho_type', 'elevation', 'shade_plot_mode',
                'grid_frequency', 'background_handle', 'shade_plot_handle',
                'visual_style_handle', 'default_lighting_flag',
                'default_lighting_type', 'view_brightness', 'view_contrast',
                'ambient_light_color_1', 'ambient_light_color_2',
                'ambient_light_color_3', 'sun_handle', 'ref_vp_object_1',
                'ref_vp_object_2', 'ref_vp_object_3', 'ref_vp_object_4'
            ])

    def export_acdb_viewport_r12(self, tagwriter: 'TagWriter'):
        self.dxf.export_dxf_attribs(tagwriter, [
            'center', 'width', 'height', 'status', 'id',
        ])
        tagwriter.write_tags(self.dxftags())

    def dxftags(self) -> Tags:
        def flag(flag):
            return 1 if self.dxf.flags & flag else 0

        dxf = self.dxf
        tags = [
            DXFTag(1001, 'ACAD'),
            DXFTag(1000, 'MVIEW'),
            DXFTag(1002, '{'),
            DXFTag(1070, 16),  # extended data version, always 16 for R11/12
            DXFVertex(1010, dxf.view_target_point),
            DXFVertex(1010, dxf.view_direction_vector),
            DXFTag(1040, dxf.view_twist_angle),
            DXFTag(1040, dxf.view_height),
            DXFTag(1040, dxf.view_center_point[0]),
            DXFTag(1040, dxf.view_center_point[1], ),
            DXFTag(1040, dxf.perspective_lens_length),
            DXFTag(1040, dxf.front_clip_plane_z_value),
            DXFTag(1040, dxf.back_clip_plane_z_value),
            DXFTag(1070, dxf.render_mode),
            DXFTag(1070, dxf.circle_zoom),
            DXFTag(1070, flag(const.VSF_FAST_ZOOM)),
            DXFTag(1070, dxf.ucs_icon),
            DXFTag(1070, flag(const.VSF_SNAP_MODE)),
            DXFTag(1070, flag(const.VSF_GRID_MODE)),
            DXFTag(1070, flag(const.VSF_ISOMETRIC_SNAP_STYLE)),
            DXFTag(1070, 0),  # snap isopair ???
            DXFTag(1040, dxf.snap_angle),
            DXFTag(1040, dxf.snap_base_point[0]),
            DXFTag(1040, dxf.snap_base_point[1]),
            DXFTag(1040, dxf.snap_spacing[0]),
            DXFTag(1040, dxf.snap_spacing[1]),
            DXFTag(1040, dxf.grid_spacing[0]),
            DXFTag(1040, dxf.grid_spacing[1]),
            DXFTag(1070, flag(const.VSF_HIDE_PLOT_MODE)),
            DXFTag(1002, '{'),  # start frozen layer list
        ]
        tags.extend(
            DXFTag(1003, layer_name) for layer_name in self.frozen_layers)
        tags.extend([
            DXFTag(1002, '}'),  # end of frozen layer list
            DXFTag(1002, '}'),  # MVIEW
        ])
        return Tags(tags)

    def rename_frozen_layer(self, old_name: str, new_name: str) -> None:
        key = self.doc.layers.key
        old_key = key(old_name)
        self.frozen_layers = [
            (name if key(name) != old_key else new_name)
            for name in self.frozen_layers
        ]

    def boundary_path(self) -> List[Vec3]:
        center = self.dxf.center
        cx = center.x
        cy = center.y
        width2 = self.dxf.width / 2
        height2 = self.dxf.height / 2
        # TODO: clipping path support for the Viewport entity
        return [
            Vec3(cx - width2, cy - height2),
            Vec3(cx + width2, cy - height2),
            Vec3(cx + width2, cy + height2),
            Vec3(cx - width2, cy + height2),
        ]

    def has_clipping_path(self) -> bool:
        _flag = self.dxf.flags & const.VSF_NON_RECTANGULAR_CLIPPING
        if _flag:
            handle = self.dxf.clipping_boundary_handle
            return handle != '0'
        return False
