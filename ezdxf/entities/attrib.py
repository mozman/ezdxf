# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-15
from typing import TYPE_CHECKING
import copy
from ezdxf.math import Vector
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER, DXF2010
from ezdxf.lldxf import const
from ezdxf.tools import set_flag_state
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import acdb_entity
from .text import Text, acdb_text
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Tags
    from .dxfentity import DXFNamespace, DXFEntity
    from ezdxf.drawing2 import Drawing

__all__ = ['AttDef', 'Attrib']

acdb_attdef = DefSubclass('AcDbAttributeDefinition', {
    'version': DXFAttr(280, default=0, dxfversion=DXF2010),  # Version number: 0 = 2010
    'prompt': DXFAttr(3, default=''),  # Prompt string
    'tag': DXFAttr(2, default=''),  # Tag string (cannot contain spaces)
    'flags': DXFAttr(70, default=0),
    # 1 = Attribute is invisible (does not appear)
    # 2 = This is a constant attribute
    # 4 = Verification is required on input of this attribute
    # 8 = Attribute is preset (no prompt during insertion)
    'field_length': DXFAttr(73, default=0, optional=True),  # Field length (optional) (not currently used)
    'valign': DXFAttr(74, default=0, optional=True),
    # Vertical text justification type (optional); see group code 73 in TEXT
    # Lock position flag. Locks the position of the attribute within the block reference
    # example of double use of group codes in one sub class
    'lock_position': DXFAttr(280, default=0, dxfversion=DXF2010),
})

# in xrecord definition, order is important, and group codes appear multiple times
# this attribute definition needs a special treatment!
acdb_attdef_xrecord = DefSubclass('AcDbXrecord', [
    ('cloning', DXFAttr(280, default=1)),  # Duplicate record cloning flag (determines how to merge duplicate entries):
    # 1 = Keep existing
    ('mtext_flag', DXFAttr(70, default=0)),  # MText flag:
    # 2 = multiline attribute
    # 4 = constant multiline attribute definition
    ('really_locked', DXFAttr(70, default=0)),  # isReallyLocked flag:
    #     0 = unlocked
    #     1 = locked
    ('secondary_attribs_count', DXFAttr(70, default=0)),  # Number of secondary attributes or attribute definitions
    ('secondary_attribs_handle', DXFAttr(70, default=0)),
    # hard-pointer id of secondary attribute(s) or attribute definition(s)
    ('align_point', DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0))),
    # Alignment point of attribute or attribute definition
    ('current_annotation_scale', DXFAttr(40, default=0)),  # current annotation scale
    ('tag', DXFAttr(2, default='')),  # attribute or attribute definition tag string
])


# ---------------------------------------------------------------------------------------------------------------------
# A special MTEXT entity can follow the ATTDEF and ATTRIB entity, which starts as a usual DXF entity with (0, 'MTEXT'),
# so processing can't be done here, because for ezdxf is this a separated Entity.
#
# Differentiation of this special MTEXT and a usual MTEXT entity could be done by handle and owner tag,
# the special tag has both set to None. One approach could be to link this MTEXT entity to the ATTDEF or ATTRIB
# entity, for now I don't have seen this combination of entities in real world examples and is ignored by ezdxf for
# now.
# ---------------------------------------------------------------------------------------------------------------------


class BaseAttrib(Text):
    XRECORD_DEF = acdb_attdef_xrecord

    def __init__(self, doc: 'Drawing' = None):
        """ Default constructor """
        super().__init__(doc)
        self.xrecord = None  # type: Tags
        self.attached_mtext = None  # type: DXFEntity

    def _clone_data(self, entity: 'BaseAttrib') -> None:
        """ Clone entity data, xrecord data and attached MTEXT are not stored in the entity database. """
        entity.xrecord = copy.deepcopy(self.xrecord)
        entity.attached_mtext = self.attached_mtext.clone()

    def link_entity(self, entity: 'DXFEntity'):
        self.attached_mtext = entity

    def export_attached_mtext(self, tagwriter: 'TagWriter') -> None:
        raise NotImplementedError()

    @property
    def is_const(self) -> bool:
        """
        This is a constant attribute.
        """
        return bool(self.dxf.flags & const.ATTRIB_CONST)

    @is_const.setter
    def is_const(self, state: bool) -> None:
        """
        This is a constant attribute.
        """
        self.dxf.flags = set_flag_state(self.dxf.flags, const.ATTRIB_CONST, state)

    @property
    def is_invisible(self) -> bool:
        """
        Attribute is invisible (does not appear).
        """
        return bool(self.dxf.flags & const.ATTRIB_INVISIBLE)

    @is_invisible.setter
    def is_invisible(self, state: bool) -> None:
        """
        Attribute is invisible (does not appear).
        """
        self.dxf.flags = set_flag_state(self.dxf.flags, const.ATTRIB_INVISIBLE, state)

    @property
    def is_verify(self) -> bool:
        """
        Verification is required on input of this attribute. (CAD application feature)
        """
        return bool(self.dxf.flags & const.ATTRIB_VERIFY)

    @is_verify.setter
    def is_verify(self, state: bool) -> None:
        """
        Verification is required on input of this attribute. (CAD application feature)
        """
        self.dxf.flags = set_flag_state(self.dxf.flags, const.ATTRIB_VERIFY, state)


    @property
    def is_preset(self) -> bool:
        """
        No prompt during insertion. (CAD application feature)
        """
        return bool(self.dxf.flags & const.ATTRIB_IS_PRESET)

    @is_preset.setter
    def is_preset(self, state: bool) -> None:
        """
        No prompt during insertion. (CAD application feature)
        """
        self.dxf.flags = set_flag_state(self.dxf.flags, const.ATTRIB_IS_PRESET, state)


