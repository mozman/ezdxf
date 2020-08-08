# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
"""
DXFEntity() is the base class of all DXF entities.

DXFNamespace() manages all named DXF attributes of an entity.

The actual entity system of ezdxf uses the latest supported DXF version.
The stored DXF version of the document is used to warn users if they use
unsupported DXF features of the actual DXF version.

The DXF version of the document can be changed at runtime or overridden by
exporting, but unsupported DXF features are just ignored by exporting.

Ezdxf does no conversion between different DXF versions, this package is
still not a CAD application.

"""
from typing import (
    TYPE_CHECKING, List, Dict, Any, Iterable, Optional, Union, Type, TypeVar,
    Set,
)
import copy
from ezdxf import options
from ezdxf.lldxf.types import handle_code, dxftag, cast_value
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import (
    DXF2000, STRUCTURE_MARKER, OWNER_CODE, DXF12, ACAD_REACTORS,
    ACAD_XDICTIONARY, DXFAttributeError, DXFValueError, DXFTypeError,
    DXFKeyError,
)
from ezdxf.tools import set_flag_state
from .xdata import XData, EmbeddedObjects
from .appdata import AppData, Reactors
from .xdict import ExtensionDict
import logging

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        Auditor, TagWriter, Drawing, EntityDB, EntityFactory, DXFAttr,
    )

