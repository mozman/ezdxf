# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-02-16
from typing import (
    TYPE_CHECKING, Iterable, cast, Tuple, Union, Optional, List,
    Callable, Dict,
)
import math
import warnings
from ezdxf.lldxf import validator
from ezdxf.lldxf.attributes import (
    DXFAttr, DXFAttributes, DefSubclass, XType, RETURN_DEFAULT,
)
from ezdxf.lldxf.const import (
    DXF12, SUBCLASS_MARKER, DXFValueError, DXFKeyError, DXFStructureError,
)
from ezdxf.math import (
    Vector, X_AXIS, Y_AXIS, Z_AXIS, Matrix44, OCS, UCS, NULLVEC,
)
from ezdxf.math.transformtools import OCSTransform, InsertTransformationError
from ezdxf.explode import (
    explode_block_reference, virtual_block_reference_entities,
)
from ezdxf.entities import factory
from ezdxf.query import EntityQuery
from ezdxf.audit import AuditError
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity, SeqEnd
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        TagWriter, Vertex, DXFNamespace, DXFEntity, Drawing, Attrib, AttDef,
        BlockLayout, BaseLayout, Auditor,
    )

__all__ = ['Insert']

# Multi-INSERT has subclass id AcDbMInsertBlock
acdb_block_reference = DefSubclass('AcDbBlockReference', {
    'attribs_follow': DXFAttr(66, default=0, optional=True),
    'name': DXFAttr(2, validator=validator.is_valid_block_name),
    'insert': DXFAttr(10, xtype=XType.any_point),
    'xscale': DXFAttr(
        41, default=1, optional=True,
        validator=validator.is_not_zero,
        fixer=RETURN_DEFAULT,
    ),
    'yscale': DXFAttr(
        42, default=1, optional=True,
        validator=validator.is_not_zero,
        fixer=RETURN_DEFAULT,
    ),
    'zscale': DXFAttr(
        43, default=1, optional=True,
        validator=validator.is_not_zero,
        fixer=RETURN_DEFAULT,
    ),
    'rotation': DXFAttr(50, default=0, optional=True),
    'column_count': DXFAttr(
        70, default=1, optional=True,
        validator=validator.is_greater_zero,
        fixer=RETURN_DEFAULT,
    ),
    'row_count': DXFAttr(
        71, default=1, optional=True,
        validator=validator.is_greater_zero,
        fixer=RETURN_DEFAULT,
    ),
    'column_spacing': DXFAttr(44, default=0, optional=True),
    'row_spacing': DXFAttr(45, default=0, optional=True),
    'extrusion': DXFAttr(
        210, xtype=XType.point3d, default=Z_AXIS, optional=True,
        validator=validator.is_not_null_vector,
        fixer=RETURN_DEFAULT,
    ),
})

