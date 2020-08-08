# Copyright (c) 2018-2020 Manfred Moitzi
# License: MIT License
from typing import Set


class Tracker:
    _dxftypes: Set[str] = set()  # track all DXF types in use

    def __contains__(self, item) -> bool:
        return item in self._dxftypes

    def __iter__(self):
        return iter(self._dxftypes)

    def add(self, dxftype: str) -> None:
        self._dxftypes.add(dxftype)
