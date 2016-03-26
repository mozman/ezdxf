# Purpose: classified tags
# Created: 30.04.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .tags import Tags, StringIterator, DXFStructureError, DXFTag, write_tags
from ..tools.c23 import isstring

APP_DATA_MARKER = 102
SUBCLASS_MARKER = 100
XDATA_MARKER = 1001

NoneTag = DXFTag(None, None)


class ClassifiedTags(object):
    """ Manage Subclasses, AppData and Extended Data """
    __slots__ = ('subclasses', 'appdata', 'xdata', 'link')

    def __init__(self, iterable=None):
        if isstring(iterable):
            raise ValueError("use ClassifiedTags.from_text() to create tags from a string.")

        self.appdata = list()  # code == 102, keys are "{<arbitrary name>", values are Tags()
        self.subclasses = list()  # code == 100, keys are "subclassname", values are Tags()
        self.xdata = list()  # code >= 1000, keys are "APPNAME", values are Tags()
        self.link = None  # link to following entities like INSERT -> ATTRIB and POLYLINE -> VERTEX
        if iterable is not None:
            self._setup(iterable)

    def __copy__(self):
        def copy(tag_lists):
            return [tags.clone() for tags in tag_lists]

        clone = self.__class__()
        clone.appdata = copy(self.appdata)
        clone.subclasses = copy(self.subclasses)
        clone.xdata = copy(self.xdata)
        clone.link = self.link  # important for dxf importer!
        return clone

    clone = __copy__

    @property
    def noclass(self):
        return self.subclasses[0]

    def replace_handle(self, handle):
        self.noclass.replace_handle(handle)

    def _setup(self, iterable):
        tagstream = iter(iterable)

        def isappdata(tag):
            return tag.code == APP_DATA_MARKER and tag.value.startswith('{')

        def collect_subclass(starttag):
            """ a subclass can contain appdata, but not xdata, ends with
            SUBCLASSMARKER or XDATACODE.
            """
            data = Tags() if starttag is None else Tags([starttag])
            try:
                while True:
                    tag = next(tagstream)
                    if isappdata(tag):
                        appdatapos = len(self.appdata)
                        data.append(DXFTag(tag.code, appdatapos))
                        collect_appdata(tag)
                    elif tag.code in (SUBCLASS_MARKER, XDATA_MARKER):
                        self.subclasses.append(data)
                        return tag
                    else:
                        data.append(tag)
            except StopIteration:
                pass
            self.subclasses.append(data)
            return NoneTag

        def collect_appdata(starttag):
            """ appdata, cannot contain xdata or subclasses """
            data = Tags([starttag])
            while True:
                try:
                    tag = next(tagstream)
                except StopIteration:
                    raise DXFStructureError("Missing closing DXFTag(102, '}') for appdata structure.")
                data.append(tag)
                if tag.code == APP_DATA_MARKER:
                    break
            self.appdata.append(data)

        def collect_xdata(starttag):
            """ xdata are always at the end of the entity and can not contain
            appdata or subclasses
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
            return NoneTag

        tag = collect_subclass(None)  # preceding tags without a subclass
        while tag.code == SUBCLASS_MARKER:
            tag = collect_subclass(tag)
        while tag.code == XDATA_MARKER:
            tag = collect_xdata(tag)

        if tag is not NoneTag:
            raise DXFStructureError("Unexpected tag '%r' at end of entity." % tag)

    def __iter__(self):
        for subclass in self.subclasses:
            for tag in subclass:
                if tag.code == APP_DATA_MARKER and isinstance(tag.value, int):
                    for subtag in self.appdata[tag.value]:
                        yield subtag
                else:
                    yield tag

        for xdata in self.xdata:
            for tag in xdata:
                yield tag

    def get_subclass(self, name, pos=0):
        getpos = 0
        for subclass in self.subclasses:
            if len(subclass) and subclass[0].value == name and getpos >= pos:
                return subclass
            getpos += 1
        raise KeyError("Subclass '%s' does not exist." % name)

    def get_xdata(self, appid):
        for xdata in self.xdata:
            if xdata[0].value == appid:
                return xdata
        raise ValueError("No extended data for APPID '%s'" % appid)

    def get_appdata(self, name):
        for appdata in self.appdata:
            if appdata[0].value == name:
                return appdata
        raise ValueError("Application defined group '%s' does not exist." % name)

    def write(self, stream):
        write_tags(stream, self)

    def dxftype(self):
        return self.noclass[0].value

    def get_handle(self):
        return self.noclass.get_handle()

    @classmethod
    def from_text(cls, text):
        return cls(StringIterator(text))

LINKED_ENTITIES = {
    'INSERT': 'ATTRIB',
    'POLYLINE': 'VERTEX'
}


def get_tags_linker():
    class PersitentVars(object):  # Python 2.7 has no nonlocal statement
        def __init__(self):
            self.prev = None
            self.expected = ""

    def tags_linker(tags, handle):
        # Parameter handle is necessary, because DXF12 did not require a handle, therefor the
        # handle isn't stored in tags and tags.get_handle() fails with an ValueError
        def attribs_follow():
            try:
                ref_tags = tags.get_subclass('AcDbBlockReference')
            except KeyError:
                return False
            else:
                return bool(ref_tags.find_first(66, 0))

        dxftype = tags.dxftype()
        are_linked_tags = False  # INSERT & POLYLINE are not linked tags, they are stored in the entity space
        if vars.prev is not None:
            are_linked_tags = True  # VERTEX, ATTRIB & SEQEND are linked tags, they are NOT stored in the entity space
            if dxftype == 'SEQEND':
                vars.prev.link = handle
                vars.prev = None
            # check for valid DXF structure just VERTEX follows POLYLINE and just ATTRIB follows INSERT
            elif dxftype == vars.expected:
                vars.prev.link = handle
                vars.prev = tags
            else:
                raise DXFStructureError("expected DXF entity %s or SEQEND" % dxftype)
        elif dxftype in ('INSERT', 'POLYLINE'):  # only these two DXF types have this special linked structure
            if dxftype == 'INSERT' and not attribs_follow():
                # INSERT must not have following ATTRIBS, ATTRIB can be a stand alone entity:
                #   INSERT with no ATTRIBS, attribs_follow == 0
                #   ATTRIB as stand alone entity
                #   INSERT with ATTRIBS, attribs_follow == 1
                #   ATTRIB as connected entity
                #   SEQEND
                #
                # Therefor a ATTRIB following an INSERT doesn't mean that these entities are connected.
                pass
            else:
                vars.prev = tags
                vars.expected = LINKED_ENTITIES[dxftype]
        return are_linked_tags  # caller should know, if *tags* should be stored in the entity space or not

    vars = PersitentVars()
    return tags_linker
