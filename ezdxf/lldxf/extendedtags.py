# Created: 30.04.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import Iterable, Optional, Callable, List
from itertools import chain

from .types import tuples_to_tags, IterableTags
from .tags import Tags, DXFTag, NONE_TAG
from .const import DXFStructureError, DXFValueError, DXFKeyError
from .types import APP_DATA_MARKER, SUBCLASS_MARKER, XDATA_MARKER
from .types import is_app_data_marker, is_embedded_object_marker
from .tagger import internal_tag_compiler


class ExtendedTags:
    """
    Manage Subclasses, AppData and Extended Data

    """
    __slots__ = ('subclasses', 'appdata', 'xdata', 'link', 'embedded_objects')

    def __init__(self, iterable: Iterable[DXFTag] = None):
        if isinstance(iterable, str):
            raise DXFValueError("use ExtendedTags.from_text() to create tags from a string.")

        self.appdata = list()  # type: List[Tags] # code == 102, keys are "{<arbitrary name>", values are Tags()
        self.subclasses = list()  # type: List[Tags] # code == 100, keys are "subclassname", values are Tags()
        self.xdata = list()  # type: List[Tags] # code >= 1000, keys are "APPNAME", values are Tags()
        self.link = None  # type: Optional[str] # link (as handle) to following entities like INSERT -> ATTRIB and POLYLINE -> VERTEX

        # store embedded objects as list, but embedded objects are rare, so storing an empty list for every DXF entity
        # is waste of memory
        self.embedded_objects = None  # type: Optional[List[Tags]]
        if iterable is not None:
            self._setup(iterable)

    def __copy__(self) -> 'ExtendedTags':
        """
        Shallow copy - linked entities are not duplicated!

        ExtendedTags() knows nothing about the entity database, and has no access to, so it is not possible for
        ExtendedTags() to do a deep copy, by also copying linked entities (VERTEX, ATTRIB, SEQEND).
        To do a deep copy you have to go one level up and use DXFEntity.copy()

        """

        def copy(tag_lists):
            return [tags.clone() for tags in tag_lists]

        clone = self.__class__()
        clone.appdata = copy(self.appdata)
        clone.subclasses = copy(self.subclasses)
        clone.xdata = copy(self.xdata)
        if self.embedded_objects is not None:
            clone.embedded_objects = copy(self.embedded_objects)
        clone.link = self.link  # important for dxf importer!
        return clone

    clone = __copy__

    def __getitem__(self, index) -> Tags:
        return self.noclass[index]

    @property
    def noclass(self) -> Tags:
        return self.subclasses[0]

    def get_handle(self) -> str:
        return self.noclass.get_handle()

    def dxftype(self) -> str:
        return self.noclass[0].value

    def replace_handle(self, handle: str) -> None:
        self.noclass.replace_handle(handle)

    def _setup(self, iterable: Iterable[DXFTag]) -> None:
        tagstream = iter(iterable)

        def collect_subclass(starttag: Optional[DXFTag]) -> DXFTag:
            """
            A subclass can contain appdata, but not XDATA, ends with
            SUBCLASS_MARKER, XDATA_MARKER or EMBEDDED_OBJ_MARKER.

            """
            # All subclasses begin with (100, subclass name)
            # EXCEPT DIMASSOC has one subclass starting with: (1, AcDbOsnapPointRef). Well done, Autodesk!
            # This special subclass is ignored by ezdxf, content is included in the preceding subclass: (100, AcDbDimAssoc)
            #
            # TEXT contains 2x the (100, AcDbText). Also well done, Autodesk! Therefore it is not possible to use an
            # (ordered) dict where subclass name is key, but usual use case is access by index.

            data = Tags() if starttag is None else Tags([starttag])
            try:
                while True:
                    tag = next(tagstream)
                    if is_app_data_marker(tag):
                        app_data_pos = len(self.appdata)
                        data.append(DXFTag(tag.code, app_data_pos))
                        collect_app_data(tag)
                    elif tag.code in (SUBCLASS_MARKER, XDATA_MARKER) or is_embedded_object_marker(tag):
                        self.subclasses.append(data)
                        return tag
                    else:
                        data.append(tag)
            except StopIteration:
                pass
            self.subclasses.append(data)
            return NONE_TAG

        def collect_app_data(starttag: DXFTag) -> None:
            """
            Appdata, cannot contain XDATA or subclasses.

            """
            data = Tags([starttag])
            closing_strings = ('}', starttag.value[1:] + '}')  # alternative closing tag 'APPID}'
            while True:
                try:
                    tag = next(tagstream)
                except StopIteration:
                    raise DXFStructureError("Missing closing (102, '}') tag for appdata structure.")
                data.append(tag)
                if (tag.code == APP_DATA_MARKER) and (tag.value in closing_strings):
                    break
                    # every other (102, ) tag is treated as usual tag
            self.appdata.append(data)

        def collect_xdata(starttag: DXFTag) -> DXFTag:
            """
            XDATA is always at the end of the entity and can not contain appdata or subclasses

            NEW: 09.08.2018

            Since AutoCAD 2018, DXF entities can contain embedded objects, this objects appear at the end of an entity,
            after XDATA (if XDATA exists).

            """
            data = Tags([starttag])
            try:
                while True:
                    tag = next(tagstream)
                    if tag.code == XDATA_MARKER:
                        self.xdata.append(data)
                        return tag
                    else:
                        data.append(tag)
            except StopIteration:
                pass
            self.xdata.append(data)
            return NONE_TAG

        def collect_embedded_object(starttag: DXFTag) -> DXFTag:
            """
            Since AutoCAD 2018, DXF entities can contain embedded objects, this objects appear at the end of an entity,
            also after XDATA, and start with the (101, 'Embedded Object') tag.

            All embedded object data is collected in a simple Tags() object, no subclass app data or XDATA processing is
            done. ezdxf does not use or modify the embedded object data, the data is just stored and written out as it
            is.

            self.embedded_objects = [1. embedded object as Tags(), 2. embedded object as Tags(), ...]

            """
            if self.embedded_objects is None:
                self.embedded_objects = list()
            data = Tags([starttag])
            try:
                while True:
                    tag = next(tagstream)
                    if is_embedded_object_marker(tag):
                        # another embedded object found, don't know if an DXF entity can contain more than one embedded
                        # objects
                        self.embedded_objects.append(data)
                        return tag
                    else:
                        data.append(tag)
            except StopIteration:
                pass
            self.embedded_objects.append(data)
            return NONE_TAG

        tag = collect_subclass(None)  # preceding tags without a subclass
        while tag.code == SUBCLASS_MARKER:
            tag = collect_subclass(tag)

        if not is_embedded_object_marker(tag):
            # XDATA can not appear after an embedded object
            while tag.code == XDATA_MARKER:
                tag = collect_xdata(tag)

        while is_embedded_object_marker(tag):
            tag = collect_embedded_object(tag)

        if tag is not NONE_TAG:
            raise DXFStructureError("Unexpected tag '%r' at end of entity." % tag)

    def __iter__(self) -> Iterable[DXFTag]:
        for subclass in self.subclasses:
            for tag in subclass:
                if tag.code == APP_DATA_MARKER and isinstance(tag.value, int):
                    yield from self.appdata[tag.value]
                else:
                    yield tag

        yield from chain.from_iterable(self.xdata)

        if self.embedded_objects is not None:
            yield from chain.from_iterable(self.embedded_objects)

    def get_subclass(self, name: str, pos: int = 0) -> Tags:
        for index, subclass in enumerate(self.subclasses):
            try:
                if (index >= pos) and (subclass[0].value == name):
                    return subclass
            except IndexError:
                pass  # subclass[0]: ignore empty subclasses

        raise DXFKeyError("Subclass '%s' does not exist." % name)

    def has_xdata(self, appid: str) -> bool:
        return any(xdata[0].value == appid for xdata in self.xdata)

    def get_xdata(self, appid: str) -> Tags:
        for xdata in self.xdata:
            if xdata[0].value == appid:
                return xdata
        raise DXFValueError("No extended data for APPID '%s'" % appid)

    def set_xdata(self, appid: str, tags: IterableTags) -> None:
        xdata = self.get_xdata(appid)
        xdata[1:] = tuples_to_tags(tags)

    def new_xdata(self, appid: str, tags: IterableTags = None) -> Tags:
        """
        Append a new xdata block.

        Assumes that no xdata block with the same appid already exists::

            try:
                xdata = tags.get_xdata('EZDXF')
            except ValueError:
                xdata = tags.new_xdata('EZDXF')
        """
        xtags = Tags([DXFTag(XDATA_MARKER, appid)])
        if tags is not None:
            xtags.extend(tuples_to_tags(tags))
        self.xdata.append(xtags)
        return xtags

    def has_app_data(self, appid: str) -> bool:
        return any(appdata[0].value == appid for appdata in self.appdata)

    def get_app_data(self, appid: str) -> Tags:
        """
        Get app data including first and last marker tag.

        """
        for appdata in self.appdata:
            if appdata[0].value == appid:
                return appdata
        raise DXFValueError("Application defined group '%s' does not exist." % appid)

    def get_app_data_content(self, appid: str) -> Tags:
        """
        Get app data without first and last marker tag.

        """
        return Tags(self.get_app_data(appid)[1:-1])

    def set_app_data_content(self, appid: str, tags: IterableTags) -> None:
        app_data = self.get_app_data(appid)
        app_data[1:-1] = tuples_to_tags(tags)

    def new_app_data(self, appid: str, tags: IterableTags = None, subclass_name: str = None) -> Tags:
        """
        Append a new app data block to subclass *subclass_name*.

        Assumes that no app data block with the same appid already exists::

            try:
                app_data = tags.get_app_data('{ACAD_REACTORS', tags)
            except ValueError:
                app_data = tags.new_app_data('{ACAD_REACTORS', tags)

        """
        if not appid.startswith('{'):
            raise DXFValueError("App data id has to start with '{'.")

        app_tags = Tags([
            DXFTag(APP_DATA_MARKER, appid),
            DXFTag(APP_DATA_MARKER, '}'),
        ])
        if tags is not None:
            app_tags[1:1] = tuples_to_tags(tags)

        if subclass_name is None:
            subclass = self.noclass
        else:
            subclass = self.get_subclass(subclass_name, 1)  # raises KeyError, if not exists
        app_data_pos = len(self.appdata)
        subclass.append(DXFTag(APP_DATA_MARKER, app_data_pos))
        self.appdata.append(app_tags)
        return app_tags

    @classmethod
    def from_text(cls, text: str) -> 'ExtendedTags':
        return cls(internal_tag_compiler(text))


