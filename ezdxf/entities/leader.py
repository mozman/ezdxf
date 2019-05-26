# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-03-12
from typing import TYPE_CHECKING, List, Iterable
import copy
from ezdxf.math import Vector
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.tags import Tags, DXFTag
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2000
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity
from .dimension import OverrideMixin

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace, Drawing, Vertex

__all__ = ['Leader']

acdb_leader = DefSubclass('AcDbLeader', {
    'dimstyle': DXFAttr(3, default='Standard'),

    # Arrowhead flag: 0/1 = no/yes
    'has_arrowhead': DXFAttr(71, default=1, optional=True),

    # Leader path type: 0 = Straight line segments; 1 = Spline
    'path_type': DXFAttr(72, default=0, optional=True),

    # Annotation type:
    # 0 = Created with text annotation
    # 1 = Created with tolerance annotation;
    # 2 = Created with block reference annotation
    # 3 = Created without any annotation
    'annotation_type': DXFAttr(73, default=3),  # Leader creation flag:

    # Hookline direction flag:
    # 0 = Hookline (or end of tangent for a splined leader) is the opposite direction from the horizontal vector
    # 1 = Hookline (or end of tangent for a splined leader) is the same direction as horizontal vector (see code 75)
    'hookline_direction': DXFAttr(74, default=0, optional=True),

    # Hookline flag: 0/1 = no/yes
    'has_hookline': DXFAttr(75, default=0, optional=True),

    # Text annotation height
    'text_height': DXFAttr(40, default=1, optional=True),

    # Text annotation width
    'text_width': DXFAttr(41, default=1, optional=True),

    # 76: Number of vertices in leader (ignored for OPEN)
    # 10, 20, 30: Vertex coordinates (one entry for each vertex)

    # Color to use if leader's DIMCLRD = BYBLOCK
    'block_color': DXFAttr(77, default=7, optional=True),

    # Hard reference to associated annotation (mtext, tolerance, or insert entity)
    'annotation_handle': DXFAttr(340, default='0', optional=True),

    'normal_vector': DXFAttr(210, xtype=XType.point3d, default=Vector(0, 0, 1), optional=True),

    # 'horizontal' direction for leader
    'horizontal_direction': DXFAttr(211, xtype=XType.point3d, default=Vector(1, 0, 0), optional=True),

    # Offset of last leader vertex from block reference insertion point
    'leader_offset_block_ref': DXFAttr(212, xtype=XType.point3d, default=Vector(0, 0, 0), optional=True),

    # Offset of last leader vertex from annotation placement point
    'leader_offset_annotation_placement': DXFAttr(213, xtype=XType.point3d, default=Vector(0, 0, 0), optional=True),

    # Xdata belonging to the application ID "ACAD" follows a leader entity if any dimension overrides
    # have been applied to this entity. See Dimension Style Overrides.
})


@register_entity
class Leader(DXFGraphic, OverrideMixin):
    """ DXF LEADER entity """
    DXFTYPE = 'LEADER'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_leader)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self.vertices = []  # type: List[Vector]

    def _copy_data(self, entity: 'Leader') -> None:
        """ Copy vertices. """
        entity.vertices = copy.deepcopy(self.vertices)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_leader)
            tags = Tags(self.load_vertices(tags))
            if len(tags):
                # 76: Number of vertices in leader (ignored for OPEN)
                processor.log_unprocessed_tags(tags.filter((76,)), subclass=acdb_leader.name)
        return dxf

    def load_vertices(self, tags: Tags) -> Iterable[DXFTag]:
        for tag in tags:
            if tag.code == 10:
                self.vertices.append(tag.value)
            else:
                yield tag

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_leader.name)
        self.dxf.export_dxf_attribs(tagwriter, [
            'dimstyle', 'has_arrowhead', 'path_type', 'annotation_type', 'hookline_direction', 'has_hookline',
            'text_height', 'text_width',
        ])
        self.export_vertices(tagwriter)
        self.dxf.export_dxf_attribs(tagwriter, [
            'block_color', 'annotation_handle', 'normal_vector', 'horizontal_direction', 'leader_offset_block_ref',
            'leader_offset_annotation_placement'
        ])

    def export_vertices(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(76, len(self.vertices))
        for vertex in self.vertices:
            tagwriter.write_vertex(10, vertex)

    def set_vertices(self, vertices: Iterable['Vertex']):
        self.vertices = [Vector(v) for v in vertices]
