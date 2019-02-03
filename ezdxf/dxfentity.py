# Created: 11.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Any, Iterable, Mapping, List, cast, Tuple
from ezdxf.lldxf.const import DXFStructureError, DXFAttributeError, DXFInvalidLayerName, DXFValueError, DXFXDataError
from ezdxf.lldxf.validator import is_valid_layer_name
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.extendedtags import ExtendedTags

from ezdxf.tools import set_flag_state
from ezdxf.math import OCS

if TYPE_CHECKING:  # import forward dependencies
    from eztypes import TagValue, IterableTags, DXFAttr, DXFDictionary
    from eztypes import Drawing, EntityDB, DXFFactoryType, GenericLayoutType

ACAD_REACTORS = '{ACAD_REACTORS'
ACAD_XDICTIONARY = '{ACAD_XDICTIONARY'


class NotFoundException(Exception):
    pass


class DXFNamespace:
    """
    Provides the dxf namespace for GenericWrapper.

    """
    __slots__ = ('_wrapper',)

    def __init__(self, wrapper: 'DXFEntity'):
        # DXFNamespace.__setattr__ can not set _wrapper
        super(DXFNamespace, self).__setattr__('_wrapper', wrapper)

    def __getattr__(self, attrib: str):
        """
        Returns value of DXF attribute *attrib*. usage: value = DXFEntity.dxf.attrib

        """
        return self._wrapper.get_dxf_attrib(attrib)

    def __setattr__(self, attrib: str, value) -> None:
        """
        Set DXF attribute *attrib* to *value.  usage: DXFEntity.dxf.attrib = value

        """
        return self._wrapper.set_dxf_attrib(attrib, value)

    def __delattr__(self, attrib: str) -> None:
        """
        Remove DXF attribute *attrib*.  usage: del DXFEntity.dxf.attrib

        """
        return self._wrapper.del_dxf_attrib(attrib)


