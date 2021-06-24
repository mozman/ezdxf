#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
"""Store user data in a XRECORD entity

The implementation has a list like interface.
All supported data types have a fixed group code:

- str: 1
- int: 90 - 32-bit values
- float: 40 - doubles
- Vec3: 10, 20, 30
- Vec2: 11, 21
- list: starts with tag (3, "[") and ends with tag (3, "]")
- dict: starts with tag (4, "{") and ends with tag (4, "}")

"""
from typing import List, Any
from ezdxf.lldxf import const
from ezdxf.entities import XRecord
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.types import dxftag
from ezdxf.math import Vec3, Vec2
from ezdxf.tools import take2

TYPE_GROUP_CODE = 2
STR_GROUP_CODE = 1
INT_GROUP_CODE = 90
FLOAT_GROUP_CODE = 40
VEC3_GROUP_CODE = 10
VEC2_GROUP_CODE = 11
COLLECTION_GROUP_CODE = 302
START_LIST = "["
END_LIST = "]"
START_DICT = "{"
END_DICT = "}"

__all__ = ["UserRecord"]


class UserRecord:
    def __init__(self, xrecord: XRecord = None, name: str = "UserRecord"):
        if xrecord is None:
            xrecord = XRecord.new()
        self.xrecord = xrecord
        self.name = str(name)
        self._data = parse_xrecord(self.xrecord, self.name)

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

    def commit(self) -> XRecord:
        tags = Tags()
        tags.append(dxftag(TYPE_GROUP_CODE, self.name))
        self.xrecord.tags = tags
        return self.xrecord


def parse_xrecord(xrecord: XRecord, name: str) -> List:
    data = []
    tags = xrecord.tags
    if tags:
        code, value = tags[0]
        if code != TYPE_GROUP_CODE and value != name:
            raise TypeError(
                f"{str(xrecord)} is not an user record of type {name}"
            )
        data.extend(item for item in parse_items(tags[1:]))
    return data


def parse_items(tags: Tags) -> List[Any]:
    stack = []
    items = []
    for tag in tags:
        code, value = tag
        if code == STR_GROUP_CODE:
            items.append(str(value))
        elif code == INT_GROUP_CODE:
            items.append(int(value))
        elif code == FLOAT_GROUP_CODE:
            items.append(float(value))
        elif code == VEC3_GROUP_CODE:
            items.append(Vec3(value))
        elif code == VEC2_GROUP_CODE:
            items.append(Vec2(value))
        elif code == COLLECTION_GROUP_CODE and (
            value == START_LIST or value == START_DICT
        ):
            stack.append(items)
            items = []
        elif code == COLLECTION_GROUP_CODE and (
            value == END_LIST or value == END_DICT
        ):
            try:
                prev_level = stack.pop()
            except IndexError:
                raise const.DXFStructureError(
                    f"invalid nested structure, mismatch of structure tags"
                    f" ({COLLECTION_GROUP_CODE}, ...)"
                )
            if value == END_DICT:
                items = dict(take2(items))
            prev_level.append(items)
            items = prev_level
        else:
            raise ValueError(f"invalid group code in tag: ({code}, {value})")
    if stack:
        raise const.DXFStructureError(
            f"invalid nested structure, mismatch of structure tags"
            f"({COLLECTION_GROUP_CODE}, ...)"
        )
    return items
