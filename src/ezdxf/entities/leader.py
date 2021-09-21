# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, List, Iterable
import logging
from ezdxf.lldxf import validator
from ezdxf.lldxf.attributes import (
    DXFAttr,
    DXFAttributes,
    DefSubclass,
    XType,
    RETURN_DEFAULT,
    group_code_mapping,
)
from ezdxf.lldxf.tags import Tags, DXFTag
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2000, DXFStructureError
from ezdxf.math import Vec3, X_AXIS, Z_AXIS, NULLVEC
from ezdxf.math.transformtools import transform_extrusion
from ezdxf.explode import explode_entity
from ezdxf.audit import AuditError
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity
from .dimension import OverrideMixin

logger = logging.getLogger("ezdxf")

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        TagWriter,
        DXFNamespace,
        Vertex,
        Matrix44,
        BaseLayout,
        EntityQuery,
        Auditor,
        DXFEntity,
    )

__all__ = ["Leader"]

acdb_leader = DefSubclass(
    "AcDbLeader",
    {
        "dimstyle": DXFAttr(
            3,
            default="Standard",
            validator=validator.is_valid_table_name,
            # no fixer!
        ),
        # Arrowhead flag: 0/1 = no/yes
        "has_arrowhead": DXFAttr(
            71,
            default=1,
            optional=True,
            validator=validator.is_integer_bool,
            fixer=RETURN_DEFAULT,
        ),
        # Leader path type:
        # 0 = Straight line segments
        # 1 = Spline
        "path_type": DXFAttr(
            72,
            default=0,
            optional=True,
            validator=validator.is_integer_bool,
            fixer=RETURN_DEFAULT,
        ),
        # Annotation type or leader creation flag:
        # 0 = Created with text annotation
        # 1 = Created with tolerance annotation;
        # 2 = Created with block reference annotation
        # 3 = Created without any annotation
        "annotation_type": DXFAttr(
            73,
            default=3,
            validator=validator.is_in_integer_range(0, 4),
            fixer=RETURN_DEFAULT,
        ),
        # Hook line direction flag:
        # 1 = Hook line (or end of tangent for a spline leader) is the opposite
        #     direction from the horizontal vector
        # 0 = Hook line (or end of tangent for a spline leader) is the same
        #     direction as horizontal vector (see code 75)
        # DXF reference error: swapped meaning of 1/0
        "hookline_direction": DXFAttr(
            74,
            default=1,
            optional=True,
            validator=validator.is_integer_bool,
            fixer=RETURN_DEFAULT,
        ),
        # Hook line flag: 0/1 = no/yes
        "has_hookline": DXFAttr(
            75,
            default=1,
            optional=True,
            validator=validator.is_integer_bool,
            fixer=RETURN_DEFAULT,
        ),
        # Text annotation height:
        "text_height": DXFAttr(
            40,
            default=1,
            optional=True,
            validator=validator.is_greater_zero,
            fixer=RETURN_DEFAULT,
        ),
        # Text annotation width:
        "text_width": DXFAttr(
            41,
            default=1,
            optional=True,
            validator=validator.is_greater_zero,
            fixer=RETURN_DEFAULT,
        ),
        # 76: Number of vertices in leader (ignored for OPEN)
        # 10, 20, 30: Vertex coordinates (one entry for each vertex)
        # Color to use if leader's DIMCLRD = BYBLOCK
        "block_color": DXFAttr(
            77,
            default=7,
            optional=True,
            validator=validator.is_valid_aci_color,
            fixer=RETURN_DEFAULT,
        ),
        # Hard reference to associated annotation:
        # (mtext, tolerance, or insert entity)
        "annotation_handle": DXFAttr(340, default="0", optional=True),
        "normal_vector": DXFAttr(
            210,
            xtype=XType.point3d,
            default=Z_AXIS,
            optional=True,
            validator=validator.is_not_null_vector,
            fixer=RETURN_DEFAULT,
        ),
        # 'horizontal' direction for leader
        "horizontal_direction": DXFAttr(
            211,
            xtype=XType.point3d,
            default=X_AXIS,
            optional=True,
            validator=validator.is_not_null_vector,
            fixer=RETURN_DEFAULT,
        ),
        # Offset of last leader vertex from block reference insertion point
        "leader_offset_block_ref": DXFAttr(
            212, xtype=XType.point3d, default=NULLVEC, optional=True
        ),
        # Offset of last leader vertex from annotation placement point
        "leader_offset_annotation_placement": DXFAttr(
            213, xtype=XType.point3d, default=NULLVEC, optional=True
        ),
        # Xdata belonging to the application ID "ACAD" follows a leader entity if
        # any dimension overrides have been applied to this entity. See Dimension
        # Style Overrides.
    },
)
acdb_leader_group_codes = group_code_mapping(acdb_leader)