@register_entity
class AttDef(BaseAttrib):
    """ DXF ATTDEF entity """
    DXFTYPE = 'ATTDEF'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_text, acdb_attdef)  # don't add acdb_attdef_xrecord here

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        # acdb_text processing is done by super class
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_attdef)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, subclass=acdb_attdef.name)
            self.xrecord = processor.find_subclass(self.XRECORD_DEF.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        # Text() writes 2x AcDbText which is not suitable for AttDef() and Attrib()
        # base class export is done by parent class
        self.export_acdb_entity(tagwriter)
        self.export_acdb_text(tagwriter)  # does not write valign!
        self.export_acdb_attdef(tagwriter)
        if self.xrecord:
            tagwriter.write_tags(self.xrecord)
        if self.attached_mtext:
            self.export_attached_mtext(tagwriter)

    def export_acdb_attdef(self, tagwriter: 'TagWriter') -> None:
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_attdef.name)
        # for all DXF versions
        self.dxf.export_dxf_attribs(tagwriter, [
            'version', 'prompt', 'tag', 'flags', 'field_length', 'valign', 'lock_position',
        ])


# copy AcDbText subclass definition
acdb_attrib_text = DefSubclass('AcDbText', dict(acdb_text.attribs))
# remove 'text_generation_flag', because ATTRIB has 'text_generation_flag' in subclass AcDbAttribute
del acdb_attrib_text.attribs['text_generation_flag']

# DXF Reference for ATTRIB is a total mess and incorrect
acdb_attrib = DefSubclass('AcDbAttribute', {
    'version': DXFAttr(280, default=0, dxfversion=DXF2010),  # Version number: 0 = 2010
    'tag': DXFAttr(2, default=''),  # Tag string (cannot contain spaces)
    'flags': DXFAttr(70, default=0),
    # comes from AcDbText - what a mess
    'text_generation_flag': DXFAttr(71, default=0, optional=True),  # Text generation flags (optional)
    # 1 = Attribute is invisible (does not appear)
    # 2 = This is a constant attribute
    # 4 = Verification is required on input of this attribute
    # 8 = Attribute is preset (no prompt during insertion)
    'field_length': DXFAttr(73, default=0, optional=True),  # Field length (optional) (not currently used)
    # Vertical text justification type (optional); see group code 73 in TEXT
    'valign': DXFAttr(74, default=0, optional=True),
    # Lock position flag. Locks the position of the attribute within the block reference
    # example of double use of group codes in one sub class
    'lock_position': DXFAttr(280, default=0, dxfversion=DXF2010),
})


@register_entity
class Attrib(BaseAttrib):
    """ DXF ATTRIB entity """

    DXFTYPE = 'ATTRIB'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_attrib_text, acdb_attrib)  # don't add acdb_attdef_xrecord here

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        # acdb_text processing is done by super class
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_attrib)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, subclass=acdb_attrib.name)
            self.xrecord = processor.find_subclass(self.XRECORD_DEF.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        # Text() writes 2x AcDbText which is not suitable for AttDef() and Attrib()
        # base class export is done by parent class
        self.export_acdb_entity(tagwriter)
        self.export_acdb_attrib_text(tagwriter)
        self.export_acdb_attrib(tagwriter)
        if self.xrecord:
            tagwriter.write_tags(self.xrecord)
        if self.attached_mtext:
            self.export_attached_mtext(tagwriter)

    def export_acdb_attrib_text(self, tagwriter: 'TagWriter') -> None:
        # difference to export_acdb_text(): do not export 'text_generation_flag'
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_attrib_text.name)
        # for all DXF versions
        self.dxf.export_dxf_attribs(tagwriter, [
            'insert', 'height', 'text', 'thickness', 'rotation', 'oblique', 'style', 'width',
            'halign', 'align_point', 'extrusion'
        ])

    def export_acdb_attrib(self, tagwriter: 'TagWriter') -> None:
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_attrib.name)
        # for all DXF versions
        self.dxf.export_dxf_attribs(tagwriter, [
            'version', 'tag', 'flags',  'text_generation_flag', 'field_length', 'valign', 'lock_position',
        ])
