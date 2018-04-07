# Created: 06.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from ..lldxf.const import DXFStructureError, DXFValueError, DXFKeyError
from ..lldxf.types import DXFTag
from .dxfobjects import none_subclass, DXFAttr, DXFAttributes, DefSubclass, ExtendedTags, DXFObject
from .object_manager import ObjectManager
from ..algebra.matrix44 import Matrix44


_MATERIAL_TPL = """0
MATERIAL
5
0
102
{ACAD_REACTORS
102
}
330
0
100
AcDbMaterial
1
Name
94
63
"""

_MATERIAL_CLS = """0
CLASS
1
MATERIAL
2
AcDbMaterial
3
ObjectDBX Classes
90
1153
91
0
280
0
281
0
"""

material_subclass = DefSubclass('AcDbMaterial', {
    'name': DXFAttr(1),
    'description': DXFAttr(2, default=''),
    'ambient_color_method': DXFAttr(70, default=0),  # 0=use current color; 1=override current color
    'ambient_color_factor': DXFAttr(40, default=1.),  # valid range is 0.0 to 1.0
    'ambient_color_value': DXFAttr(90),  # integer representing an AcCmEntityColor
    'diffuse_color_method': DXFAttr(71, default=0),  # 0=use current color; 1=override current color
    'diffuse_color_factor': DXFAttr(41, default=1.),  # valid range is 0.0 to 1.0
    'diffuse_color_value': DXFAttr(91),  # integer representing an AcCmEntityColor
    'diffuse_map_blend_factor': DXFAttr(42, default=1.),  # valid range is 0.0 to 1.0
    'diffuse_map_source': DXFAttr(72, default=1),  # 0=use current scene; 1=use image file (specified by file name; null file name specifies no map)
    'diffuse_map_file_name': DXFAttr(3, default=''),
    'diffuse_map_projection_method': DXFAttr(73, default=1),  # 1=Planar; 2=Box; 3=Cylinder; 4=Sphere
    'diffuse_map_tiling_method': DXFAttr(74, default=1),  # 1=Tile; 2=Crop; 3=Clamp
    'diffuse_map_auto_transform_method': DXFAttr(75, default=1),  # bitset;
    # 1 = No auto transform
    # 2 = Scale mapper to current entity extents; translate mapper to entity origin
    # 4 = Include current block transform in mapper transform
    # 16x group code 43: Transform matrix of diffuse map mapper (16 reals; row major format; default = identity matrix)
    'specular_gloss_factor': DXFAttr(44, default=.5),  # valid range is 0.0 to 1.0
    'specular_color_method': DXFAttr(73, default=0),  # 0=use current color; 1=override current color
    'specular_color_factor': DXFAttr(45, default=1.),  # valid range is 0.0 to 1.0
    'specular_color_value': DXFAttr(92),  # integer representing an AcCmEntityColor
    'specular_map_blend_factor': DXFAttr(46, default=1.),  # valid range is 0.0 to 1.0
    'specular_map_source': DXFAttr(77, default=1), # 0=use current scene; 1=use image file (specified by file name; null file name specifies no map)
    'specular_map_file_name': DXFAttr(4, default=''),
    'specular_map_projection_method': DXFAttr(78, default=1),  # 1=Planar; 2=Box; 3=Cylinder; 4=Sphere
    'specular_map_tiling_method': DXFAttr(79, default=1),  # 1=Tile; 2=Crop; 3=Clamp
    'specular_map_auto_transform_method': DXFAttr(170, default=1),  # bitset;
    # 1 = No auto transform
    # 2 = Scale mapper to current entity extents; translate mapper to entity origin
    # 4 = Include current block transform in mapper transform
    # 16x group code 47: Transform matrix of specular map mapper (16 reals; row major format; default = identity matrix)
    'reflection_map_blend_factor': DXFAttr(48, default=1.),  # valid range is 0.0 to 1.0
    'reflection_map_source': DXFAttr(171, default=1),  # 0=use current scene; 1=use image file (specified by file name; null file name specifies no map)
    'reflection_map_file_name': DXFAttr(6, default=''),
    'reflection_map_projection_method': DXFAttr(172, default=1),  # 1=Planar; 2=Box; 3=Cylinder; 4=Sphere
    'reflection_map_tiling_method': DXFAttr(173, default=1),  # 1=Tile; 2=Crop; 3=Clamp
    'reflection_map_auto_transform_method': DXFAttr(174, default=1),  # bitset;
    # 1 = No auto transform
    # 2 = Scale mapper to current entity extents; translate mapper to entity origin
    # 4 = Include current block transform in mapper transform
    # 16x group code 49: Transform matrix of reflection map mapper (16 reals; row major format; default = identity matrix)
    'opacity': DXFAttr(140, default=1.),  # valid range is 0.0 to 1.0
    'opacity_map_blend_factor': DXFAttr(141, default=1.),  # valid range is 0.0 to 1.0
    'opacity_map_source': DXFAttr(175, default=1),  # 0=use current scene; 1=use image file (specified by file name; null file name specifies no map)
    'opacity_map_file_name': DXFAttr(7, default=''),
    'opacity_map_projection_method': DXFAttr(176, default=1),  # 1=Planar; 2=Box; 3=Cylinder; 4=Sphere
    'opacity_map_tiling_method': DXFAttr(177, default=1),  # 1=Tile; 2=Crop; 3=Clamp
    'opacity_map_auto_transform_method': DXFAttr(178, default=1),  # bitset;
    # 1 = No auto transform
    # 2 = Scale mapper to current entity extents; translate mapper to entity origin
    # 4 = Include current block transform in mapper transform
    # 16x group code 142: Transform matrix of reflection map mapper (16 reals; row major format; default = identity matrix)
    'bump_map_blend_factor': DXFAttr(143, default=1.),  # valid range is 0.0 to 1.0
    'bump_map_source': DXFAttr(179, default=1),  # 0=use current scene; 1=use image file (specified by file name; null file name specifies no map)
    'bump_map_file_name': DXFAttr(8, default=''),
    'bump_map_projection_method': DXFAttr(270, default=1),  # 1=Planar; 2=Box; 3=Cylinder; 4=Sphere
    'bump_map_tiling_method': DXFAttr(271, default=1),  # 1=Tile; 2=Crop; 3=Clamp
    'bump_map_auto_transform_method': DXFAttr(272, default=1),  # bitset;
    # 1 = No auto transform
    # 2 = Scale mapper to current entity extents; translate mapper to entity origin
    # 4 = Include current block transform in mapper transform
    # 16x group code 144: Transform matrix of bump map mapper (16 reals; row major format; default = identity matrix)
    'refraction_index': DXFAttr(145, default=1.),  # valid range is 0.0 to 1.0
    'refraction_map_blend_factor': DXFAttr(146, default=1.),  # valid range is 0.0 to 1.0
    'refraction_map_source': DXFAttr(273, default=1),  # 0=use current scene; 1=use image file (specified by file name; null file name specifies no map)
    'refraction_map_file_name': DXFAttr(9, default=''),
    'refraction_map_projection_method': DXFAttr(274, default=1),  # 1=Planar; 2=Box; 3=Cylinder; 4=Sphere
    'refraction_map_tiling_method': DXFAttr(275, default=1),  # 1=Tile; 2=Crop; 3=Clamp
    'refraction_map_auto_transform_method': DXFAttr(276, default=1),  # bitset;
    # 1 = No auto transform
    # 2 = Scale mapper to current entity extents; translate mapper to entity origin
    # 4 = Include current block transform in mapper transform
    # 16x group code 147: Transform matrix of reflection map mapper (16 reals; row major format; default = identity matrix)

    # normal map shares group codes with diffuse map
    'normal_map_method': DXFAttr(271),
    'normal_map_strength': DXFAttr(465),
    'normal_map_blend_factor': DXFAttr(42, default=1.),  # valid range is 0.0 to 1.0
    'normal_map_source': DXFAttr(72, default=1),  # 0=use current scene; 1=use image file (specified by file name; null file name specifies no map)
    'normal_map_file_name': DXFAttr(3, default=''),
    'normal_map_projection_method': DXFAttr(73, default=1),  # 1=Planar; 2=Box; 3=Cylinder; 4=Sphere
    'normal_map_tiling_method': DXFAttr(74, default=1),  # 1=Tile; 2=Crop; 3=Clamp
    'normal_map_auto_transform_method': DXFAttr(75, default=1),  # bitset;
    # 1 = No auto transform
    # 2 = Scale mapper to current entity extents; translate mapper to entity origin
    # 4 = Include current block transform in mapper transform
    # 16x group code 43: Transform matrix of reflection map mapper (16 reals; row major format; default = identity matrix)
    'color_bleed_scale': DXFAttr(460),
    'indirect_dump_scale': DXFAttr(461),
    'reflectance_scale': DXFAttr(462),
    'transmittance_scale': DXFAttr(463),
    'two_sided_material': DXFAttr(290),
    'luminance': DXFAttr(464),
    'luminance_mode': DXFAttr(270),
    'materials_anonymous': DXFAttr(293),
    'global_illumination_mode': DXFAttr(272),
    'final_gather_mMode': DXFAttr(273),
    'gen_proc_name': DXFAttr(300),
    'gen_proc_val_bool': DXFAttr(291),
    'gen_proc_val_int': DXFAttr(271),
    'gen_proc_val_real': DXFAttr(469),
    'gen_proc_val_text': DXFAttr(301),
    'gen_proc_table_end': DXFAttr(292),
    'gen_proc_val_color_index': DXFAttr(62),
    'gen_proc_val_color_rgb': DXFAttr(420),
    'gen_proc_val_color_name': DXFAttr(430),
    'map_utile': DXFAttr(270),
    'translucence': DXFAttr(148),
    'self_illuminaton': DXFAttr(90),
    'reflectivity': DXFAttr(468),
    'illumination_model': DXFAttr(93),
    'channel_flags': DXFAttr(94),
})


