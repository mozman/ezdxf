# Copyright (c) 2011-2021, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Optional

START_HANDLE = "1"

if TYPE_CHECKING:
    from ezdxf.document import Drawing


class HandleGenerator:
    def __init__(self, start_value: str = START_HANDLE):
        self._handle: int = max(1, int(start_value, 16))

    reset = __init__

    def __str__(self):
        return "%X" % self._handle

    def next(self) -> str:
        next_handle = self.__str__()
        self._handle += 1
        return next_handle

    __next__ = next


class UnderlayKeyGenerator(HandleGenerator):
    def __str__(self):
        return "Underlay%05d" % self._handle


def safe_handle(handle: Optional[str], doc: Optional["Drawing"] = None) -> str:
    if handle is None:
        return "0"
    assert isinstance(handle, str), "invalid type"
    if doc is not None:
        if handle not in doc.entitydb:
            return "0"
        return handle
    if not is_valid_handle(handle):
        return "0"
    return handle.upper()


def is_valid_handle(handle: str) -> bool:
    # duplicated code from ezdxf.lldxf.types to avoid an unnecessary dependency
    try:
        int(handle, 16)
        return True
    except (ValueError, TypeError):
        return False
