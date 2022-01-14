# (c) Enzo Ruiz Pelaez
# https://github.com/enzoruiz/3dbinpacking
# License: MIT License
# Credits:
# - https://github.com/enzoruiz/3dbinpacking/blob/master/erick_dube_507-034.pdf
# - https://github.com/gedex/bp3d - implementation in GoLang
# - https://github.com/bom-d-van/binpacking - implementation in GoLang
# Refactoring and type annotations by Manfred Moitzi
from typing import Tuple, List
import enum
from ezdxf.math import Vec3, BoundingBox


class RotationType(enum.IntEnum):
    RT_WHD = 0
    RT_HWD = 1
    RT_HDW = 2
    RT_DHW = 3
    RT_DWH = 4
    RT_WDH = 5


ALL_ROTATIONS = (
    RotationType.RT_WHD,
    RotationType.RT_HWD,
    RotationType.RT_HDW,
    RotationType.RT_DHW,
    RotationType.RT_DWH,
    RotationType.RT_WDH,
)


class Axis(enum.IntEnum):
    WIDTH = 0
    HEIGHT = 1
    DEPTH = 2


DEFAULT_NUMBER_OF_DECIMALS = 3
ALL_AXIS = (Axis.WIDTH, Axis.HEIGHT, Axis.DEPTH)
START_POSITION: Tuple[float, float, float] = (0, 0, 0)


class Item:
    def __init__(
        self, name, width: float, height: float, depth: float, weight: float
    ):
        self.name = name
        self.width = float(width)
        self.height = float(height)
        self.depth = float(depth)
        self.weight = float(weight)
        self.rotation_type = RotationType.RT_WHD
        self.position = START_POSITION

    def __str__(self):
        return (
            f"{str(self.name)}({self.width}x{self.height}x{self.height}, "
            f"weight: {self.depth}) pos({str(self.position)}) "
            f"rt({self.rotation_type}) vol({self.get_volume()})"
        )

    def get_volume(self):
        return self.width * self.height * self.depth

    def get_dimension(self) -> Tuple[float, float, float]:
        rt = self.rotation_type
        if rt == RotationType.RT_WHD:
            return self.width, self.height, self.depth
        elif rt == RotationType.RT_HWD:
            return self.height, self.width, self.depth
        elif rt == RotationType.RT_HDW:
            return self.height, self.depth, self.width
        elif rt == RotationType.RT_DHW:
            return self.depth, self.height, self.width
        elif rt == RotationType.RT_DWH:
            return self.depth, self.width, self.height
        elif rt == RotationType.RT_WDH:
            return self.width, self.depth, self.height
        raise TypeError(rt)


class Bin:
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

    def get_total_weight(self) -> float:
        return sum(item.weight for item in self.items)

    def put_item(self, item: Item, pivot: Tuple[float, float, float]) -> bool:
        valid_item_position = item.position
        item.position = pivot
        x, y, z = pivot

        for rotation_type in ALL_ROTATIONS:
            item.rotation_type = rotation_type
            w, h, d = item.get_dimension()
            if self.width < x + w or self.height < y + h or self.depth < z + d:
                continue
            if (
                not any(intersect(i, item) for i in self.items)
                and self.get_total_weight() + item.weight <= self.max_weight
            ):
                self.items.append(item)
                return True

        item.position = valid_item_position
        return False


class Packer:
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
        bigger_first=False,
        distribute_items=False,
    ):
        self.bins.sort(key=lambda b: b.get_volume(), reverse=bigger_first)
        self.items.sort(key=lambda i: i.get_volume(), reverse=bigger_first)

        for bin_ in self.bins:
            for item in self.items:
                pack_to_bin(bin_, item)

            if distribute_items:
                for item in bin_.items:
                    self.items.remove(item)


def pack_to_bin(bin_: Bin, item: Item) -> None:
    if not bin_.items:
        response = bin_.put_item(item, START_POSITION)
        if not response:
            bin_.unfitted_items.append(item)
        return

    for axis in ALL_AXIS:
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


def intersect(item1: Item, item2: Item) -> bool:
    v1 = Vec3(item1.position)
    v2 = Vec3(item2.position)
    b1 = BoundingBox([v1, v1 + Vec3(item1.get_dimension())])
    b2 = BoundingBox([v2, v2 + Vec3(item2.get_dimension())])
    return b1.intersect(b2)
