# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Optional, Union
import copy
from ezdxf.lldxf import validator
from ezdxf.math import NULLVEC
from ezdxf.lldxf.attributes import (
    DXFAttr, DXFAttributes, DefSubclass, XType, RETURN_DEFAULT,
    group_code_mapping,
)
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER, DXF2010
from ezdxf.lldxf import const
from ezdxf.tools import set_flag_state
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import acdb_entity, elevation_to_z_axis
from .text import Text, acdb_text, acdb_text_group_codes
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Tags, DXFNamespace, DXFEntity

__all__ = ['AttDef', 'Attrib', 'copy_attrib_as_text']

# DXF Reference for ATTRIB is a total mess and incorrect, the AcDbText subclass
# for the ATTRIB entity is the same as for the TEXT entity, but the valign field
# from the 2nd AcDbText subclass of the TEXT entity is stored in the
# AcDbAttribute subclass:
attrib_fields = {
    # Version number: 0 = 2010
    'version': DXFAttr(280, default=0, dxfversion=DXF2010),

    # Tag string (cannot contain spaces):
    'tag': DXFAttr(
        2, default='',
        validator=validator.is_valid_attrib_tag,
        fixer=validator.fix_attrib_tag,
    ),

    # 1 = Attribute is invisible (does not appear)
    # 2 = This is a constant attribute
    # 4 = Verification is required on input of this attribute
    # 8 = Attribute is preset (no prompt during insertion)
    'flags': DXFAttr(70, default=0),

    # Field length (optional) (not currently used)
    'field_length': DXFAttr(73, default=0, optional=True),

    # Vertical text justification type (optional); see group code 73 in TEXT
    'valign': DXFAttr(
        74, default=0, optional=True,
        validator=validator.is_in_integer_range(0, 4),
        fixer=RETURN_DEFAULT,
    ),

    # Lock position flag. Locks the position of the attribute within the block
    # reference, example of double use of group codes in one sub class
    'lock_position': DXFAttr(
        280, default=0, dxfversion=DXF2010, optional=True,
        validator=validator.is_integer_bool,
        fixer=RETURN_DEFAULT,
    ),
}

# ATTDEF has an additional field: 'prompt'
# DXF attribute definitions are immutable, a shallow copy is sufficient:
attdef_fields = dict(attrib_fields)
attdef_fields['prompt'] = DXFAttr(
    3, default='',
    validator=validator.is_valid_one_line_text,
    fixer=validator.fix_one_line_text,
)

acdb_attdef = DefSubclass('AcDbAttributeDefinition', attdef_fields)
acdb_attdef_group_codes = group_code_mapping(acdb_attdef)
acdb_attrib = DefSubclass('AcDbAttribute', attrib_fields)
acdb_attrib_group_codes = group_code_mapping(acdb_attrib)

# For XRECORD the tag order is important and group codes appear multiple times,
# therefore this attribute definition needs a special treatment!
acdb_attdef_xrecord = DefSubclass('AcDbXrecord', [
    # Duplicate record cloning flag (determines how to merge duplicate entries):
    # 1 = Keep existing
    ('cloning', DXFAttr(280, default=1)),

    # MText flag:
    # 2 = multiline attribute
    # 4 = constant multiline attribute definition
    ('mtext_flag', DXFAttr(70, default=0)),

    # isReallyLocked flag:
    #     0 = unlocked
    #     1 = locked
    ('really_locked', DXFAttr(
        70, default=0,
        validator=validator.is_integer_bool,
        fixer=RETURN_DEFAULT,
    )),

    # Number of secondary attributes or attribute definitions:
    ('secondary_attribs_count', DXFAttr(70, default=0)),
    # Hard-pointer id of secondary attribute(s) or attribute definition(s):
    ('secondary_attribs_handle', DXFAttr(70, default=0)),

    # Alignment point of attribute or attribute definition:
    ('align_point', DXFAttr(10, xtype=XType.point3d, default=NULLVEC)),
    ('current_annotation_scale', DXFAttr(40, default=0)),

    # attribute or attribute definition tag string
    ('tag', DXFAttr(
        2, default='',
        validator=validator.is_valid_attrib_tag,
        fixer=validator.fix_attrib_tag,
    )),
])


# A special MTEXT entity can follow the ATTDEF and ATTRIB entity, which starts
# as a usual DXF entity with (0, 'MTEXT'), so processing can't be done here,
# because for ezdxf is this a separated Entity.
#
# The attached MTEXT entity: owner is None and handle is None
# Linked as attribute `attached_mtext`.
# I don't have seen this combination of entities in real world examples and is
# ignored by ezdxf for now.

# Attrib and Attdef can have embedded MTEXT entities located in the
# <Embedded Object> subclass, see issue #258

# QUESTION: How are the attached MTEXT and the embedded MTEXT related?

