# (c) Enzo Ruiz Pelaez
# https://github.com/enzoruiz/3dbinpacking
# License: MIT License
# Credits:
# - https://github.com/enzoruiz/3dbinpacking/blob/master/erick_dube_507-034.pdf
# - https://github.com/gedex/bp3d - implementation in GoLang
# - https://github.com/bom-d-van/binpacking - implementation in GoLang
# Refactoring and type annotations by Manfred Moitzi
from typing import Tuple, List, Iterable, Any
import enum
import abc
from ezdxf.math import Vec3, BoundingBox

__all__ = ["Item", "Bin2d", "Bin3d", "Packer2d", "Packer3d", "RotationType"]


class RotationType(enum.IntEnum):
    WHD = 0
    HWD = 1
    HDW = 2
    DHW = 3
    DWH = 4
    WDH = 5


class Axis(enum.IntEnum):
    WIDTH = 0
    HEIGHT = 1
    DEPTH = 2


START_POSITION: Tuple[float, float, float] = (0, 0, 0)


class Item:
    def __init__(
        self,
        payload,
        width: float,
        height: float,
        depth: float = 1.0,  # has to be 1.0 for 2d packing: volume == area
        weight: float = 0.0,
    ):
        self.payload = payload  # arbitrary associated Python object
        self.width = float(width)
        self.height = float(height)
        self.depth = float(depth)
        self.weight = float(weight)
        self._rotation_type = RotationType.WHD
        self._position = START_POSITION
        self._bbox = BoundingBox()
        self._update_bbox()

    def _update_bbox(self) -> None:
        v1 = Vec3(self._position)
        self._bbox = BoundingBox([v1, v1 + Vec3(self.get_dimension())])

    @property
    def bbox(self) -> BoundingBox:
        return self._bbox

    @property
    def rotation_type(self) -> RotationType:
        return self._rotation_type

    @rotation_type.setter
    def rotation_type(self, value: RotationType) -> None:
        self._rotation_type = value
        self._update_bbox()

    @property
    def position(self) -> Tuple[float, float, float]:
        return self._position

    @position.setter
    def position(self, value: Tuple[float, float, float]) -> None:
        self._position = value
        self._update_bbox()

    def __str__(self):
        return (
            f"{str(self.payload)}({self.width}x{self.height}x{self.height}, "
            f"weight: {self.depth}) pos({str(self.position)}) "
            f"rt({self.rotation_type}) vol({self.get_volume()})"
        )

    def get_volume(self):
        return self.width * self.height * self.depth

    def get_dimension(self) -> Tuple[float, float, float]:
        rt = self.rotation_type
        if rt == RotationType.WHD:
            return self.width, self.height, self.depth
        elif rt == RotationType.HWD:
            return self.height, self.width, self.depth
        elif rt == RotationType.HDW:
            return self.height, self.depth, self.width
        elif rt == RotationType.DHW:
            return self.depth, self.height, self.width
        elif rt == RotationType.DWH:
            return self.depth, self.width, self.height
        elif rt == RotationType.WDH:
            return self.width, self.depth, self.height
        raise TypeError(rt)


class Bin(abc.ABC):
    items: List[Item]
    unfitted_items: List[Item]
    name: Any
    width: float
    height: float
    depth: float
    max_weight: float

    def put_item(self, item: Item, pivot: Tuple[float, float, float]) -> bool:
        valid_item_position = item.position
        item.position = pivot
        x, y, z = pivot

        for rotation_type in self.rotations():
            item.rotation_type = rotation_type
            w, h, d = item.get_dimension()
            if self.width < x + w or self.height < y + h or self.depth < z + d:
                continue
            item_bbox = item.bbox
            if (
                not any(item_bbox.intersect(i.bbox) for i in self.items)
                and self.get_total_weight() + item.weight <= self.max_weight
            ):
                self.items.append(item)
                return True

        item.position = valid_item_position
        return False

    def get_total_weight(self) -> float:
        return sum(item.weight for item in self.items)

    @abc.abstractmethod
    def rotations(self) -> Iterable[RotationType]:
        ...

    @abc.abstractmethod
    def get_volume(self) -> float:
        ...


