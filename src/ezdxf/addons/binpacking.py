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
from decimal import Decimal


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
START_POSITION: Tuple[Decimal, Decimal, Decimal] = (
    Decimal(0),
    Decimal(0),
    Decimal(0),
)


class Item:
    def __init__(self, name, width, height, depth, weight):
        self.name = name
        self.width = Decimal(width)
        self.height = Decimal(height)
        self.depth = Decimal(depth)
        self.weight = Decimal(weight)
        self.rotation_type = RotationType.RT_WHD
        self.position = START_POSITION
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS

    def format_numbers(self, number_of_decimals):
        self.width = set_to_decimal(self.width, number_of_decimals)
        self.height = set_to_decimal(self.height, number_of_decimals)
        self.depth = set_to_decimal(self.depth, number_of_decimals)
        self.weight = set_to_decimal(self.weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals

    def __str__(self):
        return (
            f"{str(self.name)}({self.width}x{self.height}x{self.height}, "
            f"weight: {self.depth}) pos({str(self.position)}) "
            f"rt({self.rotation_type}) vol({self.get_volume()})"
        )

    def get_volume(self) -> Decimal:
        return self.width * self.height * self.depth

    def get_dimension(self) -> Tuple[Decimal, Decimal, Decimal]:
        rt = self.rotation_type
        if rt == RotationType.RT_WHD:
            dimension = (self.width, self.height, self.depth)
        elif rt == RotationType.RT_HWD:
            dimension = (self.height, self.width, self.depth)
        elif rt == RotationType.RT_HDW:
            dimension = (self.height, self.depth, self.width)
        elif rt == RotationType.RT_DHW:
            dimension = (self.depth, self.height, self.width)
        elif rt == RotationType.RT_DWH:
            dimension = (self.depth, self.width, self.height)
        elif rt == RotationType.RT_WDH:
            dimension = (self.width, self.depth, self.height)
        else:
            dimension = []

        return dimension


class Bin:
    def __init__(self, name, width, height, depth, max_weight):
        self.name = name
        self.width = Decimal(width)
        self.height = Decimal(height)
        self.depth = Decimal(depth)
        self.max_weight = Decimal(max_weight)
        self.items = []
        self.unfitted_items = []
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS

    def format_numbers(self, number_of_decimals):
        self.width = set_to_decimal(self.width, number_of_decimals)
        self.height = set_to_decimal(self.height, number_of_decimals)
        self.depth = set_to_decimal(self.depth, number_of_decimals)
        self.max_weight = set_to_decimal(self.max_weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals

    def __str__(self) -> str:
        return (
            f"{str(self.name)}({self.width}x{self.height}x{self.depth}, "
            f"max_weight:{self.max_weight}) "
            f"vol({self.get_volume()})"
        )

    def get_volume(self) -> Decimal:
        return self.width * self.height * self.depth

    def get_total_weight(self) -> Decimal:
        return sum(item.weight for item in self.items)

    def put_item(
        self, item: Item, pivot: Tuple[Decimal, Decimal, Decimal]
    ) -> bool:
        valid_item_position = item.position
        item.position = pivot

        for rotation_type in ALL_ROTATIONS:
            item.rotation_type = rotation_type
            w, h, d = item.get_dimension()
            x, y, z = pivot
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
        number_of_decimals=DEFAULT_NUMBER_OF_DECIMALS,
    ):
        for bin_ in self.bins:
            bin_.format_numbers(number_of_decimals)

        for item in self.items:
            item.format_numbers(number_of_decimals)

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


def rect_intersect(item1: Item, item2: Item, x: Axis, y: Axis) -> bool:
    d1 = item1.get_dimension()
    d2 = item2.get_dimension()

    cx1 = item1.position[x] + d1[x] / 2
    cy1 = item1.position[y] + d1[y] / 2
    cx2 = item2.position[x] + d2[x] / 2
    cy2 = item2.position[y] + d2[y] / 2

    ix = max(cx1, cx2) - min(cx1, cx2)
    iy = max(cy1, cy2) - min(cy1, cy2)

    return ix < (d1[x] + d2[x]) / 2 and iy < (d1[y] + d2[y]) / 2


def intersect(item1: Item, item2: Item) -> bool:
    return (
        rect_intersect(item1, item2, Axis.WIDTH, Axis.HEIGHT)
        and rect_intersect(item1, item2, Axis.HEIGHT, Axis.DEPTH)
        and rect_intersect(item1, item2, Axis.WIDTH, Axis.DEPTH)
    )


def get_limit_number_of_decimals(number_of_decimals):
    return Decimal("1.{}".format("0" * number_of_decimals))


def set_to_decimal(value, number_of_decimals) -> Decimal:
    number_of_decimals = get_limit_number_of_decimals(number_of_decimals)

    return Decimal(value).quantize(number_of_decimals)
