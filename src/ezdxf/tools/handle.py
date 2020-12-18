# Copyright (c) 2011-2020, Manfred Moitzi
# License: MIT License
START_HANDLE = '1'


class HandleGenerator:
    def __init__(self, start_value: str = START_HANDLE):
        self._handle = max(1, int(start_value, 16))

    reset = __init__

    def __str__(self):
        return "%X" % self._handle

    def next(self) -> str:
        next_handle = str(self)
        self._handle += 1
        return next_handle

    __next__ = next


class UnderlayKeyGenerator(HandleGenerator):
    def __str__(self):
        return "Underlay%05d" % self._handle