class Bin3d(Bin):
    def __init__(
        self, name, width: float, height: float, depth: float, max_weight: float
    ):
        self.name = name
        self.width = float(width)
        self.height = float(height)
        self.depth = float(depth)
        self.max_weight = float(max_weight)
        self.items: List[Item] = []
        self.unfitted_items: List[Item] = []

    def __str__(self) -> str:
        return (
            f"{str(self.name)}({self.width}x{self.height}x{self.depth}, "
            f"max_weight:{self.max_weight}) "
            f"vol({self.get_volume()})"
        )

    def get_volume(self) -> float:
        return self.width * self.height * self.depth

    def rotations(self) -> Iterable[RotationType]:
        return RotationType


class Bin2d(Bin):
    def __init__(self, name, width: float, height: float, max_weight: float):
        self.name = name
        self.width = float(width)
        self.height = float(height)
        self.depth = 1.0
        self.max_weight = float(max_weight)
        self.items: List[Item] = []
        self.unfitted_items: List[Item] = []

    def __str__(self) -> str:
        return (
            f"{str(self.name)}({self.width}x{self.height}, "
            f"max_weight:{self.max_weight}) "
            f"area({self.get_volume()})"
        )

    def rotations(self) -> Iterable[RotationType]:
        return RotationType.WHD, RotationType.HWD

    def get_volume(self) -> float:
        return self.width * self.height


class Packer(abc.ABC):
    def __init__(self):
        self.bins: List[Bin] = []
        self.items: List[Item] = []
        self.unfit_items: List[Item] = []

    def add_bin(self, bin_: Bin) -> None:
        self.bins.append(bin_)

    def add_item(self, item: Item) -> None:
        self.items.append(item)

    def pack(
        self,
        *,
        bigger_first=True,  # only this strategy works!
        distribute_items=False,
    ):
        self.bins.sort(key=lambda b: b.get_volume(), reverse=bigger_first)
        self.items.sort(key=lambda i: i.get_volume(), reverse=bigger_first)

        for bin_ in self.bins:
            for item in self.items:
                self.pack_to_bin(bin_, item)

            if distribute_items:
                for item in bin_.items:
                    self.items.remove(item)

    @staticmethod
    @abc.abstractmethod
    def pack_to_bin(bin_: Bin, item: Item) -> None:
        ...


class Packer3d(Packer):
    @staticmethod
    def pack_to_bin(bin_: Bin, item: Item) -> None:
        if not bin_.items:
            response = bin_.put_item(item, START_POSITION)
            if not response:
                bin_.unfitted_items.append(item)
            return

        for axis in Axis:
            for ib in bin_.items:
                w, h, d = ib.get_dimension()
                x, y, z = ib.position
                if axis == Axis.WIDTH:
                    pivot = (x + w, y, z)
                elif axis == Axis.HEIGHT:
                    pivot = (x, y + h, z)
                elif axis == Axis.DEPTH:
                    pivot = (x, y, z + d)
                else:
                    raise TypeError(axis)
                if bin_.put_item(item, pivot):
                    return
        bin_.unfitted_items.append(item)


class Packer2d(Packer):
    @staticmethod
    def pack_to_bin(bin_: Bin, item: Item) -> None:
        if not bin_.items:
            response = bin_.put_item(item, START_POSITION)
            if not response:
                bin_.unfitted_items.append(item)
            return

        for axis in (Axis.WIDTH, Axis.HEIGHT):
            for ib in bin_.items:
                w, h, _ = ib.get_dimension()
                x, y, _ = ib.position
                if axis == Axis.WIDTH:
                    pivot = (x + w, y, 0)
                elif axis == Axis.HEIGHT:
                    pivot = (x, y + h, 0)
                else:
                    raise TypeError(axis)
                if bin_.put_item(item, pivot):
                    return
        bin_.unfitted_items.append(item)
