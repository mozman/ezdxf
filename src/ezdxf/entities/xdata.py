# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
from typing import TYPE_CHECKING, List, Iterable, Tuple
from collections import OrderedDict
from ezdxf.lldxf.types import dxftag
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.const import XDATA_MARKER, DXFValueError
from ezdxf.lldxf.tags import (
    xdata_list, remove_named_list_from_xdata, get_named_list_from_xdata,
    NotFoundException,
)
from ezdxf import options
from ezdxf.lldxf.repair import filter_invalid_xdata_group_codes
import logging

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter

__all__ = ['XData', 'EmbeddedObjects']


class XData:
    def __init__(self, xdata: List[Tags] = None):
        # no back links, no self.clone() required, use deepcopy
        self.data = OrderedDict()
        for data in (xdata or []):
            self._add(data)

    def __len__(self):
        return len(self.data)

    def __contains__(self, appid: str) -> bool:
        return appid in self.data

    def _add(self, tags: Tags) -> None:
        tags = Tags(tags)
        if len(tags):
            appid = tags[0].value
            if appid in self.data:
                logger.info(f'Duplicate XDATA appid {appid} in one entity')
            self.data[appid] = tags

    def add(self, appid: str, tags: Iterable) -> None:
        data = Tags(dxftag(code, value) for code, value in tags)
        if len(data) == 0 or data[0] != (XDATA_MARKER, appid):
            data.insert(0, dxftag(XDATA_MARKER, appid))
        self._add(data)

    def get(self, appid: str) -> Tags:
        if appid in self.data:
            return self.data[appid]
        else:
            raise DXFValueError(appid)

    def discard(self, appid):
        if appid in self.data:
            del self.data[appid]

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        for appid, tags in self.data.items():
            if options.filter_invalid_xdata_group_codes:
                tags = list(filter_invalid_xdata_group_codes(tags))
            tagwriter.write_tags(tags)

    def has_xlist(self, appid: str, name: str) -> bool:
        """ Returns True if list `name` from XDATA `appid` exists.

        Args:
            appid: APPID
            name: list name

        """
        try:
            self.get_xlist(appid, name)
        except DXFValueError:
            return False
        else:
            return True

    def get_xlist(self, appid: str, name: str) -> List[Tuple]:
        """ Get list `name` from XDATA `appid`.

        Args:
            appid: APPID
            name: list name

        Returns: list of DXFTags including list name and curly braces '{' '}' tags

        Raises:
            DXFKeyError: XDATA `appid` does not exist
            DXFValueError: list `name` does not exist

        """
        xdata = self.get(appid)
        try:
            return get_named_list_from_xdata(name, xdata)
        except NotFoundException:
            raise DXFValueError(
                f'No data list "{name}" not found for APPID "{appid}"')

    def set_xlist(self, appid: str, name: str, tags: Iterable) -> None:
        """ Create new list `name` of XDATA `appid` with `xdata_tags` and
        replaces list `name` if already exists.

        Args:
            appid: APPID
            name: list name
            tags: list content as DXFTags or (code, value) tuples, list name and
                curly braces '{' '}' tags will be added
        """
        if appid not in self.data:
            data = [(XDATA_MARKER, appid)]
            data.extend(xdata_list(name, tags))
            self.add(appid, data)
        else:
            self.replace_xlist(appid, name, tags)

    def discard_xlist(self, appid: str, name: str) -> None:
        """ Deletes list `name` from XDATA `appid`. Ignores silently if XDATA
        `appid` or list `name` not exist.

        Args:
            appid: APPID
            name: list name

        """
        try:
            xdata = self.get(appid)
        except DXFValueError:
            pass
        else:
            try:
                tags = remove_named_list_from_xdata(name, xdata)
            except NotFoundException:
                pass
            else:
                self.add(appid, tags)

    def replace_xlist(self, appid: str, name: str, tags: Iterable) -> None:
        """ Replaces list `name` of existing XDATA `appid` by `tags`. Appends
        new list if list `name` do not exist, but raises `DXFValueError` if
        XDATA `appid` do not exist.

        Low level interface, if not sure use `set_xdata_list()` instead.

        Args:
            appid: APPID
            name: list name
            tags: list content as DXFTags or (code, value) tuples, list name and
                curly braces '{' '}' tags will be added
        Raises:
            DXFValueError: XDATA `appid` do not exist

        """
        xdata = self.get(appid)
        try:
            data = remove_named_list_from_xdata(name, xdata)
        except NotFoundException:
            data = xdata
        xlist = xdata_list(name, tags)
        data.extend(xlist)
        self.add(appid, data)


class EmbeddedObjects:
    """ Introduced with DXF R2018 - replaces XDATA in MTEXT entity. """

    def __init__(self, embedded_objects: List[Tags]):
        self.embedded_objects = embedded_objects

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        for tags in self.embedded_objects:
            tagwriter.write_tags(tags)
