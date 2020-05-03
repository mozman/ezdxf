# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-02-16
from typing import TYPE_CHECKING, Iterable, cast, Tuple, Union, Optional, List, Dict, Callable
import math
from ezdxf.math import Vector, UCS, BRCS, X_AXIS, Y_AXIS, Matrix44, OCS
from ezdxf.math.transformtools import (
    transform_extrusion, transform_ocs_vertex, transform_scale_factor, transform_angle
)

from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER, DXFValueError, DXFKeyError, DXFStructureError
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity, SeqEnd
from .factory import register_entity
from ezdxf.explode import explode_block_reference, virtual_block_reference_entities
from ezdxf.query import EntityQuery

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        TagWriter, Vertex, DXFNamespace, DXFEntity, Drawing, Attrib, AttDef, UCS,
        BlockLayout, BaseLayout
    )

__all__ = ['Insert']

# multiple insert has subclass id AcDbMInsertBlock
acdb_block_reference = DefSubclass('AcDbBlockReference', {
    'attribs_follow': DXFAttr(66, default=0, optional=True),
    'name': DXFAttr(2),
    'insert': DXFAttr(10, xtype=XType.any_point),
    'xscale': DXFAttr(41, default=1, optional=True),
    'yscale': DXFAttr(42, default=1, optional=True),
    'zscale': DXFAttr(43, default=1, optional=True),
    'rotation': DXFAttr(50, default=0, optional=True),
    'column_count': DXFAttr(70, default=1, optional=True),
    'row_count': DXFAttr(71, default=1, optional=True),
    'column_spacing': DXFAttr(44, default=0, optional=True),
    'row_spacing': DXFAttr(45, default=0, optional=True),
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=Vector(0, 0, 1), optional=True),
})