__all__ = [
    'DXFNamespace', 'DXFEntity', 'DXFTagStorage', 'SubclassProcessor',
    'base_class'
]

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
    """
    Uses the Python object itself as attribute storage, only valid Python names
    can be used as attrib name.

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
        attrib_def: Optional['DXFAttr'] = self.dxfattribs.get(key)
        if attrib_def:
            if attrib_def.xtype == XType.callback:
                return attrib_def.get_callback_value(self._entity)
            else:
                return attrib_def.default
        else:
            raise DXFAttributeError(
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
                    raise DXFValueError(
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
            raise DXFAttributeError(
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
            raise DXFAttributeError(ERR_DXF_ATTRIB_NOT_EXITS.format(key))

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
            raise DXFAttributeError(
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
        """
        Exports DXF attribute `name` by `tagwriter`. Non optional attributes
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
        """
        Exports DXF attribute `name` by `tagwriter`. Optional tags are only
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
            raise DXFAttributeError(
                ERR_INVALID_DXF_ATTRIB.format(name, self.dxftype))


BASE_CLASS_CODES = {0, 5, 102, 330}


class SubclassProcessor:
    """  Helper class for loading tags into entities. (internal class) """

    def __init__(self, tags: ExtendedTags, dxfversion=None):
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
        self.r12 = (dxfversion == DXF12) or (len(self.subclasses) == 1)
        self.name = tags.dxftype()
        try:
            self.handle = tags.get_handle()
        except DXFValueError:
            self.handle = '<?>'

    @property
    def base_class(self):
        return self.subclasses[0]

    def log_unprocessed_tags(self, unprocessed_tags: Iterable,
                             subclass='<?>') -> None:
        if options.log_unprocessed_tags:
            for tag in unprocessed_tags:
                logger.info(
                    f"ignored {repr(tag)} in {str(self)}, {subclass}")

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
        """
        Load all existing DXF attribute into DXFNamespace and return unprocessed
        tags, without leading subclass marker(102, ...).

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
        """
        Load all existing DXF attribute into DXFNamespace and return unprocessed
        tags, without leading subclass marker (102, ...).

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


base_class = DefSubclass(None, {
    'handle': DXFAttr(5),

    # owner: Soft-pointer ID/handle to owner BLOCK_RECORD object
    # This tag is not supported by DXF R12, but is used intern to unify entity
    # handling between DXF R12 and DXF R2000+
    # Do not write this tag into DXF R12 files!
    'owner': DXFAttr(330),

    # Application defined data can only appear here:
    # 102, {APPID ... multiple entries possible DXF R12?
    # 102, {ACAD_REACTORS ... one entry DXF R2000+, optional
    # 102, {ACAD_XDICTIONARY  ... one entry DXF R2000+, optional
})

T = TypeVar('T', bound='DXFEntity')


class DXFEntity:
    """ Common base class for all DXF entities. """
    DXFTYPE = 'DXFENTITY'  # storing as class var needs less memory
    DXFATTRIBS = DXFAttributes(base_class)  # DXF attribute definitions

    # Default DXF attributes are set at instantiating a new object, the the
    # difference to attribute default values is, that this attributes are
    # really set, this means there is an real object in the dxf namespace
    # defined, where default attribute values get returned on access without
    # an existing object in the dxf namespace.
    DEFAULT_ATTRIBS: Dict = {}
    MIN_DXF_VERSION_FOR_EXPORT = DXF12

    def __init__(self, doc: 'Drawing' = None):
        """ Default constructor. (internal API)"""
        # Public attributes for package users
        self.doc: Drawing = doc
        self.dxf: DXFNamespace = DXFNamespace(entity=self)

        # None public attributes for package users
        # create extended data only if needed
        self.appdata: Optional[AppData] = None
        self.reactors: Optional[Reactors] = None
        self.extension_dict: Optional[ExtensionDict] = None
        self.xdata: Optional[XData] = None
        self.embedded_objects: Optional[EmbeddedObjects] = None
        self.proxy_graphic: Optional[bytes] = None

    @classmethod
    def load(cls: Type[T], tags: Union[ExtendedTags, Tags],
             doc: 'Drawing' = None) -> T:
        """
        Constructor to generate entities loaded from DXF files (untrusted
        environment)

        Args:
            tags: DXF tags as Tags() or ExtendedTags()
            doc: DXF Document

        (internal API)
        """
        if not isinstance(tags, ExtendedTags):
            tags = ExtendedTags(tags)
        entity = cls(doc)  # bare minimum setup
        entity.load_tags(tags)
        return entity

    @classmethod
    def from_text(cls: Type[T], text: str, doc: 'Drawing' = None) -> T:
        """ Load constructor from text for testing. (internal API)"""
        return cls.load(ExtendedTags.from_text(text), doc)

    @classmethod
    def shallow_copy(cls: Type[T], other: 'DXFEntity') -> T:
        """ Copy constructor for type casting e.g. Polyface and Polymesh.
        (internal API)
        """
        entity = cls(other.doc)
        entity.dxf = other.dxf
        entity.extension_dict = other.extension_dict
        entity.reactors = other.reactors
        entity.appdata = other.appdata
        entity.xdata = other.xdata
        entity.embedded_objects = other.embedded_objects
        entity.proxy_graphic = other.proxy_graphic
        entity.dxf.rewire(entity)
        if (entity.doc is not None) and (entity.dxf.handle is not None):
            # Replace entity in entity db, can't call add() here.
            entity.doc.entitydb[entity.dxf.handle] = entity
        return entity

    def copy(self: T) -> T:
        """
        Returns a copy of `self` but without handle, owner and reactors.
        This copy is NOT stored in the entity database and does NOT reside
        in any layout, block, table or objects section! Extension dictionary
        and reactors are not copied.

        Don't use this function to duplicate DXF entities in drawing,
        use :meth:`EntityDB.duplicate_entity` instead for this task.

        Copying is not trivial, because of linked resources and the lack of
        documentation how to handle this linked resources: extension dictionary,
        handles in appdata, xdata or embedded objects.

        (internal API)
        """
        entity = self.__class__(doc=self.doc)
        # copy and bind dxf namespace to new entity
        entity.dxf = self.dxf.copy(entity)
        entity.dxf.reset_handles()
        entity.extension_dict = None
        entity.reactors = None
        entity.proxy_graphic = self.proxy_graphic  # immutable bytes

        # if appdata contains handles, they are treated as shared resources
        entity.appdata = copy.deepcopy(self.appdata)

        # if xdata contains handles, they are treated as shared resources
        entity.xdata = copy.deepcopy(self.xdata)

        # if embedded objects contains handles, they are treated as shared resources
        entity.embedded_objects = copy.deepcopy(self.embedded_objects)
        self._copy_data(entity)
        return entity

    def _copy_data(self, entity: 'DXFEntity') -> None:
        """ Copy entity data like vertices or attribs and store the copies into
        the entity database.
        (internal API)
        """
        pass

    def __deepcopy__(self, memodict: Dict = None):
        """ Some entities maybe linked by more than one entity, to be safe use
        `memodict` for bookkeeping.
        (internal API)
        """
        memodict = memodict or {}
        try:
            return memodict[id(self)]
        except KeyError:
            copy = self.copy()
            memodict[id(self)] = copy
            return copy

    def load_tags(self, tags: ExtendedTags) -> None:
        """ Generic tag loading interface, called if DXF drawing is loaded from
        a stream or file.
        (internal API)
        """
        if tags:
            if len(tags.appdata):
                self.setup_app_data(tags.appdata)
            if len(tags.xdata):
                self.xdata = XData(tags.xdata)
            if tags.embedded_objects:
                self.embedded_objects = EmbeddedObjects(
                    tags.embedded_objects)
            if self.doc:
                dxfversion = self.doc.dxfversion
            else:  # test cases
                dxfversion = None
            processor = SubclassProcessor(tags, dxfversion=dxfversion)
            self.dxf = self.load_dxf_attribs(processor)

    @classmethod
    def new(cls: Type[T], handle: str = None, owner: str = None,
            dxfattribs: Dict = None, doc: 'Drawing' = None) -> T:
        """
        Constructor for building new entities from scratch by ezdxf
        (trusted environment).

        Args:
            handle: unique DXF entity handle or None
            owner: owner handle if entity has an owner else None or '0'
            dxfattribs: DXF attributes
            doc: DXF document

        (internal API)
        """
        entity = cls(doc)
        if handle:
            entity.dxf.handle = handle
        if owner:
            entity.dxf.owner = owner
        attribs = dict(cls.DEFAULT_ATTRIBS)
        attribs.update(dxfattribs or {})
        entity.update_dxf_attribs(attribs)
        entity.post_new_hook()
        return entity

    def update_dxf_attribs(self, dxfattribs: Dict) -> None:
        """ Set DXF attributes by a ``dict`` like :code:`{'layer': 'test',
        'color': 4}`.
        """
        setter = self.dxf.set
        for key, value in dxfattribs.items():
            setter(key, value)

    def post_new_hook(self):
        """ Post processing and integrity validation after entity creation
        (internal API)
        """
        pass

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> DXFNamespace:
        return DXFNamespace(processor, self)

    def setup_app_data(self, appdata: List[Tags]) -> None:
        """ Setup data structures from APP data. (internal API) """
        for data in appdata:
            code, appid = data[0]
            if appid == ACAD_REACTORS:
                self.reactors = Reactors.from_tags(data)
            elif appid == ACAD_XDICTIONARY:
                self.extension_dict = ExtensionDict.from_tags(self, data)
            else:
                self.set_app_data(appid, data)

    def update_handle(self, handle: str) -> None:
        """ Update entity handle. (internal API) """
        self.dxf.handle = handle
        if self.extension_dict:
            self.extension_dict.update_owner(self)

    @property
    def dxffactory(self) -> 'EntityFactory':
        """ Get the associated DXF factory. (internal API) """
        return self.doc.dxffactory

    def get_dxf_attrib(self, key: str, default: Any = None) -> Any:
        """
        Get DXF attribute `key`, returns `default` if key doesn't exist, or
        raise :class:`DXFValueError` if `default` is :class:`DXFValueError`
        and no DXF default value is defined::

            layer = entity.get_dxf_attrib("layer")
            # same as
            layer = entity.dxf.layer

        Raises :class:`DXFAttributeError` if `key` is not an supported DXF
        attribute.

        """
        return self.dxf.get(key, default)

    def set_dxf_attrib(self, key: str, value: Any) -> None:
        """
        Set new `value` for DXF attribute `key`::

           entity.set_dxf_attrib("layer", "MyLayer")
           # same as
           entity.dxf.layer = "MyLayer"

        Raises :class:`DXFAttributeError` if `key` is not an supported DXF
        attribute.

        """
        self.dxf.set(key, value)

    def del_dxf_attrib(self, key: str) -> None:
        """
        Delete DXF attribute `key`, does not raise an error if attribute is
        supported but not present.

        Raises :class:`DXFAttributeError` if `key` is not an supported DXF
        attribute.

        """
        self.dxf.discard(key)

    def has_dxf_attrib(self, key: str) -> bool:
        """
        Returns ``True`` if DXF attribute `key` really exist.

        Raises :class:`DXFAttributeError` if `key` is not an supported DXF
        attribute.

        """
        return self.dxf.hasattr(key)

    dxf_attrib_exists = has_dxf_attrib

    def is_supported_dxf_attrib(self, key: str) -> bool:
        """
        Returns ``True`` if DXF attrib `key` is supported by this entity.
        Does not grant that attribute `key` really exist.

        """
        if key in self.DXFATTRIBS:
            return self.doc.dxfversion >= self.DXFATTRIBS.get(key).dxfversion
        else:
            return False

    @property
    def entitydb(self) -> 'EntityDB':
        """ Returns associated entity database. (internal API)"""
        return self.doc.entitydb

    def dxftype(self) -> str:
        """ Get DXF type as string, like ``LINE`` for the line entity. """
        return self.DXFTYPE

    def __str__(self) -> str:
        """ Returns a simple string representation. """
        return "{}(#{})".format(self.dxftype(), self.dxf.handle)

    def __repr__(self) -> str:
        """ Returns a simple string representation including the class. """
        return str(self.__class__) + " " + str(self)

    def dxfattribs(self, drop: Set[str] = None) -> Dict:
        """ Returns a ``dict`` with all existing DXF attributes and their
        values and exclude all DXF attributes listed in set `drop`.

        .. versionchanged:: 0.12
            added `drop` argument

        """
        all_attribs = self.dxf.all_existing_dxf_attribs()
        if drop:
            return {k: v for k, v in all_attribs.items() if k not in drop}
        else:
            return all_attribs

    def set_flag_state(self, flag: int, state: bool = True,
                       name: str = 'flags') -> None:
        """ Set binary coded `flag` of DXF attribute `name` to ``1`` (on)
        if `state` is ``True``, set `flag` to ``0`` (off)
        if `state` is ``False``.
        """
        flags = self.dxf.get(name, 0)
        self.dxf.set(name, set_flag_state(flags, flag, state=state))

    def get_flag_state(self, flag: int, name: str = 'flags') -> bool:
        """
        Returns ``True`` if any `flag` of DXF attribute is ``1`` (on), else
        ``False``. Always check only one flag state at the time.
        """
        return bool(self.dxf.get(name, 0) & flag)

    @property
    def is_alive(self):
        """ Returns ``False`` if entity has been deleted. """
        return hasattr(self, 'dxf')

    def remove_dependencies(self, other: 'Drawing' = None):
        """ Remove all dependencies from actual document.

        Intended usage is to remove dependencies from the actual document to
        move or copy the entity to an `other` document.

        An error free call of this method does NOT guarantee that this entity
        can be moved/copied to the `other` document, some entities like
        DIMENSION have too much dependencies to a document to move or copy
        them, but to check this is not the domain of this method!

        (internal API)
        """
        if self.is_alive:
            self.dxf.owner = None
            self.dxf.handle = None
            self.reactors = None
            self.extension_dict = None
            self.appdata = None
            self.xdata = None
            self.embedded_objects = None

    def destroy(self) -> None:
        """
        Delete all data and references. Does not delete entity from structures
        like layouts or groups.

        This method should not be used to delete entities from a layout/document
        by the package user, use :meth:`BaseLayout.delete_entity` method for
        that!

        (internal API)

        """
        if self.extension_dict is not None:
            self.extension_dict.destroy(self.doc)
            del self.extension_dict
        del self.appdata
        del self.reactors
        del self.xdata
        del self.embedded_objects
        del self.doc
        del self.dxf  # check mark for is_alive

    def preprocess_export(self, tagwriter: 'TagWriter') -> bool:
        """ Pre requirement check and pre processing for export.

        Returns False if entity should not be exported at all.

        (internal API)
        """
        return True

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        """ Export DXF entity by `tagwriter`.

        This is the first key method for exporting DXF entities:

            - has to know the group codes for each attribute
            - has to add subclass tags in correct order
            - has to integrate extended data: ExtensionDict, Reactors, AppData
            - has to maintain the correct tag order (because sometimes order matters)

        (internal API)

        """
        if tagwriter.dxfversion < self.MIN_DXF_VERSION_FOR_EXPORT:
            return
        if not self.preprocess_export(tagwriter):
            return
        # ! first step !
        # write handle, AppData, Reactors, ExtensionDict, owner
        self.export_base_class(tagwriter)

        # this is the entity specific part
        self.export_entity(tagwriter)

        # ! Last step !
        # write xdata, embedded objects
        self.export_embedded_objects(tagwriter)
        self.export_xdata(tagwriter)

    def export_base_class(self, tagwriter: 'TagWriter') -> None:
        """ Export base class DXF attributes and structures. (internal API) """
        dxftype = self.DXFTYPE
        _handle_code = 105 if dxftype == 'DIMSTYLE' else 5
        # 1. tag: (0, DXFTYPE)
        tagwriter.write_tag2(STRUCTURE_MARKER, dxftype)

        if tagwriter.dxfversion >= DXF2000:
            tagwriter.write_tag2(_handle_code, self.dxf.handle)
            if self.appdata:
                self.appdata.export_dxf(tagwriter)
            if self.extension_dict:
                self.extension_dict.export_dxf(tagwriter)
            if self.reactors:
                self.reactors.export_dxf(tagwriter)
            tagwriter.write_tag2(OWNER_CODE, self.dxf.owner)
        else:  # DXF R12
            if tagwriter.write_handles:
                tagwriter.write_tag2(_handle_code, self.dxf.handle)
                # do not write owner handle - not supported by DXF R12

    # interface definition
    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export DXF entity specific data by `tagwriter`.

        This is the second key method for exporting DXF entities:

            - has to know the group codes for each attribute
            - has to add subclass tags in correct order
            - has to maintain the correct tag order (because sometimes order matters)

        (internal API)
        """
        # base class (handle, appid, reactors, xdict, owner) export is done by parent class
        pass
        # xdata and embedded objects  export is also done by parent

    def export_xdata(self, tagwriter: 'TagWriter') -> None:
        """ Export DXF XDATA by `tagwriter`. (internal API)"""
        if self.xdata:
            self.xdata.export_dxf(tagwriter)

    def export_embedded_objects(self, tagwriter: 'TagWriter') -> None:
        """ Export embedded objects by `tagwriter`. (internal API)"""
        if self.embedded_objects:
            self.embedded_objects.export_dxf(tagwriter)

    def audit(self, auditor: 'Auditor') -> None:
        """ Validity check. (internal API) """
        # do not check owner -> DXFGraphic(), DXFObject()
        # check app data
        # check reactors
        # check extension dict
        # check XDATA

    def has_extension_dict(self) -> bool:
        """ Returns ``True`` if entity has an attached
        :class:`~ezdxf.entities.xdict.ExtensionDict`.
        """
        return self.extension_dict is not None

    def get_extension_dict(self) -> 'ExtensionDict':
        """ Returns the existing :class:`~ezdxf.entities.xdict.ExtensionDict`
        or a new created one.
        """

        def new_extension_dict():
            self.extension_dict = ExtensionDict.new(self)
            return self.extension_dict

        if self.has_extension_dict():
            return self.extension_dict
        else:
            return new_extension_dict()

    def has_app_data(self, appid: str) -> bool:
        """ Returns ``True`` if application defined data for `appid` exist. """
        if self.appdata:
            return appid in self.appdata
        else:
            return False

    def get_app_data(self, appid: str) -> Tags:
        """ Returns application defined data for `appid`.

        Args:
            appid: application name as defined in the APPID table.

        Raises:
            DXFValueError: no data for `appid` found

        """
        if self.appdata:
            return self.appdata.get(appid)[1:-1]
        else:
            raise DXFValueError(appid)

    def set_app_data(self, appid: str, tags: Iterable) -> None:
        """ Set application defined data for `appid` as iterable of tags.

        Args:
             appid: application name as defined in the APPID table.
             tags: iterable of (code, value) tuples or :class:`~ezdxf.lldxf.types.DXFTag`

        """
        if self.appdata is None:
            self.appdata = AppData()
        self.appdata.add(appid, tags)

    def discard_app_data(self, appid: str):
        """ Discard application defined data for `appid`. Does not raise an
        exception if no data for `appid` exist.
        """
        if self.appdata:
            self.appdata.discard(appid)

    def has_xdata(self, appid: str) -> bool:
        """ Returns ``True`` if extended data for `appid` exist. """
        if self.xdata:
            return appid in self.xdata
        else:
            return False

    def get_xdata(self, appid: str) -> Tags:
        """ Returns extended data for `appid`.

        Args:
            appid: application name as defined in the APPID table.

        Raises:
            DXFValueError: no extended data for `appid` found

        """
        if self.xdata:
            return Tags(self.xdata.get(appid)[1:])
        else:
            raise DXFValueError(appid)

    def set_xdata(self, appid: str, tags: Iterable) -> None:
        """ Set extended data for `appid` as iterable of tags.

        Args:
             appid: application name as defined in the APPID table.
             tags: iterable of (code, value) tuples or :class:`~ezdxf.lldxf.types.DXFTag`

        """
        if self.xdata is None:
            self.xdata = XData()
        self.xdata.add(appid, tags)

    def discard_xdata(self, appid: str) -> None:
        """ Discard extended data for `appid`. Does not raise an exception if
        no extended data for `appid` exist.
        """
        if self.xdata:
            self.xdata.discard(appid)

    def has_xdata_list(self, appid: str, name: str) -> bool:
        """ Returns ``True`` if a tag list `name` for extended data `appid`
        exist.
        """
        if self.has_xdata(appid):
            return self.xdata.has_xlist(appid, name)
        else:
            return False

    def get_xdata_list(self, appid: str, name: str) -> Tags:
        """ Returns tag list `name` for extended data `appid`.

        Args:
            appid: application name as defined in the APPID table.
            name: extended data list name

        Raises:
            DXFValueError: no extended data for `appid` found or no data list `name` not found

        """
        if self.xdata:
            return Tags(self.xdata.get_xlist(appid, name))
        else:
            raise DXFValueError(appid)

    def set_xdata_list(self, appid: str, name: str, tags: Iterable) -> None:
        """ Set tag list `name` for extended data `appid` as iterable of tags.

        Args:
             appid: application name as defined in the APPID table.
             name: extended data list name
             tags: iterable of (code, value) tuples or :class:`~ezdxf.lldxf.types.DXFTag`

        """
        if self.xdata is None:
            self.xdata = XData()
        self.xdata.set_xlist(appid, name, tags)

    def discard_xdata_list(self, appid: str, name: str) -> None:
        """ Discard tag list `name` for extended data `appid`. Does not raise
        an exception if no extended data for `appid` or no tag list `name`
        exist.
        """
        if self.xdata:
            self.xdata.discard_xlist(appid, name)

    def replace_xdata_list(self, appid: str, name: str, tags: Iterable) -> None:
        """
        Replaces tag list `name` for existing extended data `appid` by `tags`.
        Appends new list if tag list `name` do not exist, but raises
        :class:`DXFValueError` if extended data `appid` do not exist.

        Args:
             appid: application name as defined in the APPID table.
             name: extended data list name
             tags: iterable of (code, value) tuples or :class:`~ezdxf.lldxf.types.DXFTag`

        Raises:
            DXFValueError: no extended data for `appid` found

        """
        self.xdata.replace_xlist(appid, name, tags)

    def has_reactors(self) -> bool:
        """ Returns ``True`` if entity has reactors. """
        return bool(self.reactors)

    def get_reactors(self) -> List[str]:
        """ Returns associated reactors as list of handles. """
        return self.reactors.get() if self.reactors else []

    def set_reactors(self, handles: Iterable[str]) -> None:
        """ Set reactors as list of handles. """
        if self.reactors is None:
            self.reactors = Reactors()
        self.reactors.set(handles)

    def append_reactor_handle(self, handle: str) -> None:
        """ Append `handle` to reactors. """
        if self.reactors is None:
            self.reactors = Reactors()
        self.reactors.add(handle)

    def discard_reactor_handle(self, handle: str) -> None:
        """ Discard `handle` from reactors. Does not raise an exception if
        `handle` does not exist.
        """
        if self.reactors:
            self.reactors.discard(handle)