class DXFEntity:
    __slots__ = ('tags', 'dxf', 'drawing')
    TEMPLATE = None
    CLASS = None
    DXFATTRIBS = {}

    def __init__(self, tags: ExtendedTags, drawing: 'Drawing' = None):
        self.tags = tags  # DXF tags stored as DXFTag (and inherited) in an ExtendedTags container
        self.dxf = DXFNamespace(self)  # type: Any # dynamic DXF attribute dispatching, e.g. DXFEntity.dxf.layer
        self.drawing = drawing

    def __str__(self) -> str:
        """
        Returns a simple string representation.

        """
        return "{}(#{})".format(self.dxftype(), self.dxf.handle)

    def __repr__(self) -> str:
        """
        Returns a simple string representation including the class.

        """
        return str(self.__class__) + " " + str(self)

    @property
    def dxffactory(self) -> 'DXFFactoryType':
        return self.drawing.dxffactory

    @property
    def dxfversion(self) -> str:
        return self.drawing.dxfversion

    @property
    def entitydb(self) -> 'EntityDB':
        return self.drawing.entitydb

    @classmethod
    def new(cls, handle: str, dxfattribs: dict = None, drawing: 'Drawing' = None) -> 'DXFEntity':
        if cls.TEMPLATE is None:
            raise NotImplementedError("new() for type %s not implemented." % cls.__name__)
        entity = cls(cls.TEMPLATE.clone(), drawing)
        entity.dxf.handle = handle
        if dxfattribs is not None:
            if 'layer' in dxfattribs:
                layer_name = dxfattribs['layer']
                if not is_valid_layer_name(layer_name):
                    raise DXFInvalidLayerName("Invalid layer name '{}'".format(layer_name))
            entity.update_dxf_attribs(dxfattribs)
        entity.post_new_hook()
        return entity

    def post_new_hook(self) -> None:
        """
        Called after entity creation.

        """
        pass

    def _new_entity(self, type_: str, dxfattribs: dict) -> 'DXFEntity':
        """
        Create new entity with same layout settings as *self*.

        Used by INSERT & POLYLINE to create appended DXF entities, don't use it to create new standalone entities.

        """
        entity = self.dxffactory.create_db_entry(type_, dxfattribs)
        self.dxffactory.copy_layout(self, entity)
        return entity

    def __copy__(self) -> 'DXFEntity':
        """
        Deep copy of DXFEntity with new handle and duplicated linked entities (VERTEX, ATTRIB, SEQEND).
        The new entity is not included in any layout space, so the owner tag is set to '0' for undefined owner/layout.

        Use Layout.add_entity(new_entity) to add the duplicated entity to a layout, layout can be the model space,
        a paper space layout or a block layout.

        It is not called __deepcopy__, because this is not a deep copy in the meaning of Python, because handle, link
        and owner is changed.

        """
        new_tags = self.entitydb.duplicate_tags(self.tags)
        entity = self.dxffactory.wrap_entity(new_tags)
        if self.supports_dxf_attrib('owner'):  # R2000+
            entity.dxf.owner = '0'  # reset ownership/layout
        return entity

    copy = __copy__

    def linked_entities(self) -> Iterable['DXFEntity']:
        """
        Iterate over all linked entities, only POLYLINE and INSERT has linked entities (VERTEX, ATTRIB, SEQEND)

        Yields: DXFEntity() objects

        """
        link = self.tags.link  # type: str
        wrap = self.dxffactory.wrap_handle
        while link is not None:
            entity = wrap(link)
            yield entity
            link = entity.tags.link

    def copy_to_layout(self, layout: 'GenericLayoutType') -> 'DXFEntity':
        """
        Copy entity to another layout.

        Args:
            layout: any layout (model space, paper space, block)

        Returns: new created entity as DXFEntity() object

        """
        new_entity = self.copy()
        layout.add_entity(new_entity)
        return new_entity

    def move_to_layout(self, layout: 'GenericLayoutType', source: 'GenericLayoutType' = None) -> None:
        """
        Move entity from model space or a paper space layout to another layout. For block layout as source, the
        block layout has to be specified.

        Args:
            layout: any layout (model space, paper space, block)
            source: provide source layout, faster for DXF R12, if entity is in a block layout

        """
        if source is None:
            source = self.get_layout()
            if source is None:
                raise DXFValueError('Source layout for entity not found.')
        source.move_to_layout(self, layout)

    def dxftype(self) -> str:
        return self.tags.noclass[0].value

    def _get_dxfattr_definition(self, key: str) -> 'DXFAttr':
        try:
            return self.DXFATTRIBS[key]
        except KeyError:
            raise DXFAttributeError(key)

    def get_dxf_attrib(self, key: str, default: Any = DXFValueError) -> 'TagValue':
        dxfattr = self._get_dxfattr_definition(key)
        return dxfattr.get_attrib(self, key, default)

    def set_dxf_attrib(self, key: str, value: 'TagValue') -> None:
        dxfattr = self._get_dxfattr_definition(key)
        dxfattr.set_attrib(self, key, value)

    def del_dxf_attrib(self, key: str) -> None:
        dxfattr = self._get_dxfattr_definition(key)
        dxfattr.del_attrib(self)

    def supports_dxf_attrib(self, key: str) -> bool:
        """
        Returns True if DXF attribute key is supported else False. Does not grant that attribute key really exists.

        """
        dxfattr = self.DXFATTRIBS.get(key, None)
        if dxfattr is None:
            return False
        if dxfattr.dxfversion is None:
            return True
        return self.drawing.dxfversion >= dxfattr.dxfversion

    def dxf_attrib_exists(self, key: str) -> bool:
        """
        Returns True if DXF attrib key really exists else False. Raises AttributeError if key isn't supported.

        """
        # attributes with default values don't raise an exception!
        return self.get_dxf_attrib(key, default=None) is not None

    def valid_dxf_attrib_names(self) -> Iterable[str]:
        """
        Returns a list of supported DXF attribute names.

        """
        return [key for key, attrib in self.DXFATTRIBS.items() if
                attrib.dxfversion is None or (attrib.dxfversion <= self.drawing.dxfversion)]

    def get_dxf_default_value(self, key: str) -> 'TagValue':
        """
        Returns the default value as defined in the DXF standard.

        """
        return self._get_dxfattr_definition(key).default

    def has_dxf_default_value(self, key: str) -> bool:
        """
        Returns True if the DXF attribute key has a DXF standard default value.

        """
        return self._get_dxfattr_definition(key).default is not None

    def dxfattribs(self) -> dict:
        """
        Clones defined and existing DXF attributes as dict.

        """
        dxfattribs = {}
        for key in self.DXFATTRIBS.keys():
            value = self.get_dxf_attrib(key, default=None)
            if value is not None:
                dxfattribs[key] = value
        return dxfattribs

    clone_dxf_attribs = dxfattribs

    def update_dxf_attribs(self, dxfattribs: Mapping) -> None:
        for key, value in dxfattribs.items():
            self.set_dxf_attrib(key, value)

    def set_flag_state(self, flag: int, state: bool = True, name: str = 'flags') -> None:
        flags = self.get_dxf_attrib(name, 0)
        self.set_dxf_attrib(name, set_flag_state(flags, flag, state=state))

    def get_flag_state(self, flag: int, name: str = 'flags') -> bool:
        return bool(self.get_dxf_attrib(name, 0) & flag)

    def ocs(self) -> OCS:
        extrusion = self.get_dxf_attrib('extrusion', default=(0, 0, 1))
        return OCS(extrusion)

    def destroy(self) -> None:
        if self.has_extension_dict():
            xdict = self.get_extension_dict()
            self.drawing.objects.delete_entity(xdict)

    def has_app_data(self, appid: str) -> bool:
        return self.tags.has_app_data(appid)

    def get_app_data(self, appid: str) -> Tags:
        return self.tags.get_app_data_content(appid)

    def set_app_data(self, appid: str, app_data_tags: 'IterableTags') -> None:
        if self.tags.has_app_data(appid):
            self.tags.set_app_data_content(appid, app_data_tags)
        else:
            self.tags.new_app_data(appid, app_data_tags)

    def has_xdata(self, appid: str) -> bool:
        return self.tags.has_xdata(appid)

    def get_xdata(self, appid: str) -> Tags:
        return Tags(self.tags.get_xdata(appid)[1:])  # without app id tag

    def set_xdata(self, appid: str, xdata_tags: 'IterableTags') -> None:
        if self.tags.has_xdata(appid):
            self.tags.set_xdata(appid, xdata_tags)
        else:
            self.tags.new_xdata(appid, xdata_tags)

    def has_xdata_list(self, appid: str, name: str) -> bool:
        """
        Returns if list `name` from XDATA `appid` exists.

        Args:
            appid: APPID
            name: list name

        """
        try:
            self.get_xdata_list(appid, name)
        except DXFValueError:
            return False
        else:
            return True

    def get_xdata_list(self, appid: str, name: str) -> List[Tuple]:
        """
        Get list `name` from XDATA `appid`.

        Args:
            appid: APPID
            name: list name

        Returns: list of DXFTags including list name and curly braces '{' '}' tags

        Raises:
            DXFValueError: XDATA `appid` do not exist or list `name` do not exist

        """
        xdata = self.get_xdata(appid)
        try:
            return get_named_list_from_xdata(name, xdata)
        except NotFoundException:
            raise DXFValueError('No data list "{}" not found for APPID "{}"'.format(name, appid))

    def set_xdata_list(self, appid: str, name: str, xdata_tags: 'IterableTags') -> None:
        """
        Create new list `name` of XDATA `appid` with `xdata_tags` and replaces list `name` if already exists.

        Args:
            appid: APPID
            name: list name
            xdata_tags: list content as DXFTags or (code, value) tuples, list name and curly braces '{' '}' tags will
                        be added
        """
        if not self.tags.has_xdata(appid):
            self.tags.new_xdata(appid, xdata_list(name, xdata_tags))
        else:
            self.replace_xdata_list(appid, name, xdata_tags)

    def discard_xdata_list(self, appid: str, name: str) -> None:
        """
        Deletes list `name` from XDATA `appid`. Ignores silently if XDATA `appid` or list `name` not exists.

        Args:
            appid: APPID
            name: list name

        """
        try:
            xdata = self.get_xdata(appid)
        except DXFValueError:
            pass
        else:
            try:
                tags = remove_named_list_from_xdata(name, xdata)
            except NotFoundException:
                pass
            else:
                self.set_xdata(appid, tags)

    def replace_xdata_list(self, appid: str, name: str, xdata_tags: 'IterableTags') -> None:
        """
        Replaces list `name` of existing XDATA `appid` with `xdata_tags`. Appends new list if list `name` do not exist,
        but raises `DXFValueError` if XDATA `appid` do not exist.

        Low level interface, if not sure use `set_xdata_list()` instead.

        Args:
            appid: APPID
            name: list name
            xdata_tags: list content as DXFTags or (code, value) tuples, list name and curly braces '{' '}' tags will
                        be added
        Raises:
            DXFValueError: XDATA `appid` do not exist

        """
        xdata = self.get_xdata(appid)
        try:
            tags = remove_named_list_from_xdata(name, xdata)
        except NotFoundException:
            tags = xdata
        tags.extend(xdata_list(name, xdata_tags))
        self.tags.set_xdata(appid, tags)

    def has_reactors(self) -> bool:
        return self.has_app_data(ACAD_REACTORS)

    def get_reactors(self) -> List[str]:
        reactor_tags = self.get_app_data(ACAD_REACTORS)
        return [tag.value for tag in reactor_tags]

    def set_reactors(self, reactor_handles: Iterable[str]) -> None:
        reactor_tags = [(330, handle) for handle in reactor_handles]
        self.set_app_data(ACAD_REACTORS, reactor_tags)

    def append_reactor_handle(self, handle: str) -> None:
        reactors = set(self.get_reactors())
        reactors.add(handle)
        self.set_reactors(sorted(reactors, key=lambda x: int(x, base=16)))

    def remove_reactor_handle(self, handle: str) -> None:
        reactors = set(self.get_reactors())
        reactors.discard(handle)
        self.set_reactors(reactors)

    def has_extension_dict(self) -> bool:
        return self.has_app_data(ACAD_XDICTIONARY)

    def get_extension_dict(self) -> 'DXFDictionary':
        """
        Get associated extension dictionary as DXFDictionary() object.

        """
        app_data = self.get_app_data(ACAD_XDICTIONARY)
        if len(app_data) == 0 or app_data[0].code != 360:
            raise DXFStructureError("XDICTIONARY error in entity: " + str(self))
        # are more than one XDICTIONARY possible?
        xdict_handle = app_data[0].value
        return cast('DXFDictionary', self.dxffactory.wrap_handle(xdict_handle))

    def new_extension_dict(self) -> 'DXFDictionary':
        """
        Creates and assigns a new extensions dictionary. Link to an existing extension dictionary will be lost.

        """
        xdict = self.drawing.objects.add_dictionary(owner=self.dxf.handle)
        self.set_app_data(ACAD_XDICTIONARY, [(360, xdict.dxf.handle)])
        return xdict

    def get_layout(self) -> 'GenericLayoutType':
        return self.dxffactory.get_layout_for_entity(self)

    def audit(self, auditor):
        """
        Audit entity for errors.

        Args:
            auditor: Audit() object

        """
        pass

    def has_embedded_objects(self) -> bool:
        return any(tags.has_embedded_objects() for tags in self.tags.subclasses)