class BaseAttrib(Text):
    XRECORD_DEF = acdb_attdef_xrecord

    def __init__(self):
        """ Default constructor """
        super().__init__()
        # TODO: implement embedded MTEXT support
        #  remove DXFEntity.embedded_objects if done
        self.xrecord: Optional['Tags'] = None
        self.attached_mtext: Optional['DXFEntity'] = None

    def _copy_data(self, entity: 'BaseAttrib') -> None:
        """ Copy entity data, xrecord data and attached MTEXT are not stored
        in the entity database.

        """
        entity.xrecord = copy.deepcopy(self.xrecord)
        if self.attached_mtext:
            entity.attached_mtext = self.attached_mtext.copy()
            # attached mtext entity is not stored in the entity database
            # no further action required

    def link_entity(self, entity: 'DXFEntity'):
        self.attached_mtext = entity

    def export_dxf(self, tagwriter: 'TagWriter'):
        """ Export attached MTEXT entity. """
        super().export_dxf(tagwriter)
        if self.attached_mtext:
            # todo: export MTEXT attached to ATTRIB
            # Attached MTEXT has no handle and owner and can not exported
            # by the usual export process:
            # self.attached_mtext.export_dxf(tagwriter)
            raise NotImplemented('Attached MTEXT export')

    @property
    def is_const(self) -> bool:
        """ This is a constant attribute. """
        return bool(self.dxf.flags & const.ATTRIB_CONST)

    @is_const.setter
    def is_const(self, state: bool) -> None:
        """ This is a constant attribute. """
        self.dxf.flags = set_flag_state(self.dxf.flags, const.ATTRIB_CONST,
                                        state)

    @property
    def is_invisible(self) -> bool:
        """ Attribute is invisible (does not appear). """
        return bool(self.dxf.flags & const.ATTRIB_INVISIBLE)

    @is_invisible.setter
    def is_invisible(self, state: bool) -> None:
        """ Attribute is invisible (does not appear). """
        self.dxf.flags = set_flag_state(self.dxf.flags, const.ATTRIB_INVISIBLE,
                                        state)

    @property
    def is_verify(self) -> bool:
        """ Verification is required on input of this attribute.
        (CAD application feature)

        """
        return bool(self.dxf.flags & const.ATTRIB_VERIFY)

    @is_verify.setter
    def is_verify(self, state: bool) -> None:
        """ Verification is required on input of this attribute.
        (CAD application feature)

        """
        self.dxf.flags = set_flag_state(self.dxf.flags, const.ATTRIB_VERIFY,
                                        state)

    @property
    def is_preset(self) -> bool:
        """ No prompt during insertion. (CAD application feature) """
        return bool(self.dxf.flags & const.ATTRIB_IS_PRESET)

    @is_preset.setter
    def is_preset(self, state: bool) -> None:
        """ No prompt during insertion. (CAD application feature) """
        self.dxf.flags = set_flag_state(self.dxf.flags, const.ATTRIB_IS_PRESET,
                                        state)


@register_entity
class AttDef(BaseAttrib):
    """ DXF ATTDEF entity """
    DXFTYPE = 'ATTDEF'
    # Don't add acdb_attdef_xrecord here:
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_text, acdb_attdef)

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super(Text, self).load_dxf_attribs(processor)
        # Do not call Text loader.
        if processor:
            processor.fast_load_dxfattribs(
                dxf, acdb_text_group_codes, 2, recover=True)
            processor.fast_load_dxfattribs(
                dxf, acdb_attdef_group_codes, 3, recover=True)
            self.xrecord = processor.find_subclass(self.XRECORD_DEF.name)
            if processor.r12:
                # Transform elevation attribute from R11 to z-axis values:
                elevation_to_z_axis(dxf, ('insert', 'align_point'))

        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        # Text() writes 2x AcDbText which is not suitable for AttDef()
        self.export_acdb_entity(tagwriter)
        self.export_acdb_text(tagwriter)
        self.export_acdb_attdef(tagwriter)
        if self.xrecord:
            tagwriter.write_tags(self.xrecord)

    def export_acdb_attdef(self, tagwriter: 'TagWriter') -> None:
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_attdef.name)
        self.dxf.export_dxf_attribs(tagwriter, [
            'version', 'prompt', 'tag', 'flags', 'field_length', 'valign',
            'lock_position',
        ])


@register_entity
class Attrib(BaseAttrib):
    """ DXF ATTRIB entity """

    DXFTYPE = 'ATTRIB'
    # Don't add acdb_attdef_xrecord here:
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_text, acdb_attrib)

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super(Text, self).load_dxf_attribs(processor)
        # Do not call Text loader.
        if processor:
            processor.fast_load_dxfattribs(
                dxf, acdb_text_group_codes, 2, recover=True)
            processor.fast_load_dxfattribs(
                dxf, acdb_attrib_group_codes, 3, recover=True)
            self.xrecord = processor.find_subclass(self.XRECORD_DEF.name)
            if processor.r12:
                # Transform elevation attribute from R11 to z-axis values:
                elevation_to_z_axis(dxf, ('insert', 'align_point'))
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        # Text() writes 2x AcDbText which is not suitable for AttDef()
        self.export_acdb_entity(tagwriter)
        self.export_acdb_attrib_text(tagwriter)
        self.export_acdb_attrib(tagwriter)
        if self.xrecord:
            tagwriter.write_tags(self.xrecord)

    def export_acdb_attrib_text(self, tagwriter: 'TagWriter') -> None:
        # Despite the similarities to TEXT, it is different to
        # Text.export_acdb_text():
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_text.name)
        self.dxf.export_dxf_attribs(tagwriter, [
            'insert', 'height', 'text', 'thickness', 'rotation', 'oblique',
            'style', 'width', 'halign', 'align_point', 'text_generation_flag',
            'extrusion',
        ])

    def export_acdb_attrib(self, tagwriter: 'TagWriter') -> None:
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_attrib.name)
        self.dxf.export_dxf_attribs(tagwriter, [
            'version', 'tag', 'flags', 'field_length', 'valign',
            'lock_position',
        ])


IGNORE_FROM_ATTRIB = {
    'handle', 'owner', 'version', 'prompt', 'tag', 'flags', 'field_length',
    'lock_position'
}


def copy_attrib_as_text(attrib: BaseAttrib):
    """ Returns the content of the ATTRIB/ATTDEF entity as a new virtual TEXT
    entity.

    """
    # TODO: MTEXT feature of DXF R2018+ is not supported yet!
    dxfattribs = attrib.dxfattribs(drop=IGNORE_FROM_ATTRIB)
    return Text.new(dxfattribs=dxfattribs, doc=attrib.doc)
