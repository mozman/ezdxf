# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-02-21
from typing import TYPE_CHECKING
from ezdxf.math import Vector
from ezdxf.math.transformtools import OCSTransform
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace, UCS, Matrix44

__all__ = ['Shape']

acdb_shape = DefSubclass('AcDbShape', {
    'thickness': DXFAttr(39, default=0, optional=True),  # Thickness
    'insert': DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0)),  # Insertion point (in WCS)
    'size': DXFAttr(40, default=1),
    'name': DXFAttr(2, default=''),  # Shape name
    'rotation': DXFAttr(50, default=0, optional=True),  # Rotation angle in degrees
    'xscale': DXFAttr(41, default=1, optional=True),  # Relative X scale factor
    'oblique': DXFAttr(51, default=0, optional=True),  # Oblique angle
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=Vector(0, 0, 1), optional=True),  # Extrusion direction
})


@register_entity
class Shape(DXFGraphic):
    """ DXF SHAPE entity """
    DXFTYPE = 'SHAPE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_shape)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_shape)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, subclass=acdb_shape.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_shape.name)
        # for all DXF versions
        self.dxf.export_dxf_attribs(tagwriter, [
            'insert', 'size', 'name', 'thickness', 'rotation', 'xscale', 'oblique', 'extrusion',
        ])

    def transform_to_wcs(self, ucs: 'UCS') -> 'Shape':
        """ Transform SHAPE entity from local :class:`~ezdxf.math.UCS` coordinates to :ref:`WCS` coordinates.

        .. versionadded:: 0.11

        """
        self._ucs_and_ocs_transformation(ucs, vector_names=('insert',), angle_names=('rotation',))
        return self

    def transform(self, m: 'Matrix44') -> 'Shape':
        """ Transform SHAPE entity by transformation matrix `m` inplace.

        .. versionadded:: 0.13

        """
        dxf = self.dxf
        dxf.insert = m.transform(dxf.insert)  # DXF Reference: WCS?
        ocs = OCSTransform(self.dxf.extrusion, m)

        dxf.rotation = ocs.transform_deg_angle(dxf.rotation)
        dxf.oblique = ocs.transform_deg_angle(dxf.oblique)
        dxf.size = ocs.transform_length((0, dxf.size, 0))
        dxf.x_scale = ocs.transform_length((dxf.x_scale, 0, 0))
        dxf.extrusion = ocs.new_extrusion
        return self