@register_entity
class Leader(DXFGraphic, OverrideMixin):
    """DXF LEADER entity"""

    DXFTYPE = "LEADER"
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_leader)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000

    def __init__(self):
        super().__init__()
        self.vertices: List[Vec3] = []

    def _copy_data(self, entity: "DXFEntity") -> None:
        """Copy vertices."""
        assert isinstance(entity, Leader)
        entity.vertices = Vec3.list(self.vertices)

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.subclass_by_index(2)
            if tags:
                tags = Tags(self.load_vertices(tags))
                processor.fast_load_dxfattribs(
                    dxf, acdb_leader_group_codes, tags, recover=True
                )
            else:
                raise DXFStructureError(
                    f"missing 'AcDbLeader' subclass in LEADER(#{dxf.handle})"
                )

        return dxf

    def load_vertices(self, tags: Tags) -> Iterable[DXFTag]:
        for tag in tags:
            if tag.code == 10:
                self.vertices.append(tag.value)
            elif tag.code == 76:
                # Number of vertices in leader (ignored for OPEN)
                pass
            else:
                yield tag

    def preprocess_export(self, tagwriter: "TagWriter") -> bool:
        if len(self.vertices) < 2:
            logger.debug(f"Invalid {str(self)}: more than 1 vertex required.")
            return False
        else:
            return True

    def export_entity(self, tagwriter: "TagWriter") -> None:
        """Export entity specific data as DXF tags."""
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_leader.name)
        self.dxf.export_dxf_attribs(
            tagwriter,
            [
                "dimstyle",
                "has_arrowhead",
                "path_type",
                "annotation_type",
                "hookline_direction",
                "has_hookline",
                "text_height",
                "text_width",
            ],
        )
        self.export_vertices(tagwriter)
        self.dxf.export_dxf_attribs(
            tagwriter,
            [
                "block_color",
                "annotation_handle",
                "normal_vector",
                "horizontal_direction",
                "leader_offset_block_ref",
                "leader_offset_annotation_placement",
            ],
        )

    def export_vertices(self, tagwriter: "TagWriter") -> None:
        tagwriter.write_tag2(76, len(self.vertices))
        for vertex in self.vertices:
            tagwriter.write_vertex(10, vertex)

    def set_vertices(self, vertices: Iterable["Vertex"]):
        """Set vertices of the leader, vertices is an iterable of
        (x, y [,z]) tuples or :class:`~ezdxf.math.Vec3`.

        """
        self.vertices = [Vec3(v) for v in vertices]

    def transform(self, m: "Matrix44") -> "Leader":
        """Transform LEADER entity by transformation matrix `m` inplace."""
        self.vertices = list(m.transform_vertices(self.vertices))
        self.dxf.normal_vector, _ = transform_extrusion(
            self.dxf.normal_vector, m
        )  # ???
        self.dxf.horizontal_direction = m.transform_direction(
            self.dxf.horizontal_direction
        )
        self.post_transform(m)
        return self

    def __virtual_entities__(self) -> Iterable["DXFGraphic"]:
        """Implements the SupportsVirtualEntities protocol. """
        from ezdxf.render.leader import virtual_entities
        return virtual_entities(self)

    def virtual_entities(self) -> Iterable["DXFGraphic"]:
        """Yields 'virtual' parts of LEADER as DXF primitives.

        This entities are located at the original positions, but are not stored
        in the entity database, have no handle and are not assigned to any
        layout.

        """
        return self.__virtual_entities__()

    def explode(self, target_layout: "BaseLayout" = None) -> "EntityQuery":
        """
        Explode parts of LEADER as DXF primitives into target layout, if target
        layout is ``None``, the target layout is the layout of the LEADER.

        Returns an :class:`~ezdxf.query.EntityQuery` container with all
        DXF parts.

        Args:
            target_layout: target layout for DXF parts, ``None`` for same
                layout as source entity.

        .. versionadded:: 0.14

        """
        return explode_entity(self, target_layout)

    def audit(self, auditor: "Auditor") -> None:
        """Validity check."""
        super().audit(auditor)
        if len(self.vertices) < 2:
            auditor.fixed_error(
                code=AuditError.INVALID_VERTEX_COUNT,
                message=f"Deleted entity {str(self)} with invalid vertex count "
                        f"= {len(self.vertices)}.",
                dxf_entity=self,
            )
            self.destroy()