@register_entity
class Insert(DXFGraphic):
    """ DXF INSERT entity """
    DXFTYPE = 'INSERT'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_block_reference)

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self.attribs = []  # type: List[Attrib]
        self.seqend = None  # type: SeqEnd

    def linked_entities(self) -> Iterable['DXFEntity']:
        # don't yield seqend here, because it is not a DXFGraphic entity
        return self.attribs

    def link_entity(self, entity: 'DXFGraphic') -> None:
        entity.set_owner(self.dxf.owner, self.dxf.paperspace)
        self.attribs.append(entity)

    def link_seqend(self, seqend: 'DXFEntity') -> None:
        seqend.dxf.owner = self.dxf.owner
        self.seqend = seqend

    @property
    def attribs_follow(self) -> bool:
        return bool(len(self.attribs))

    def _copy_data(self, entity: 'Insert') -> None:
        """ Copy ATTRIB entities, does not store the copies into database. """
        entity.attribs = [attrib.copy() for attrib in self.attribs]
        if self.seqend:  # is None for INSERTS loaded from file with attached ATTRIBS
            entity.seqend = self.seqend.copy()

    def add_sub_entities_to_entitydb(self):
        """ Called by EntityDB.add() """
        for attrib in self.attribs:
            attrib.doc = self.doc  # grant same document
            self.entitydb.add(attrib)
        if self.seqend:
            self.seqend.doc = self.doc  # grant same document
            self.entitydb.add(self.seqend)

    def set_owner(self, owner: str, paperspace: int = 0):
        # At loading form file, INSERT will be added to layout before attribs are linked, so set_owner() of INSERT
        # does not set owner of attribs
        super().set_owner(owner, paperspace)
        # attribs handled by super class by linked_entities() interface
        if self.seqend:  # has no paperspace flag
            self.seqend.dxf.owner = owner

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        """
        Adds subclass processing for 'AcDbLine', requires previous base class and 'AcDbEntity' processing by parent
        class.
        """
        dxf = super().load_dxf_attribs(processor)
        if processor:
            # always use 2nd subclass, could be AcDbBlockReference or AcDbMInsertBlock
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_block_reference, 2)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, subclass=acdb_block_reference.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            if (self.dxf.column_count > 1) or (self.dxf.row_count > 1):
                tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDbMInsertBlock')
            else:
                tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDbBlockReference')
        # for all DXF versions
        if self.attribs_follow:
            tagwriter.write_tag2(66, 1)
        self.dxf.export_dxf_attribs(tagwriter, [
            'name', 'insert',
            'xscale', 'yscale', 'zscale',
            'rotation',
            'column_count', 'row_count',
            'column_spacing', 'row_spacing',
            'extrusion',
        ])

        # xdata and embedded objects export will be done by parent clas
        # ATTRIBS and following SEQEND is exported by EntitySpace()

    def export_seqend(self, tagwriter: 'TagWriter'):
        # export at same layer, don't know if ATTRIB entities must have the same layer
        self.seqend.dxf.layer = self.dxf.layer
        self.seqend.export_dxf(tagwriter)

    def destroy(self) -> None:
        """
        Delete all data and references.

        """
        self.delete_all_attribs()
        if self.seqend is not None:
            self.entitydb.delete_entity(self.seqend)
        super().destroy()

    @property
    def has_scaling(self) -> bool:
        """ Returns ``True`` if any axis scaling is applied.

        .. versionadded:: 0.12

        """
        if self.dxf.hasattr('xscale') and self.dxf.xscale != 1:
            return True
        if self.dxf.hasattr('yscale') and self.dxf.yscale != 1:
            return True
        if self.dxf.hasattr('zscale') and self.dxf.zscale != 1:
            return True
        return False

    @property
    def has_uniform_scaling(self) -> bool:
        """ Returns ``True`` if scaling is uniform in x-, y- and z-axis.

        .. versionadded:: 0.12

        """
        return self.dxf.xscale == self.dxf.yscale == self.dxf.zscale

    @property
    def text_scaling(self) -> float:
        """ Returns uniform scaling factor for text entities.

        .. versionadded:: 0.12

        """
        return max(abs(self.dxf.xscale), abs(self.dxf.yscale), abs(self.dxf.zscale))

    def set_scale(self, factor: float):
        """ Set uniform scaling.

        .. versionadded:: 0.12

        """
        if factor == 0:
            raise ValueError('Invalid scaling factor.')
        self.dxf.xscale = factor
        self.dxf.yscale = factor
        self.dxf.zscale = factor
        return self

    def block(self) -> Optional['BlockLayout']:
        """  Returns associated :class:`~ezdxf.layouts.BlockLayout`.

        .. versionadded:: 0.12

        """
        if self.doc is None:
            return None
        block_layout = self.doc.blocks.get(self.dxf.name)
        if block_layout is not None and block_layout.block.dxf.flags & 12:  # XREF(4) & XREF_OVERLAY(8)
            return None
        return block_layout

    def place(self, insert: 'Vertex' = None,
              scale: Tuple[float, float, float] = None,
              rotation: float = None) -> 'Insert':
        """
        Set block reference placing location `insert`, scaling and rotation attributes.
        Parameters which are ``None`` will not be altered.

        Args:
            insert: insert location as ``(x, y [,z])`` tuple
            scale: ``(x-scale, y-scale, z-scale)`` tuple
            rotation : rotation angle in degrees

        """
        if insert is not None:
            self.dxf.insert = insert
        if scale is not None:
            if len(scale) != 3:
                raise DXFValueError("Parameter scale has to be a (x, y, z)-tuple.")
            x, y, z = scale
            self.dxf.xscale = x
            self.dxf.yscale = y
            self.dxf.zscale = z
        if rotation is not None:
            self.dxf.rotation = rotation
        return self

    def grid(self, size: Tuple[int, int] = (1, 1), spacing: Tuple[float, float] = (1, 1)) -> 'Insert':
        """
        Place block reference in a grid layout, grid `size` defines the row- and column count,
        `spacing` defines the distance between two block references.

        Args:
            size: grid size as ``(row_count, column_count)`` tuple
            spacing: distance between placing as ``(row_spacing, column_spacing)`` tuple

        """
        if len(size) != 2:
            raise DXFValueError("Parameter size has to be a (row_count, column_count)-tuple.")
        if len(spacing) != 2:
            raise DXFValueError("Parameter spacing has to be a (row_spacing, column_spacing)-tuple.")
        self.dxf.row_count = size[0]
        self.dxf.column_count = size[1]
        self.dxf.row_spacing = spacing[0]
        self.dxf.column_spacing = spacing[1]
        return self

    def get_attrib(self, tag: str, search_const: bool = False) -> Optional[Union['Attrib', 'AttDef']]:
        """
        Get attached :class:`Attrib` entity with :code:`dxf.tag == tag`, returns ``None`` if not found.
        Some applications may not attach constant ATTRIB entities, set `search_const` to ``True``,
        to get at least the associated :class:`AttDef` entity.

        Args:
            tag: tag name
            search_const: search also const ATTDEF entities

        Returns:
            ATTRIB or ATTDEF object

        """
        for attrib in self.attribs:
            if tag == attrib.dxf.tag:
                return attrib
        if search_const and self.doc is not None:
            block = self.doc.blocks[self.dxf.name]  # raises KeyError() if not found
            for attdef in block.get_const_attdefs():
                if tag == attdef.dxf.tag:
                    return attdef
        return None

    def get_attrib_text(self, tag: str, default: str = None, search_const: bool = False) -> str:
        """
        Get content text of attached :class:`Attrib` entity with :code:`dxf.tag == tag`, returns `default` if not found.
        Some applications may not attach constant ATTRIB entities, set `search_const` to ``True``,
        to get content text of the associated :class:`AttDef` entity.

        Args:
            tag: tag name
            default: default value if ATTRIB `tag` is absent
            search_const: search also const ATTDEF entities

        """
        attrib = self.get_attrib(tag, search_const)
        if attrib is None:
            return default
        return attrib.dxf.text

    def has_attrib(self, tag: str, search_const: bool = False) -> bool:
        """
        Returns ``True`` if ATTRIB `tag` exist, for `search_const` doc see :meth:`get_attrib`.

        Args:
            tag: tag name as string
            search_const: search also const ATTDEF entities

        """
        return self.get_attrib(tag, search_const) is not None

    def add_attrib(self, tag: str, text: str, insert: 'Vertex' = (0, 0), dxfattribs: dict = None) -> 'Attrib':
        """
        Attach an :class:`Attrib` entity to the block reference.

        Example for appending an attribute to an INSERT entity with none standard alignment::

            e.add_attrib('EXAMPLETAG', 'example text').set_pos((3, 7), align='MIDDLE_CENTER')

        Args:
            tag: tag name as string
            text: content text as string
            insert: insert loaction as tuple ``(x, y[, z])`` in :ref:`WCS`
            dxfattribs: additional DXF attributes for the ATTRIB entity

        """
        dxfattribs = dxfattribs or {}
        dxfattribs['tag'] = tag
        dxfattribs['text'] = text
        dxfattribs['insert'] = insert
        attrib = cast('Attrib', self._new_compound_entity('ATTRIB', dxfattribs))
        self.attribs.append(attrib)

        # this case is only possible if INSERT is read from file without attached ATTRIBS
        if self.seqend is None:
            self.new_seqend()
        return attrib

    def new_seqend(self):
        """ Create new ENDSEQ. (internal API)"""
        seqend = self.doc.dxffactory.create_db_entry('SEQEND', dxfattribs={'layer': self.dxf.layer})
        self.link_seqend(seqend)

    def delete_attrib(self, tag: str, ignore=False) -> None:
        """
        Delete an attached :class:`Attrib` entity from INSERT. If `ignore` is ``False``, an :class:`DXFKeyError`
        exception is raised, if ATTRIB `tag` does not exist.

        Args:
            tag: ATTRIB name
            ignore: ``False`` for raising :class:`DXFKeyError` if ATTRIB `tag` does not exist.

        Raises:
            DXFKeyError: if ATTRIB `tag` does not exist.

        """
        for index, attrib in enumerate(self.attribs):
            if attrib.dxf.tag == tag:
                del self.attribs[index]
                self.entitydb.delete_entity(attrib)
                return
        if not ignore:
            raise DXFKeyError(tag)

    def delete_all_attribs(self) -> None:
        """ Delete all :class:`Attrib` entities attached to the INSERT entity. """
        db = self.entitydb
        for attrib in self.attribs:
            db.delete_entity(attrib)
        self.attribs = []

    def transform_to_wcs(self, ucs: 'UCS') -> 'Insert':
        """ Transform INSERT entity and attached ATTRIB entities from local :class:`~ezdxf.math.UCS` coordinates to
        :ref:`WCS` coordinates.

        .. versionadded:: 0.11

        """
        self._ucs_and_ocs_transformation(ucs, vector_names=['insert'], angle_names=['rotation'])

        for attrib in self.attribs:
            attrib.transform_to_wcs(ucs)
        return self

    def transform(self, m: 'Matrix44') -> 'Insert':
        """ Transform INSERT entity by transformation matrix `m` inplace.

        .. versionadded:: 0.13

        """
        dxf = self.dxf
        old_ocs = OCS(dxf.extrusion)
        new_extrusion, _ = transform_extrusion(dxf.extrusion, m)
        new_ocs = OCS(new_extrusion)

        dxf.insert = transform_ocs_vertex(dxf.insert, old_ocs, new_ocs, m)
        dxf.rotation = math.degrees(transform_angle(math.radians(dxf.rotation), old_ocs, new_extrusion, m))

        # todo: transform_scale_factor is transform_length and does not return negative scaling
        dxf.xscale = transform_scale_factor((dxf.xscale, 0, 0), old_ocs, m)
        dxf.yscale = transform_scale_factor((0, dxf.yscale, 0), old_ocs, m)
        dxf.zscale = transform_scale_factor((0, 0, dxf.zscale), old_ocs, m)

        for attrib in self.attribs:
            attrib.transform(m)
        return self

    def brcs(self) -> 'BRCS':
        """ Returns a block reference coordinate system as :class:`BRCS` object, placed at the block reference
        `insert` location, axis aligned to the block axis, :attr:`~Insert.dxf.rotation` around z-axis and axis
        scaling :attr:`~Insert.dxf.xscale`, :attr:`~Insert.dxf.yscale` and :attr:`~Insert.dxf.zscale` are applied.

        .. versionchanged:: 0.12
            renamed from :meth:`ucs`

        """
        sx = self.dxf.xscale
        sy = self.dxf.yscale
        sz = self.dxf.zscale
        ocs = self.ocs()
        insert = self.dxf.insert
        if insert is None:
            insert = Vector()
        else:
            insert = Vector(insert)

        brcs = BRCS(
            insert=ocs.to_wcs(insert),
            ux=ocs.to_wcs(X_AXIS) * sx,
            uy=ocs.to_wcs(Y_AXIS) * sy,
            uz=Vector(self.dxf.extrusion).normalize(sz),
        )
        brcs._rotate_local_z(math.radians(self.dxf.rotation))
        block_layout = self.block()
        if block_layout is not None:
            brcs._base_point = Vector(block_layout.block.dxf.base_point)
        return brcs

    def reset_transformation(self):
        """ Reset block reference parameters `location`, `rotation` and `extrusion` vector.

        .. versionadded:: 0.11

        """
        self.dxf.insert = (0, 0, 0)
        self.dxf.discard('rotation')
        self.dxf.discard('extrusion')

    def explode(self, target_layout: 'BaseLayout' = None, non_uniform_scaling=False) -> 'EntityQuery':
        """
        Explode block reference entities into target layout, if target layout is ``None``, the target layout is the
        layout of the block reference.

        Transforms the block entities into the required :ref:`WCS` location by applying the block reference
        attributes `insert`, `extrusion`, `rotation` and the scaling values `xscale`, `yscale` and `zscale`.
        Multiple inserts by row and column attributes is not supported.

        Attached ATTRIB entities are converted to TEXT entities, this is the behavior of the BURST command of
        the AutoCAD Express Tools.

        Returns an :class:`~ezdxf.query.EntityQuery` container with all "exploded" DXF entities.

        .. warning::

            **Non uniform scaling** lead to incorrect results for text entities (TEXT, MTEXT, ATTRIB) and
            some other entities like ELLIPSE, SHAPE, HATCH with arc or ellipse path segments and and
            POLYLINE/LWPOLYLINE with arc segments. Non uniform scaling is getting better, but still not perfect!

        Args:
            target_layout: target layout for exploded entities, ``None`` for same layout as source entity.
            non_uniform_scaling: enable non uniform scaling if ``True``, see warning

        .. versionadded:: 0.12
            experimental feature

        """
        if target_layout is None:
            target_layout = self.get_layout()
            if target_layout is None:
                raise DXFStructureError('INSERT without layout assigment, specify target layout.')

        if non_uniform_scaling is False and not self.has_uniform_scaling:
            return EntityQuery()

        return explode_block_reference(self, target_layout=target_layout)

    def virtual_entities(self,
                         non_uniform_scaling=False,
                         skipped_entity_callback: Optional[Callable[[DXFGraphic, str], None]] = None
                         ) -> Iterable[DXFGraphic]:
        """
        Yields "virtual" entities of a block reference. This method is meant to examine the block reference
        entities at the "exploded" location without really "exploding" the block reference. The
        `skipped_entity_callback()` will be called for all entities which are not processed, signature:
        :code:`skipped_entity_callback(entity: DXFEntity, reason: str)`, `entity` is the original (untransformed)
        DXF entity of the block definition, the `reason` string is an explanation why the entity was skipped.

        This entities are not stored in the entity database, have no handle and are not assigned to any layout.
        It is possible to convert this entities into regular drawing entities by adding the entities to the
        entities database and a layout of the same DXF document as the block reference::

            doc.entitydb.add(entity)
            msp = doc.modelspace()
            msp.add_entity(entity)

        .. warning::

            **Non uniform scaling** returns incorrect results for text entities (TEXT, MTEXT, ATTRIB) and
            some other entities like ELLIPSE, SHAPE, HATCH with arc or ellipse path segments and
            POLYLINE/LWPOLYLINE with arc segments. Non uniform scaling is getting better, but still not perfect!

        Args:
            non_uniform_scaling: enable non uniform scaling if ``True``, see warning
            skipped_entity_callback: called whenever the transformation of an entity is not supported and so was skipped

        .. versionadded:: 0.12
            experimental feature

        """
        if non_uniform_scaling is False and not self.has_uniform_scaling:
            return []

        return virtual_block_reference_entities(self, skipped_entity_callback=skipped_entity_callback)

    def add_auto_attribs(self, values: Dict[str, str]) -> 'Insert':
        """
        Attach for each :class:`~ezdxf.entities.Attdef` entity, defined in the block definition,
        automatically an :class:`Attrib` entity to the block reference and set ``tag/value`` DXF attributes of
        the ATTRIB entities by the ``key/value`` pairs (both as strings) of the `values` dict.
        The ATTRIB entities are placed relative to the insert location of the block reference, which is identical to the
        block base point.

        This method avoids the wrapper block of the :meth:`~ezdxf.layouts.BaseLayout.add_auto_blockref` method, but
        the visual results may not match the results of CAD applications, especially for non uniform scaling.
        If the visual result is very important to you, use the :meth:`add_auto_blockref` method.

        .. versionadded: 0.12

        Args:
            values: :class:`~ezdxf.entities.Attrib` tag values as ``tag/value`` pairs

        """

        def unpack(dxfattribs) -> Tuple[str, str, 'Vertex']:
            tag = dxfattribs.pop('tag')
            text = values.get(tag, "")
            location = dxfattribs.pop('insert')
            return tag, text, location

        def autofill() -> None:
            for attdef in blockdef.attdefs():
                dxfattribs = attdef.dxfattribs(drop={'prompt', 'handle'})
                tag, text, location = unpack(dxfattribs)
                attrib = self.add_attrib(tag, text, location, dxfattribs)
                attrib.transform_to_wcs(brcs)
                attrib.dxf.height *= attrib_scaling_factor

        brcs = cast('UCS', self.brcs())
        # This method does not work well for non uniform scaled block references!
        attrib_scaling_factor = self.text_scaling
        blockdef = self.block()
        autofill()
        return self