NON_ORTHO_MSG = 'INSERT entity can not represent a non-orthogonal target ' \
                'coordinate system.'


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
        # Don't yield seqend here, because it is not a DXFGraphic entity
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
        if self.seqend:
            # If is None for INSERTS loaded from file with attached ATTRIBS
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
        # At loading form file, INSERT will be added to layout before attribs
        # are linked, so set_owner() of INSERT does not set owner of attribs.
        super().set_owner(owner, paperspace)
        # attribs handled by super class by linked_entities() interface
        if self.seqend:  # has no paperspace flag
            self.seqend.dxf.owner = owner

    def load_dxf_attribs(self,
                         processor: SubclassProcessor = None) -> 'DXFNamespace':
        """
        Adds subclass processing for 'AcDbLine', requires previous base class
        and 'AcDbEntity' processing by parent class.

        """
        dxf = super().load_dxf_attribs(processor)
        if processor:
            # Always use the 2nd subclass, could be AcDbBlockReference or
            # AcDbMInsertBlock:
            tags = processor.load_dxfattribs_into_namespace(
                dxf, acdb_block_reference, 2)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(
                    tags, subclass=acdb_block_reference.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        super().export_entity(tagwriter)
        if tagwriter.dxfversion > DXF12:
            if (self.dxf.column_count > 1) or (self.dxf.row_count > 1):
                tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDbMInsertBlock')
            else:
                tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDbBlockReference')
        if self.attribs_follow:
            tagwriter.write_tag2(66, 1)
        self.dxf.export_dxf_attribs(tagwriter, [
            'name', 'insert', 'xscale', 'yscale', 'zscale', 'rotation',
            'column_count', 'row_count', 'column_spacing', 'row_spacing',
            'extrusion',
        ])

    def export_seqend(self, tagwriter: 'TagWriter'):
        # Export at same layer, don't know if ATTRIB entities must have the
        # same layer:
        self.seqend.dxf.layer = self.dxf.layer
        self.seqend.export_dxf(tagwriter)

    def destroy(self) -> None:
        """ Delete all data and references. """
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
        """ Returns ``True`` if scaling is uniform in x-, y- and z-axis ignoring
        reflections e.g. (1, 1, -1) is uniform scaling.

        """
        return abs(self.dxf.xscale) == abs(self.dxf.yscale) == abs(
            self.dxf.zscale)

    def set_scale(self, factor: float):
        """ Set uniform scaling. """
        if factor == 0:
            raise ValueError('Invalid scaling factor.')
        self.dxf.xscale = factor
        self.dxf.yscale = factor
        self.dxf.zscale = factor
        return self

    def is_xref(self) -> bool:
        """ Return ``True`` if XREF or XREF_OVERLAY. """
        assert self.doc is not None, 'Requires a document object'
        block_layout = self.doc.blocks.get(self.dxf.name)
        if block_layout is not None and block_layout.block.dxf.flags & 12:  # XREF(4) & XREF_OVERLAY(8)
            return True
        return False

    def block(self) -> Optional['BlockLayout']:
        """  Returns associated :class:`~ezdxf.layouts.BlockLayout`. """
        if self.doc is None:
            return None
        return self.doc.blocks.get(self.dxf.name)

    def place(self, insert: 'Vertex' = None,
              scale: Tuple[float, float, float] = None,
              rotation: float = None) -> 'Insert':
        """
        Set block reference placing location `insert`, scaling and rotation
        attributes. Parameters which are ``None`` will not be altered.

        Args:
            insert: insert location as ``(x, y [,z])`` tuple
            scale: ``(x-scale, y-scale, z-scale)`` tuple
            rotation : rotation angle in degrees

        """
        if insert is not None:
            self.dxf.insert = insert
        if scale is not None:
            if len(scale) != 3:
                raise DXFValueError(
                    "Parameter scale has to be a (x, y, z)-tuple."
                )
            x, y, z = scale
            self.dxf.xscale = x
            self.dxf.yscale = y
            self.dxf.zscale = z
        if rotation is not None:
            self.dxf.rotation = rotation
        return self

    def grid(self, size: Tuple[int, int] = (1, 1),
             spacing: Tuple[float, float] = (1, 1)) -> 'Insert':
        """ Place block reference in a grid layout, grid `size` defines the
        row- and column count, `spacing` defines the distance between two block
        references.

        Args:
            size: grid size as ``(row_count, column_count)`` tuple
            spacing: distance between placing as
                ``(row_spacing, column_spacing)`` tuple

        """
        try:
            rows, cols = size
        except ValueError:
            raise DXFValueError(
                "Size has to be a 2-tuple: (row_count, column_count)."
            )
        self.dxf.row_count = rows
        self.dxf.column_count = cols
        try:
            row_spacing, col_spacing = spacing
        except ValueError:
            raise DXFValueError(
                "Spacing has to be a 2-tuple: (row_spacing, column_spacing)."
            )
        self.dxf.row_spacing = row_spacing
        self.dxf.column_spacing = col_spacing
        return self

    def get_attrib(self, tag: str, search_const: bool = False) -> Optional[
        Union['Attrib', 'AttDef']]:
        """ Get attached :class:`Attrib` entity with :code:`dxf.tag == tag`,
        returns ``None`` if not found. Some applications may not attach constant
        ATTRIB entities, set `search_const` to ``True``, to get at least the
        associated :class:`AttDef` entity.

        Args:
            tag: tag name
            search_const: search also const ATTDEF entities

        """
        for attrib in self.attribs:
            if tag == attrib.dxf.tag:
                return attrib
        if search_const and self.doc is not None:
            block = self.doc.blocks[
                self.dxf.name]  # raises KeyError() if not found
            for attdef in block.get_const_attdefs():
                if tag == attdef.dxf.tag:
                    return attdef
        return None

    def get_attrib_text(self, tag: str, default: str = None,
                        search_const: bool = False) -> str:
        """ Get content text of attached :class:`Attrib` entity with
        :code:`dxf.tag == tag`, returns `default` if not found.
        Some applications may not attach constant ATTRIB entities, set
        `search_const` to ``True``, to get content text of the
        associated :class:`AttDef` entity.

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
        """ Returns ``True`` if ATTRIB `tag` exist, for `search_const` doc see
        :meth:`get_attrib`.

        Args:
            tag: tag name as string
            search_const: search also const ATTDEF entities

        """
        return self.get_attrib(tag, search_const) is not None

    def add_attrib(self, tag: str, text: str, insert: 'Vertex' = (0, 0),
                   dxfattribs: dict = None) -> 'Attrib':
        """ Attach an :class:`Attrib` entity to the block reference.

        Example for appending an attribute to an INSERT entity with none
        standard alignment::

            e.add_attrib('EXAMPLETAG', 'example text').set_pos(
                (3, 7), align='MIDDLE_CENTER'
            )

        Args:
            tag: tag name as string
            text: content text as string
            insert: insert location as tuple ``(x, y[, z])`` in :ref:`WCS`
            dxfattribs: additional DXF attributes for the ATTRIB entity

        """
        dxfattribs = dxfattribs or {}
        dxfattribs['tag'] = tag
        dxfattribs['text'] = text
        dxfattribs['insert'] = insert
        attrib = cast('Attrib', self._new_compound_entity('ATTRIB', dxfattribs))
        self.attribs.append(attrib)

        # This case is only possible if INSERT is read from file without
        # attached ATTRIBS:
        if self.seqend is None:
            self.new_seqend()
        return attrib

    def new_seqend(self):
        """ Create new ENDSEQ. (internal API)"""
        if self.doc:
            seqend = self.doc.dxffactory.create_db_entry('SEQEND', dxfattribs={
                'layer': self.dxf.layer})
        else:
            seqend = factory.new('SEQEND', dxfattribs={'layer': self.dxf.layer})
        self.link_seqend(seqend)

    def delete_attrib(self, tag: str, ignore=False) -> None:
        """ Delete an attached :class:`Attrib` entity from INSERT. If `ignore`
        is ``False``, an :class:`DXFKeyError` exception is raised, if
        ATTRIB `tag` does not exist.

        Args:
            tag: ATTRIB name
            ignore: ``False`` for raising :class:`DXFKeyError` if ATTRIB `tag`
                does not exist.

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

    def transform(self, m: 'Matrix44') -> 'Insert':
        """ Transform INSERT entity by transformation matrix `m` inplace.

        Unlike the transformation matrix `m`, the INSERT entity can not
        represent a non orthogonal target coordinate system, for this case an
        :class:`InsertTransformationError` will be raised.

        .. versionadded:: 0.13

        """

        dxf = self.dxf
        m1 = self.matrix44()

        # Transform scaled source axis into target coordinate system
        ux, uy, uz = m.transform_directions((m1.ux, m1.uy, m1.uz))

        # Get new scaling factors, all are positive:
        # z-axis is the real new z-axis, no reflection required
        # x-axis is the real new x-axis, no reflection required
        # y-axis - reflection is detected below
        z_scale = uz.magnitude
        x_scale = ux.magnitude
        y_scale = uy.magnitude

        # check for orthogonal x-, y- and z-axis
        ux = ux.normalize()
        uy = uy.normalize()
        uz = uz.normalize()
        if not (math.isclose(ux.dot(uz), 0.0, abs_tol=1e-9) and
                math.isclose(ux.dot(uy), 0.0, abs_tol=1e-9) and
                math.isclose(uz.dot(uy), 0.0, abs_tol=1e-9)):
            raise InsertTransformationError(NON_ORTHO_MSG)

        # expected y-axis for an orthogonal right handed coordinate system
        expected_uy = uz.cross(ux)
        if expected_uy.isclose(-uy, abs_tol=1e-9):
            # transformed y-axis points into opposite direction of the expected
            # y-axis:
            y_scale = -y_scale

        ocs = OCSTransform.from_ocs(OCS(dxf.extrusion), OCS(uz), m)
        dxf.insert = ocs.transform_vertex(dxf.insert)
        dxf.rotation = ocs.transform_deg_angle(dxf.rotation)

        dxf.extrusion = uz
        dxf.xscale = x_scale
        dxf.yscale = y_scale
        dxf.zscale = z_scale

        for attrib in self.attribs:
            attrib.transform(m)
        return self

    def translate(self, dx: float, dy: float, dz: float) -> 'Insert':
        """ Optimized INSERT translation about `dx` in x-axis, `dy` in y-axis
        and `dz` in z-axis.

        .. versionadded:: 0.13

        """
        ocs = self.ocs()
        self.dxf.insert = ocs.from_wcs(
            Vector(dx, dy, dz) + ocs.to_wcs(self.dxf.insert))
        for attrib in self.attribs:
            attrib.translate(dx, dy, dz)
        return self

    def matrix44(self) -> Matrix44:
        """ Returns a transformation :class:`Matrix44` object to transform block
        entities into WCS.

        .. versionadded:: 0.13

        """
        dxf = self.dxf
        sx = dxf.xscale
        sy = dxf.yscale
        sz = dxf.zscale

        ocs = self.ocs()
        extrusion = ocs.uz
        ux = Vector(ocs.to_wcs(X_AXIS))
        uy = Vector(ocs.to_wcs(Y_AXIS))
        m = Matrix44.ucs(ux=ux * sx, uy=uy * sy, uz=extrusion * sz)

        angle = math.radians(dxf.rotation)
        if angle != 0.0:
            m = Matrix44.chain(m, Matrix44.axis_rotate(extrusion, angle))

        insert = ocs.to_wcs(dxf.get('insert', Vector()))

        block_layout = self.block()
        if block_layout is not None:
            # transform block base point into WCS without translation
            insert -= m.transform_direction(block_layout.block.dxf.base_point)

        # set translation
        m.set_row(3, insert.xyz)
        return m

    def ucs(self):
        """ Returns the block reference coordinate system as
        :class:`ezdxf.math.UCS` object.
        """
        m = self.matrix44()
        ucs = UCS()
        ucs.matrix = m
        return ucs

    def reset_transformation(self) -> None:
        """ Reset block reference parameters `location`, `rotation` and
        `extrusion` vector.

        """
        self.dxf.insert = NULLVEC
        self.dxf.discard('rotation')
        self.dxf.discard('extrusion')

    def explode(self, target_layout: 'BaseLayout' = None,
                non_uniform_scaling=None) -> 'EntityQuery':
        """
        Explode block reference entities into target layout, if target layout is
        ``None``, the target layout is the layout of the block reference.

        Transforms the block entities into the required :ref:`WCS` location by
        applying the block reference attributes `insert`, `extrusion`,
        `rotation` and the scaling values `xscale`, `yscale` and `zscale`.

        Attached ATTRIB entities are converted to TEXT entities, this is the
        behavior of the BURST command of the AutoCAD Express Tools.

        Returns an :class:`~ezdxf.query.EntityQuery` container with all
        "exploded" DXF entities.

        .. warning::

            **Non uniform scaling** may lead to incorrect results for text
            entities (TEXT, MTEXT, ATTRIB) and maybe some other entities.

        Args:
            target_layout: target layout for exploded entities, ``None`` for
            same layout as source entity.

        .. versionchanged:: 0.13
            deprecated `non_uniform_scaling` argument

        """
        if target_layout is None:
            target_layout = self.get_layout()
            if target_layout is None:
                raise DXFStructureError(
                    'INSERT without layout assigment, specify target layout.'
                )
        if non_uniform_scaling is not None:
            warnings.warn(
                'Insert.explode() argument `non_uniform_scaling` is deprecated'
                ' (removed in v0.15).',
                DeprecationWarning
            )
        return explode_block_reference(self, target_layout=target_layout)

    def virtual_entities(self,
                         non_uniform_scaling=None,
                         skipped_entity_callback: Optional[
                             Callable[[DXFGraphic, str], None]] = None
                         ) -> Iterable[DXFGraphic]:
        """
        Yields "virtual" entities of a block reference. This method is meant to
        examine the block reference entities at the "exploded" location without
        really "exploding" the block reference. The`skipped_entity_callback()`
        will be called for all entities which are not processed, signature:
        :code:`skipped_entity_callback(entity: DXFEntity, reason: str)`,
        `entity` is the original (untransformed) DXF entity of the block
        definition, the `reason` string is an explanation why the entity was
        skipped.

        This entities are not stored in the entity database, have no handle and
        are not assigned to any layout. It is possible to convert this entities
        into regular drawing entities by adding the entities to the entities
        database and a layout of the same DXF document as the block reference::

            doc.entitydb.add(entity)
            msp = doc.modelspace()
            msp.add_entity(entity)

        This method does not resolve the MINSERT attributes, only the
        sub-entities of the base INSERT will be returned. To resolve MINSERT
        entities check if multi insert processing is required, that's the case
        if property :attr:`Insert.mcount` > 1, use the :meth:`Insert.multi_insert`
        method to resolve the MINSERT entity into single INSERT entities.

        .. warning::

            **Non uniform scaling** may return incorrect results for text
            entities (TEXT, MTEXT, ATTRIB) and maybe some other entities.

        Args:
            skipped_entity_callback: called whenever the transformation of an
                entity is not supported and so was skipped

        .. versionchanged:: 0.13
            deprecated `non_uniform_scaling` argument

        """
        if non_uniform_scaling is not None:
            warnings.warn(
                'Insert.virtual_entities() argument `non_uniform_scaling` is'
                ' deprecated (removed in v0.15).',
                DeprecationWarning
            )
        return virtual_block_reference_entities(
            self, skipped_entity_callback=skipped_entity_callback)

    @property
    def mcount(self):
        """ Returns the multi-insert count, MINSERT (multi-insert) processing
        is required if :attr:`mcount` > 1.

        .. versionadded:: 0.14

        """
        return (self.dxf.row_count if self.dxf.row_spacing else 1) * (
            self.dxf.column_count if self.dxf.column_spacing else 1)

    def multi_insert(self) -> Iterable['Insert']:
        """ Yields a virtual INSERT entity for each grid element of a MINSERT
        entity (multi-insert).

        .. versionadded:: 0.14

        """
        def transform_attached_attrib_entities(insert, offset):
            for attrib in insert.attribs:
                attrib.dxf.insert += offset

        def adjust_dxf_attribs(insert, offset):
            dxf = insert.dxf
            dxf.insert += offset
            dxf.discard('row_count')
            dxf.discard('column_count')
            dxf.discard('row_spacing')
            dxf.discard('column_spacing')

        done = set()
        row_spacing = self.dxf.row_spacing
        col_spacing = self.dxf.column_spacing
        rotation = self.dxf.rotation
        for row in range(self.dxf.row_count):
            for col in range(self.dxf.column_count):
                # All transformations in OCS:
                offset = Vector(col * col_spacing, row * row_spacing)
                # If any spacing is 0, yield only unique locations:
                if offset not in done:
                    done.add(offset)
                    if rotation:  # Apply rotation to the grid.
                        offset = offset.rotate_deg(rotation)
                    # Do not apply scaling to the grid!
                    insert = self.copy()
                    adjust_dxf_attribs(insert, offset)
                    transform_attached_attrib_entities(insert, offset)
                    yield insert

    def add_auto_attribs(self, values: Dict[str, str]) -> 'Insert':
        """
        Attach for each :class:`~ezdxf.entities.Attdef` entity, defined in the
        block definition, automatically an :class:`Attrib` entity to the block
        reference and set ``tag/value`` DXF attributes of the ATTRIB entities
        by the ``key/value`` pairs (both as strings) of the `values` dict.
        The ATTRIB entities are placed relative to the insert location of the
        block reference, which is identical to the block base point.

        This method avoids the wrapper block of the
        :meth:`~ezdxf.layouts.BaseLayout.add_auto_blockref` method, but the
        visual results may not match the results of CAD applications, especially
        for non uniform scaling. If the visual result is very important to you,
        use the :meth:`add_auto_blockref` method.

        Args:
            values: :class:`~ezdxf.entities.Attrib` tag values as ``tag/value``
                pairs

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
                attrib.transform(m)

        m = self.matrix44()
        blockdef = self.block()
        autofill()
        return self

    def audit(self, auditor: 'Auditor') -> None:
        """ Validity check. """
        super().audit(auditor)
        doc = self.doc
        if doc and doc.blocks:
            if self.dxf.name not in doc.blocks:
                auditor.fixed_error(
                    code=AuditError.UNDEFINED_BLOCK,
                    message=f'Deleted entity {str(self)} without required BLOCK'
                            f' definition.',
                )
                if auditor.has_trashcan:
                    auditor.trash(self.dxf.handle)
                else:
                    self.destroy()