OPEN_LIST = (1002, '{')
CLOSE_LIST = (1002, '}')


def xdata_list(name: str, xdata_tags: 'IterableTags') -> List[Tuple]:
    tags = []
    if name:
        tags.append((1000, name))
    tags.append(OPEN_LIST)
    tags.extend(xdata_tags)
    tags.append(CLOSE_LIST)
    return tags


def remove_named_list_from_xdata(name: str, tags: Tags) -> List[Tuple]:
    start, end = get_start_and_end_of_named_list_in_xdata(name, tags)
    del tags[start: end]
    return tags


def get_named_list_from_xdata(name: str, tags: Tags) -> List[Tuple]:
    start, end = get_start_and_end_of_named_list_in_xdata(name, tags)
    return tags[start: end]


def get_start_and_end_of_named_list_in_xdata(name: str, tags: List[Tuple]) -> Tuple[int, int]:
    start = None
    end = None
    level = 0
    for index in range(len(tags)):
        tag = tags[index]

        if start is None and tag == (1000, name):
            next_tag = tags[index + 1]
            if next_tag == OPEN_LIST:
                start = index
                continue
        if start is not None:
            if tag == OPEN_LIST:
                level += 1
            elif tag == CLOSE_LIST:
                level -= 1
            if level == 0:
                end = index
                break

    if start is None:
        raise NotFoundException
    if end is None:
        raise DXFXDataError('Invalid XDATA structure: missing  (1002, "}").')
    return start, end + 1