LINKED_ENTITIES = {
    'INSERT': 'ATTRIB',
    'POLYLINE': 'VERTEX'
}


def get_xtags_linker() -> Callable[[ExtendedTags], bool]:
    prev = None  # type: Optional[ExtendedTags]
    expected = ""

    def xtags_linker(tags: ExtendedTags) -> bool:
        nonlocal prev, expected
        handle = tags.get_handle()

        def attribs_follow() -> bool:
            try:
                ref_tags = tags.get_subclass('AcDbBlockReference')
            except DXFKeyError:
                return False
            else:
                return bool(ref_tags.get_first_value(66, 0))

        dxftype = tags.dxftype()  # type: str
        are_linked_tags = False  # INSERT & POLYLINE are not linked tags, they are stored in the entity space
        if prev is not None:
            are_linked_tags = True  # VERTEX, ATTRIB & SEQEND are linked tags, they are NOT stored in the entity space
            if dxftype == 'SEQEND':
                prev.link = handle
                prev = None
            # check for valid DXF structure just VERTEX follows POLYLINE and just ATTRIB follows INSERT
            elif dxftype == expected:
                prev.link = handle
                prev = tags
            else:
                raise DXFStructureError("expected DXF entity {} or SEQEND".format(dxftype))
        elif dxftype in ('INSERT', 'POLYLINE'):  # only these two DXF types have this special linked structure
            if dxftype == 'INSERT' and not attribs_follow():
                # INSERT must not have following ATTRIBS, ATTRIB can be a stand alone entity:
                #   INSERT with no ATTRIBS, attribs_follow == 0
                #   ATTRIB as stand alone entity
                #   ....
                #   INSERT with ATTRIBS, attribs_follow == 1
                #   ATTRIB as connected entity
                #   SEQEND
                #
                # Therefore a ATTRIB following an INSERT doesn't mean that these entities are connected.
                pass
            else:
                prev = tags
                expected = LINKED_ENTITIES[dxftype]
        return are_linked_tags  # caller should know, if *tags* should be stored in the entity space or not

    return xtags_linker
