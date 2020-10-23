# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Any, Optional, Union, Iterable, List, TYPE_CHECKING
import logging
from ezdxf import options
from ezdxf.lldxf import const
from ezdxf.lldxf.attributes import XType, DXFAttributes, DefSubclass, DXFAttr
from ezdxf.lldxf.types import handle_code, cast_value, dxftag
from ezdxf.lldxf.tags import Tags

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import ExtendedTags, DXFEntity, TagWriter

__all__ = ['DXFNamespace', 'SubclassProcessor']

ERR_INVALID_DXF_ATTRIB = 'Invalid DXF attribute "{}" for entity {}'
ERR_DXF_ATTRIB_NOT_EXITS = 'DXF attribute "{}" does not exist'

# supported event handler called by setting DXF attributes
# for usage, implement a method named like the dict-value, that accepts the new
# value as argument e.g.:
#   Polyline.on_layer_change(name) -> changes also layers of all vertices

SETTER_EVENTS = {
    'layer': 'on_layer_change',
    'linetype': 'on_linetype_change',
    'style': 'on_style_change',
    'dimstyle': 'on_dimstyle_change',
}


class DXFNamespace:
    """ :class:`DXFNamespace` manages all named DXF attributes of an entity.

    The DXFNamespace.__dict__ is used as DXF attribute storage, therefore only
    valid Python names can be used as attrib name.

    The namespace can only contain immutable objects: string, int, float, bool,
    Vector. Because of the immutability, copy and deepcopy are the same.

    (internal class)
    """

    def __init__(self, processor: 'SubclassProcessor' = None,
                 entity: 'DXFEntity' = None):
        if processor:
            base_class_ = processor.base_class
            code = handle_code(base_class_[0].value)
            # CLASS entity has no handle and TABLE also has no handle if
            # loaded from DXF R12 file
            handle = base_class_.get_first_value(code, None)
            # owner is None if loaded from DXF R12 file
            owner = base_class_.get_first_value(330, None)
            self.rewire(entity, handle, owner)
        else:
            self.reset_handles()
            self.rewire(entity)

    def copy(self, entity: 'DXFEntity'):
        namespace = self.__class__()
        for k, v in self.__dict__.items():
            namespace.__dict__[k] = v
        namespace.rewire(entity)
        return namespace

    def __deepcopy__(self, memodict: dict = None):
        return self.copy(self._entity)

    def reset_handles(self):
        """ Reset handle and owner to None. """
        self.__dict__['handle'] = None
        self.__dict__['owner'] = None

    def rewire(self, entity: 'DXFEntity', handle: str = None,
               owner: str = None) -> None:
        """ Rewire DXF namespace with parent entity

        Args:
            entity: new associated entity
            handle: new handle or None
            owner:  new entity owner handle or None

        """
        # bypass __setattr__()
        self.__dict__['_entity'] = entity
        if handle is not None:
            self.__dict__['handle'] = handle
        if owner is not None:
            self.__dict__['owner'] = owner

    def __getattr__(self, key: str) -> Any:
        """ Called if DXF attribute `key` does not exist, returns the DXF
        default value or ``None``.

        Raises:
            DXFAttributeError: attribute `key` is not supported

        """
        attrib_def: Optional[DXFAttr] = self.dxfattribs.get(key)
        if attrib_def:
            if attrib_def.xtype == XType.callback:
                return attrib_def.get_callback_value(self._entity)
            else:
                return attrib_def.default
        else:
            raise const.DXFAttributeError(
                ERR_INVALID_DXF_ATTRIB.format(key, self.dxftype)
            )

    def __setattr__(self, key: str, value: Any) -> None:
        """ Set DXF attribute `key` to `value`.

        Raises:
            DXFAttributeError: attribute `key` is not supported

        """

        def check(value):
            value = cast_value(attrib_def.code, value)
            if not attrib_def.is_valid_value(value):
                if attrib_def.fixer:
                    value = attrib_def.fixer(value)
                    logger.debug(
                        f'Fixed invalid attribute "{key}" in entity'
                        f' {str(self._entity)} to "{str(value)}".'
                    )
                else:
                    raise const.DXFValueError(
                        f'Invalid value {str(value)} for attribute "{key}" in '
                        f'entity {str(self._entity)}.'
                    )
            return value

        attrib_def: Optional['DXFAttr'] = self.dxfattribs.get(key)
        if attrib_def:
            if attrib_def.xtype == XType.callback:
                attrib_def.set_callback_value(self._entity, value)
            else:
                self.__dict__[key] = check(value)
        else:
            raise const.DXFAttributeError(
                ERR_INVALID_DXF_ATTRIB.format(key, self.dxftype))

        if key in SETTER_EVENTS:
            handler = getattr(self._entity, SETTER_EVENTS[key], None)
            if handler:
                handler(value)

    def __delattr__(self, key: str) -> None:
        """ Delete DXF attribute `key`.

        Raises:
            DXFAttributeError: attribute `key` does not exist

        """
        if self.hasattr(key):
            del self.__dict__[key]
        else:
            raise const.DXFAttributeError(ERR_DXF_ATTRIB_NOT_EXITS.format(key))

    def get(self, key: str, default: Any = None) -> Any:
        """ Returns value of DXF attribute `key` or the given `default` value
        not DXF default value for unset attributes.

        Raises:
            DXFAttributeError: attribute `key` is not supported

        """
        # callback values should not exist as attribute in __dict__
        if self.hasattr(key):
            # do not return the DXF default value
            return self.__dict__[key]
        attrib_def: Optional['DXFAttr'] = self.dxfattribs.get(key)
        if attrib_def:
            if attrib_def.xtype == XType.callback:
                return attrib_def.get_callback_value(self._entity)
            else:
                return default  # return give default
        else:
            raise const.DXFAttributeError(
                ERR_INVALID_DXF_ATTRIB.format(key, self.dxftype))

    def get_default(self, key: str) -> Any:
        """ Returns DXF default value for unset DXF attribute `key`. """
        value = self.get(key, None)
        return self.dxf_default_value(key) if value is None else value

    def set(self, key: str, value: Any) -> None:
        """ Set DXF attribute `key` to `value`.

        Raises:
            DXFAttributeError: attribute `key` is not supported

        """
        self.__setattr__(key, value)

    def all_existing_dxf_attribs(self) -> dict:
        """ Returns all existing DXF attributes, except DXFEntity parent link.
        """
        attribs = dict(self.__dict__)
        del attribs['_entity']
        return attribs

    def discard(self, key: str) -> None:
        """ Delete DXF attribute `key` silently without any exception. """
        try:
            del self.__dict__[key]
        except KeyError:
            pass

    def is_supported(self, key: str) -> bool:
        """ Returns True if DXF attribute `key` is supported else False.
        Does not grant that attribute `key` really exists and does not
        check if the actual DXF version of the document supports this
        attribute, unsupported attributes will be ignored at export.

        """
        return key in self.dxfattribs

    def hasattr(self, key: str) -> bool:
        """ Returns True if attribute `key` really exists else False. """
        return key in self.__dict__

    @property
    def dxftype(self) -> str:
        """ Returns the DXF entity type. """
        return self._entity.DXFTYPE

    @property
    def dxfattribs(self) -> DXFAttributes:
        """ Returns the DXF attribute definition. """
        return self._entity.DXFATTRIBS

    def dxf_default_value(self, key: str) -> Any:
        """ Returns the default value as defined in the DXF standard. """
        attrib: Optional['DXFAttr'] = self.dxfattribs.get(key)
        if attrib:
            return attrib.default
        else:
            return None

    def export_dxf_attribs(self, tagwriter: 'TagWriter',
                           attribs: Union[str, Iterable]) -> None:
        """ Exports DXF attribute `name` by `tagwriter`. Non optional attributes
        are forced and optional tags are only written if different to default
        value. DXF version check is always on: does not export DXF attribs
        which are not supported by tagwriter.dxfversion.

        Args:
            tagwriter: tag writer object
            attribs: DXF attribute name as string or an iterable of names

        """
        if isinstance(attribs, str):
            self._export_dxf_attribute_optional(tagwriter, attribs)
        else:
            for name in attribs:
                self._export_dxf_attribute_optional(tagwriter, name)

    def _export_dxf_attribute_optional(self, tagwriter: 'TagWriter',
                                       name: str) -> None:
        """ Exports DXF attribute `name` by `tagwriter`. Optional tags are only
        written if different to default value.

        Args:
            tagwriter: tag writer object
            name: DXF attribute name

        """
        export_dxf_version = tagwriter.dxfversion
        not_force_optional = not tagwriter.force_optional
        attrib: Optional['DXFAttr'] = self.dxfattribs.get(name)

        if attrib:
            optional = attrib.optional
            default = attrib.default
            value = self.get(name, None)
            # Force default value e.g. layer
            if value is None and not optional:
                # Default value could be None
                value = default

                # Do not export None values
            if ((value is not None) and
                    (export_dxf_version >= attrib.dxfversion)):
                # Do not write explicit optional attribs if equal to default
                # value
                if (optional
                        and not_force_optional
                        and default is not None
                        and default == value):
                    return
                    # Just export x, y for 2D points, if value is a 3D point
                if attrib.xtype == XType.point2d and len(value) > 2:
                    value = value[:2]
                if isinstance(value, str):
                    assert '\n' not in value, "line break '\\n' not allowed"
                    assert '\r' not in value, "line break '\\r' not allowed"
                tag = dxftag(attrib.code, value)
                tagwriter.write_tag(tag)
        else:
            raise const.DXFAttributeError(
                ERR_INVALID_DXF_ATTRIB.format(name, self.dxftype))


