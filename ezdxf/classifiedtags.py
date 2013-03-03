#!/usr/bin/env python
#coding:utf-8
# Purpose: classifiedtags
# Created: 30.04.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .tags import Tags, StringIterator, DXFStructureError, DXFTag, strtag

APP_DATA_MARKER = 102
SUBCLASS_MARKER = 100
XDATA_MARKER = 1001

NoneTag = DXFTag(None, None)


class ClassifiedTags:
    """ Manage Subclasses, AppData and Extended Data """
    __slots__ = ('subclasses', 'appdata', 'xdata')

    def __init__(self, iterable=None):
        self.appdata = list()  # code == 102, keys are "{<arbitrary name>", values are Tags()
        self.subclasses = list()  # code == 100, keys are "subclassname", values are Tags()
        self.xdata = list()  # code >= 1000, keys are "APPNAME", values are Tags()
        if iterable is not None:
            self._setup(iterable)

    @property
    def noclass(self):
        return self.subclasses[0]

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
            if subclass[0].value == name:
                if getpos >= pos:
                    return subclass
                else:
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
        for tag in self:
            stream.write(strtag(tag))

    def get_type(self):
        return self.noclass[0].value

    def get_handle(self):
        return self.noclass.get_handle()

    @staticmethod
    def fromtext(text):
        return ClassifiedTags(StringIterator(text))