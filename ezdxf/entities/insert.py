# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-16
from typing import TYPE_CHECKING, Iterable, cast, Tuple, Union, Optional, List
from ezdxf.math import Vector
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER, DXFValueError, DXFKeyError
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity, SeqEnd
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Vertex, DXFNamespace, DXFEntity, Drawing, Attrib, AttDef

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
        """ Copy ATTRIB entities, and store the copies into database. """
        entity.attribs = [attrib.copy() for attrib in self.attribs]
        entity.seqend = self.seqend.copy()

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
        self.entitydb.delete_entity(self.seqend)
        super().destroy()

    def place(self, insert: 'Vertex' = None,
              scale: Tuple[float, float, float] = None,
              rotation: float = None) -> 'Insert':
        """
        Set placing attributes of the INSERT entity.

        Args:
            insert: insert position as (x, y [,z]) tuple
            scale: (scale_x, scale_y, scale_z) tuple
            rotation (float): rotation angle in degrees

        Returns:
            Insert object (fluent interface)

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
        Set grid placing attributes of the INSERT entity.

        Args:
            size: grid size as (row_count, column_count) tuple
            spacing: distance between placing as (row_spacing, column_spacing) tuple

        Returns:
            Insert object (fluent interface)

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
        Get attached ATTRIB entity by `tag`.

        Args:
            tag: tag name
            search_const: search also const ATTDEF entities

        Returns:
            Attrib or Attdef object

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
        Get content text of attached ATTRIB entity `tag`.

        Args:
            tag: tag name
            default: default value if tag is absent
            search_const: search also const ATTDEF entities

        Returns:
            content text as str

        """
        attrib = self.get_attrib(tag, search_const)
        if attrib is None:
            return default
        return attrib.dxf.text

    def has_attrib(self, tag: str, search_const: bool = False) -> bool:
        """
        Check if ATTRIB for *tag* exists.

        Args:
            tag: tag name
            search_const: search also const ATTDEF entities

        """
        return self.get_attrib(tag, search_const) is not None

    def add_attrib(self, tag: str, text: str, insert: 'Vertex' = (0, 0), dxfattribs: dict = None) -> 'Attrib':
        """
        Add new ATTRIB entity.

        Args:
            tag: tag name
            text: content text
            insert: insert position as tuple (x, y[, z])
            dxfattribs: additional DXF attributes

        Returns:
            Attrib object

        """
        dxfattribs = dxfattribs or {}
        dxfattribs['tag'] = tag
        dxfattribs['text'] = text
        dxfattribs['insert'] = insert
        attrib = cast('Attrib', self._new_compound_entity('ATTRIB', dxfattribs))
        self.attribs.append(attrib)
        return attrib

    def delete_attrib(self, tag: str, ignore=False) -> None:
        """
        Delete attached ATTRIB entity `tag`, raises a KeyError exception if `tag` does not exist, set `ignore` to True,
        to ignore not existing ATTRIB entities.

        Args:
            tag: ATTRIB name
            ignore: False -> raise KeyError exception if `tag` does not exist

        """
        for index, attrib in enumerate(self.attribs):
            if attrib.dxf.tag == tag:
                del self.attribs[index]
                self.entitydb.delete_entity(attrib)
                return
        if not ignore:
            raise DXFKeyError(tag)

    def delete_all_attribs(self) -> None:
        """ Delete all ATTRIB entities attached to the INSERT entity. """
        db = self.entitydb
        for attrib in self.attribs:
            db.delete_entity(attrib)
        self.attribs = []