class Material(DXFObject):
    TEMPLATE = ExtendedTags.from_text(_MATERIAL_TPL)
    CLASS = ExtendedTags.from_text(_MATERIAL_CLS)
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        material_subclass,
    )

    def _get_matrix(self, code):
        subclass = self.tags.subclasses[1]  # always 2nd subclass
        values = [tag.value for tag in subclass.find_all(code)]
        if len(values) != 16:
            raise DXFStructureError('Invalid transformation matrix in entity ' + self.__str__())
        return Matrix44(values)

    def _set_matrix(self, code, data):
        values = list(data)
        if len(values) != 16:
            raise DXFValueError("Transformation matrix requires 16 values.")

        subclass = self.tags.subclasses[1]  # always 2nd subclass
        try:
            insert_pos = subclass.tag_index(code)
        except DXFValueError:
            insert_pos = len(subclass)
        subclass.remove_tags((code, ))
        tags = [DXFTag(code, value) for value in values]
        subclass[insert_pos:insert_pos] = tags

    def set_transformation_matrix_diffuse_map(self, matrix):
        self._set_matrix(code=43, data=matrix)

    def get_transformation_matrix_diffuse_map(self):
        return self._get_matrix(code=43)

    def set_transformation_matrix_normal_map(self, matrix):  # collision with diffuse map
        self._set_matrix(code=43, data=matrix)

    def get_transformation_matrix_normal_map(self):  # collision with diffuse map
        return self._get_matrix(code=43)

    def set_transformation_matrix_specular_map(self, matrix):
        self._set_matrix(code=47, data=matrix)

    def get_transformation_matrix_specular_map(self):
        return self._get_matrix(code=47)

    def set_transformation_matrix_reflection_map(self, matrix):
        self._set_matrix(code=49, data=matrix)

    def get_transformation_matrix_reflection_map(self):
        return self._get_matrix(code=49)

    def set_transformation_matrix_opacity_map(self, matrix):
        self._set_matrix(code=142, data=matrix)

    def get_transformation_matrix_opacity_map(self):
        return self._get_matrix(code=142)

    def set_transformation_matrix_bump_map(self, matrix):
        self._set_matrix(code=144, data=matrix)

    def get_transformation_matrix_bump_map(self):
        return self._get_matrix(code=144)

    def set_transformation_matrix_refraction_map(self, matrix):
        self._set_matrix(code=147, data=matrix)

    def get_transformation_matrix_refraction_map(self):
        return self._get_matrix(code=147)


class MaterialManager(ObjectManager):
    def __init__(self, drawing):
        super(MaterialManager, self).__init__(drawing, dict_name='ACAD_MATERIAL', object_type='MATERIAL')
        self.create_required_entries()

    @property
    def objects(self):
        return self.drawing.objects

    def create_required_entries(self):
        for name in ('ByBlock', 'ByLayer', 'Global'):
            if name not in self.object_dict:
                self.new(name)