class DXFTagStorage(DXFEntity):
    """ Just store all the tags as they are. (internal class) """

    def __init__(self, doc: 'Drawing' = None):
        """ Default constructor """
        super().__init__(doc)
        self.xtags: Optional[ExtendedTags] = None

    def copy(self) -> 'DXFEntity':
        raise DXFTypeError(
            f'Cloning of tag storage {self.dxftype()} not supported.'
        )

    @property
    def base_class(self):
        return self.xtags.subclasses[0]

    @classmethod
    def load(cls, tags: ExtendedTags, doc: 'Drawing' = None) -> 'DXFTagStorage':
        assert isinstance(tags, ExtendedTags)
        entity = cls(doc)
        entity.load_tags(tags)
        entity.store_tags(tags)
        if options.load_proxy_graphics:
            entity.load_proxy_graphic()
        return entity

    def load_proxy_graphic(self) -> Optional[bytes]:
        try:
            acdb_entity = self.xtags.get_subclass('AcDbEntity')
        except DXFKeyError:
            return
        binary_data = [tag.value for tag in acdb_entity.find_all(310)]
        if len(binary_data):
            self.proxy_graphic = b''.join(binary_data)

    def store_tags(self, tags: ExtendedTags) -> None:
        # store DXFTYPE, overrides class member
        # 1. tag of 1. subclass is the structure tag (0, DXFTYPE)
        self.xtags = tags
        self.DXFTYPE = self.base_class[0].value
        try:
            acdb_entity = tags.get_subclass('AcDbEntity')
            self.dxf.__dict__['paperspace'] = acdb_entity.get_first_value(67, 0)
        except DXFKeyError:
            # just fake it
            self.dxf.__dict__['paperspace'] = 0

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Write subclass tags as they are. """
        for subclass in self.xtags.subclasses[1:]:
            tagwriter.write_tags(subclass)

    def destroy(self) -> None:
        del self.xtags
        super().destroy()
