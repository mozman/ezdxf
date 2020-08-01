# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-02-21
from typing import TYPE_CHECKING
from ezdxf.lldxf import validator
from ezdxf.lldxf.attributes import (
    DXFAttr, DXFAttributes, DefSubclass, XType, RETURN_DEFAULT,
)
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from ezdxf.math import NULLVEC, Z_AXIS
from ezdxf.math.transformtools import OCSTransform
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace, Matrix44

__all__ = ['Shape']

acdb_shape = DefSubclass('AcDbShape', {
    # Thickness could be negative:
    'thickness': DXFAttr(39, default=0, optional=True),

    # Insertion point (in WCS)
    'insert': DXFAttr(10, xtype=XType.point3d, default=NULLVEC),

    # Shape size:
    'size': DXFAttr(40, default=1),

    # Shape name:
    'name': DXFAttr(2, default=''),

    # Rotation angle in degrees:
    'rotation': DXFAttr(50, default=0, optional=True),

    # Relative X scale factor
    'xscale': DXFAttr(
        41, default=1, optional=True,
        validator=validator.is_not_zero,
        fixer=RETURN_DEFAULT,
    ),
    # Oblique angle in degrees:
    'oblique': DXFAttr(51, default=0, optional=True),

    'extrusion': DXFAttr(
        210, xtype=XType.point3d, default=Z_AXIS, optional=True,
        validator=validator.is_not_null_vector,
        fixer=RETURN_DEFAULT,
    ),
})


@register_entity
class Shape(DXFGraphic):
    """ DXF SHAPE entity """
    DXFTYPE = 'SHAPE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_shape)

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_shape)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, subclass=acdb_shape.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        super().export_entity(tagwriter)
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_shape.name)
        self.dxf.export_dxf_attribs(tagwriter, [
            'insert', 'size', 'name', 'thickness', 'rotation', 'xscale',
            'oblique', 'extrusion',
        ])

    def transform(self, m: 'Matrix44') -> 'Shape':
        """ Transform SHAPE entity by transformation matrix `m` inplace.

        .. versionadded:: 0.13

        """
        dxf = self.dxf
        dxf.insert = m.transform(dxf.insert)  # DXF Reference: WCS?
        ocs = OCSTransform(self.dxf.extrusion, m)

        dxf.rotation = ocs.transform_deg_angle(dxf.rotation)
        dxf.size = ocs.transform_length((0, dxf.size, 0))
        dxf.x_scale = ocs.transform_length(
            (dxf.x_scale, 0, 0), reflection=dxf.x_scale)
        if dxf.hasattr('thickness'):
            dxf.thickness = ocs.transform_length(
                (0, 0, dxf.thickness), reflection=dxf.thickness)

        dxf.extrusion = ocs.new_extrusion
        return self
