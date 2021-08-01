# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
from typing import (
    TYPE_CHECKING,
    List,
    Iterable,
    Tuple,
    Any,
    Dict,
    MutableSequence,
    MutableMapping,
)
from collections import OrderedDict
from contextlib import contextmanager
from ezdxf.math import Vec3
from ezdxf.lldxf.types import dxftag
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.const import XDATA_MARKER, DXFValueError, DXFTypeError
from ezdxf.lldxf.tags import (
    xdata_list,
    remove_named_list_from_xdata,
    get_named_list_from_xdata,
    NotFoundException,
)
from ezdxf.tools import take2
from ezdxf import options
from ezdxf.lldxf.repair import filter_invalid_xdata_group_codes
import logging

logger = logging.getLogger("ezdxf")

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFEntity

__all__ = ["XData", "XDataUserList", "XDataUserDict"]


class XData:
    def __init__(self, xdata: List[Tags] = None):
        self.data = OrderedDict()
        for data in xdata or []:
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
                logger.info(f"Duplicate XDATA appid {appid} in one entity")
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

    def export_dxf(self, tagwriter: "TagWriter") -> None:
        for appid, tags in self.data.items():
            if options.filter_invalid_xdata_group_codes:
                tags = list(filter_invalid_xdata_group_codes(tags))
            tagwriter.write_tags(tags)

    def has_xlist(self, appid: str, name: str) -> bool:
        """Returns True if list `name` from XDATA `appid` exists.

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
        """Get list `name` from XDATA `appid`.

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
                f'No data list "{name}" not found for APPID "{appid}"'
            )

    def set_xlist(self, appid: str, name: str, tags: Iterable) -> None:
        """Create new list `name` of XDATA `appid` with `xdata_tags` and
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
        """Deletes list `name` from XDATA `appid`. Ignores silently if XDATA
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
        """Replaces list `name` of existing XDATA `appid` by `tags`. Appends
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


class XDataUserList(MutableSequence):
    """Manage named XDATA lists as a list-like object.

    Stores just a few data types with fixed group codes:

        1000 str
        1010 Vec3
        1040 float
        1071 32bit int

    This class can not manage arbitrary XDATA!

    This class does not create the required AppID table entry, only the
    default AppID "EZDXF" exist by default.

    """

    converter = {
        1000: str,
        1010: Vec3,
        1040: float,
        1071: int,
    }
    group_codes = {
        str: 1000,
        Vec3: 1010,
        float: 1040,
        int: 1071,
    }

    def __init__(self, xdata: XData = None, name="DefaultList", appid="EZDXF"):
        if xdata is None:
            xdata = XData()
        self.xdata = xdata
        self._appid = str(appid)
        self._name = str(name)
        try:
            data = xdata.get_xlist(self._appid, self._name)
        except DXFValueError:
            data = []
        self._data: List = self._parse_list(data)

    @classmethod
    @contextmanager
    def entity(
        cls, entity: "DXFEntity", name="DefaultList", appid="EZDXF"
    ) -> "XDataUserList":
        xdata = entity.xdata
        if xdata is None:
            xdata = XData()
            entity.xdata = xdata
        xlist = cls(xdata, name, appid)
        yield xlist
        xlist.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()

    def __str__(self):
        return str(self._data)

    def insert(self, index: int, value) -> None:
        self._data.insert(index, value)

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, item, value) -> Any:
        self._data.__setitem__(item, value)

    def __delitem__(self, item) -> None:
        self._data.__delitem__(item)

    def _parse_list(self, tags: Iterable[Tuple]) -> List:
        data = list(tags)
        content = []
        for code, value in data[2:-1]:
            factory = self.converter.get(code)
            if factory:
                content.append(factory(value))
            else:
                raise DXFValueError(f"unsupported group code: {code}")
        return content

    def __len__(self) -> int:
        return len(self._data)

    def commit(self):
        data = []
        for value in self._data:
            if isinstance(value, str):
                if len(value) > 255:  # XDATA limit for group code 1000
                    raise DXFValueError("string too long, max. 255 characters")
                if "\n" in value or "\r" in value:
                    raise DXFValueError(
                        "found invalid line break '\\n' or '\\r'"
                    )
            code = self.group_codes.get(type(value))
            if code:
                data.append(dxftag(code, value))
            else:
                raise DXFTypeError(f"invalid type: {type(value)}")
        self.xdata.set_xlist(self._appid, self._name, data)


class XDataUserDict(MutableMapping):
    """Manage named XDATA lists as a dict-like object.

    Uses XDataUserList to store key, value pairs in XDATA.

    This class does not create the required AppID table entry, only the
    default AppID "EZDXF" exist by default.

    """

    def __init__(self, xdata: XData = None, name="DefaultDict", appid="EZDXF"):
        self._xlist = XDataUserList(xdata, name, appid)
        self._user_dict: Dict = self._parse_xlist()

    def _parse_xlist(self) -> Dict:
        if self._xlist:
            return dict(take2(self._xlist))
        else:
            return dict()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()

    def __str__(self):
        return str(self._user_dict)

    @classmethod
    @contextmanager
    def entity(
        cls, entity: "DXFEntity", name="DefaultDict", appid="EZDXF"
    ) -> "XDataUserDict":
        xdata = entity.xdata
        if xdata is None:
            xdata = XData()
            entity.xdata = xdata
        xdict = cls(xdata, name, appid)
        yield xdict
        xdict.commit()

    @property
    def xdata(self):
        return self._xlist.xdata

    def __len__(self):
        return len(self._user_dict)

    def __getitem__(self, key):
        return self._user_dict[key]

    def __setitem__(self, key, item):
        self._user_dict[key] = item

    def __delitem__(self, key):
        del self._user_dict[key]

    def __iter__(self):
        return iter(self._user_dict)

    def discard(self, key):
        try:
            del self._user_dict[key]
        except KeyError:
            pass

    def commit(self) -> None:
        xlist = self._xlist
        xlist.clear()
        for key, value in self._user_dict.items():
            xlist.append(key)
            xlist.append(value)
        xlist.commit()