BASE_CLASS_CODES = {0, 5, 102, 330}


class SubclassProcessor:
    """ Helper class for loading tags into entities. (internal class) """

    def __init__(self, tags: 'ExtendedTags', dxfversion=None):
        if len(tags.subclasses) == 0:
            raise ValueError('Invalid tags.')
        self.subclasses: List[Tags] = list(tags.subclasses)  # copy subclasses
        self.dxfversion = dxfversion
        # DXF R12 and prior have no subclass marker system, all tags of an
        # entity in one flat list.
        # Later DXF versions have at least 2 subclasses base_class and
        # AcDbEntity.
        # Exception: CLASS has also only one subclass and no subclass marker,
        # handled as DXF R12 entity
        self.r12 = (dxfversion == const.DXF12) or (len(self.subclasses) == 1)
        self.name = tags.dxftype()
        try:
            self.handle = tags.get_handle()
        except const.DXFValueError:
            self.handle = '<?>'

    @property
    def base_class(self):
        return self.subclasses[0]

    def log_unprocessed_tags(self, unprocessed_tags: Iterable,
                             subclass='<?>') -> None:
        if options.log_unprocessed_tags:
            for tag in unprocessed_tags:
                logger.info(
                    f"ignored {repr(tag)} in subclass {subclass}")

    def find_subclass(self, name: str) -> Optional[Tags]:
        for subclass in self.subclasses:
            if len(subclass) and subclass[0].value == name:
                return subclass
        return None

    def subclass_by_index(self, index: int) -> Optional[Tags]:
        try:
            return self.subclasses[index]
        except IndexError:
            return None

    def load_dxfattribs_into_namespace(self, dxf: DXFNamespace,
                                       subclass_definition: DefSubclass,
                                       index: int = None) -> Tags:
        """ Load all existing DXF attribute into DXFNamespace and return
        unprocessed tags, without leading subclass marker(102, ...).

        Args:
            dxf: target namespace
            subclass_definition: DXF attribute definitions (name=subclass_name,
                                 attribs={key=attribute name, value=DXFAttr})
            index: locate subclass by location

        Returns:
             Tags: unprocessed tags

        """

        # R12 has always unprocessed tags, because there are all tags in one
        # subclass and one subclass definition never covers all tags e.g.
        # handle is processed in DXFEntity, so it is an unprocessed tag in
        # AcDbEntity.
        if self.r12:
            tags = self.subclasses[0]
        else:
            if index is None:
                tags = self.find_subclass(subclass_definition.name)
            else:
                tags = self.subclass_by_index(index)
            if tags is None:
                return Tags()
        return self.load_tags_into_namespace(dxf, tags[1:], subclass_definition)

    @staticmethod
    def load_tags_into_namespace(dxf: DXFNamespace, tags: Tags,
                                 subclass_definition: DefSubclass) -> Tags:
        """ Load all existing DXF attribute into DXFNamespace and return
        unprocessed tags, without leading subclass marker (102, ...).

        Args:
            dxf: target namespace
            tags: tags to process
            subclass_definition: DXF attribute definitions (name=subclass_name,
                                 attribs={key=attribute name, value=DXFAttr})

        Returns:
             Tags: unprocessed tags

        """

        def replace_attrib(code) -> bool:
            """ Returns ``True`` if an attribute was replaced by a doublet. """
            for index, dxfattr in enumerate(doublets):
                if dxfattr.code == code:
                    group_codes[code] = dxfattr
                    del doublets[index]
                    return True
            return False

        unprocessed_tags = Tags()
        # Do not cache group codes, content of group code will be deleted while
        # processing.
        group_codes = dict()
        doublets = []
        for dxfattr in subclass_definition.attribs.values():
            if dxfattr.code in group_codes:
                doublets.append(dxfattr)
            else:
                group_codes[dxfattr.code] = dxfattr

        # Iterate without leading subclass marker and for R12 without
        # leading (0, ...) structure tag.
        for tag in tags:
            code, value = tag
            attrib = group_codes.get(code)
            if attrib is not None:
                if (attrib.xtype != XType.callback) or (
                        attrib.setter is not None):
                    dxf.set(attrib.name, value)

                if len(doublets) and replace_attrib(code):
                    continue
                del group_codes[code]
            else:
                unprocessed_tags.append(tag)
        return unprocessed_tags

    def append_base_class_to_acdb_entity(self) -> None:
        """ It is valid to mix up the base class with AcDbEntity class.
        This method appends all none base class group codes to the
        AcDbEntity class.
        """
        # This is only needed for DXFEntity, so applying this method
        # automatically to all entities is waste of runtime
        # -> DXFGraphic.load_dxf_attribs()
        if self.r12:
            return

        acdb_entity_tags = self.subclasses[1]
        if acdb_entity_tags[0] == (100, 'AcDbEntity'):
            acdb_entity_tags.extend(tag for tag in self.subclasses[0] if
                                    tag.code not in BASE_CLASS_CODES)

    @staticmethod
    def recover_graphic_attributes(tags: Tags, dxf: DXFNamespace) -> Tags:
        return recover_graphic_attributes(tags, dxf)

    def load_and_recover_dxfattribs(self, dxf, subclass, index=None):
        tags = self.load_dxfattribs_into_namespace(dxf, subclass, index)
        if len(tags) and not self.r12:
            tags = recover_graphic_attributes(tags, dxf)
            if len(tags):
                self.log_unprocessed_tags(tags, subclass=subclass.name)


GRAPHIC_ATTRIBUTES_TO_RECOVER = {
    8: 'layer',
    6: 'linetype',
    62: 'color',
    67: 'paperspace',
    370: 'lineweight',
    48: 'ltscale',
    60: 'invisible',
    420: 'true_color',
    430: 'color_name',
    440: 'transparency',
    284: 'shadow_mode',
    347: 'material_handle',
    348: 'visualstyle_handle',
    380: 'plotstyle_enum',
    390: 'plotstyle_handle'
}


def recover_graphic_attributes(tags: Tags, dxf: DXFNamespace) -> Tags:
    unprocessed_tags = Tags()
    for tag in tags:
        attrib_name = GRAPHIC_ATTRIBUTES_TO_RECOVER.get(tag.code)
        # Don't know if the unprocessed tag is really a misplaced tag,
        # so check if the attribute already exist!
        if attrib_name and not dxf.hasattr(attrib_name):
            dxf.set(attrib_name, tag.value)
        else:
            unprocessed_tags.append(tag)
    return unprocessed_tags
