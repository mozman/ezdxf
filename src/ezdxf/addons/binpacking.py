# (c) Enzo Ruiz Pelaez
# https://github.com/enzoruiz/3dbinpacking
# License: MIT License
# Credits:
# - https://github.com/enzoruiz/3dbinpacking/blob/master/erick_dube_507-034.pdf
# - https://github.com/gedex/bp3d - implementation in GoLang
# - https://github.com/bom-d-van/binpacking - implementation in GoLang
# Refactoring and type annotations by Manfred Moitzi
from typing import Tuple, List, Iterable
from enum import Enum, auto

from ezdxf.math import (
    Vec2,
    Vec3,
    BoundingBox,
    BoundingBox2d,
    AbstractBoundingBox,
)

__all__ = [
    "Item",
    "FlatItem",
    "Box",  # contains Item
    "Envelope",  # contains FlatItem
    "Packer",
    "RotationType",
    "PickStrategy",
]

UNLIMITED_WEIGHT = 1e99


class RotationType(Enum):
    WHD = auto()
    HWD = auto()
    HDW = auto()
    DHW = auto()
    DWH = auto()
    WDH = auto()


class Axis(Enum):
    WIDTH = auto()
    HEIGHT = auto()
    DEPTH = auto()


class PickStrategy(Enum):
    SMALLER_FIRST = auto()
    BIGGER_FIRST = auto()


START_POSITION: Tuple[float, float, float] = (0, 0, 0)


class Item:
    def __init__(
        self,
        payload,
        width: float,
        height: float,
        depth: float,
        weight: float = 0.0,
    ):
        self.payload = payload  # arbitrary associated Python object
        self.width = float(width)
        self.height = float(height)
        self.depth = float(depth)
        self.weight = float(weight)
        self._rotation_type = RotationType.WHD
        self._position = START_POSITION
        self._bbox: AbstractBoundingBox = BoundingBox()
        self._update_bbox()

    def get_volume(self):
        return self.width * self.height * self.depth

    def _update_bbox(self) -> None:
        v1 = Vec3(self._position)
        self._bbox = BoundingBox([v1, v1 + Vec3(self.get_dimension())])

    def __str__(self):
        return (
            f"{str(self.payload)}({self.width}x{self.height}x{self.depth}, "
            f"weight: {self.weight}) pos({str(self.position)}) "
            f"rt({self.rotation_type}) vol({self.get_volume()})"
        )

    @property
    def bbox(self) -> AbstractBoundingBox:
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
        raise ValueError(rt)


class FlatItem(Item):
    def __init__(
        self,
        payload,
        width: float,
        height: float,
        weight: float = 0.0,
    ):
        super().__init__(payload, width, height, 1.0, weight)

    def get_volume(self):
        return self.width * self.height

    def _update_bbox(self) -> None:
        v1 = Vec2(self._position)
        self._bbox = BoundingBox2d([v1, v1 + Vec2(self.get_dimension())])

    def __str__(self):
        return (
            f"{str(self.payload)}({self.width}x{self.height}, "
            f"weight: {self.weight}) pos({str(self.position)}) "
            f"rt({self.rotation_type}) area({self.get_volume()})"
        )


class Bin:
    def __init__(
        self,
        name,
        width: float,
        height: float,
        depth: float,
        max_weight: float = UNLIMITED_WEIGHT,
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
            f"{str(self.name)}({self.width:.3f}x{self.height:.3f}x{self.depth:.3f}, "
            f"max_weight:{self.max_weight}) "
            f"vol({self.get_volume():.3f})"
        )

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

    def get_volume(self) -> float:
        return self.width * self.height * self.depth

    def rotations(self) -> Iterable[RotationType]:
        return RotationType


class Box(Bin):
    pass


class Envelope(Bin):
    def __init__(
        self,
        name,
        width: float,
        height: float,
        max_weight: float = UNLIMITED_WEIGHT,
    ):
        super().__init__(name, width, height, 1.0, max_weight)

    def __str__(self) -> str:
        return (
            f"{str(self.name)}({self.width:.3f}x{self.height:.3f}, "
            f"max_weight:{self.max_weight}) "
            f"area({self.get_volume():.3f})"
        )

    def rotations(self) -> Iterable[RotationType]:
        return RotationType.WHD, RotationType.HWD

    def get_volume(self) -> float:
        return self.width * self.height


class _Packer:
    def __init__(self):
        self.bins: List[Bin] = []
        self.items: List[Item] = []
        self.unfit_items: List[Item] = []

    def __str__(self) -> str:
        return f"{self.__class__.__name__} with {len(self.bins)} bins"

    def add_bin(self, bin_: Bin) -> None:
        self.bins.append(bin_)

    def add_item(self, item: Item) -> None:
        self.items.append(item)

    def pack(
        self,
        *,
        pick_strategy=PickStrategy.BIGGER_FIRST,
        distribute_items=False,
    ):
        reverse = True if pick_strategy == PickStrategy.BIGGER_FIRST else False
        self.bins.sort(key=lambda b: b.get_volume(), reverse=reverse)
        self.items.sort(key=lambda i: i.get_volume(), reverse=reverse)

        for bin_ in self.bins:
            for item in self.items:
                self.pack_to_bin(bin_, item)

            if distribute_items:
                for item in bin_.items:
                    self.items.remove(item)

    @staticmethod
    def pack_to_bin(box: Bin, item: Item) -> None:
        pass


class Packer(_Packer):
    def new_box(
        self,
        name: str,
        width: float,
        height: float,
        depth: float,
        max_weight: float = UNLIMITED_WEIGHT,
    ) -> Box:
        box = Box(name, width, height, depth, max_weight)
        self.add_bin(box)
        return box

    def new_item(
        self,
        payload,
        width: float,
        height: float,
        depth: float,
        weight: float = 0.0,
    ) -> Item:
        item = Item(payload, width, height, depth, weight)
        self.add_item(item)
        return item

    @staticmethod
    def pack_to_bin(box: Bin, item: Item) -> None:
        if not box.items:
            response = box.put_item(item, START_POSITION)
            if not response:
                box.unfitted_items.append(item)
            return

        for axis in Axis:
            for ib in box.items:
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
                if box.put_item(item, pivot):
                    return
        box.unfitted_items.append(item)


class FlatPacker(_Packer):
    def new_envelope(
        self,
        name: str,
        width: float,
        height: float,
        max_weight: float = UNLIMITED_WEIGHT,
    ) -> Envelope:
        envelope = Envelope(name, width, height, max_weight)
        self.add_bin(envelope)
        return envelope

    def new_item(
        self,
        payload,
        width: float,
        height: float,
        weight: float = 0.0,
    ) -> Item:
        item = FlatItem(payload, width, height, weight)
        self.add_item(item)
        return item

    @staticmethod
    def pack_to_bin(envelope: Bin, item: Item) -> None:
        if not envelope.items:
            response = envelope.put_item(item, START_POSITION)
            if not response:
                envelope.unfitted_items.append(item)
            return

        for axis in (Axis.WIDTH, Axis.HEIGHT):
            for ib in envelope.items:
                w, h, _ = ib.get_dimension()
                x, y, _ = ib.position
                if axis == Axis.WIDTH:
                    pivot = (x + w, y, 0)
                elif axis == Axis.HEIGHT:
                    pivot = (x, y + h, 0)
                else:
                    raise TypeError(axis)
                if envelope.put_item(item, pivot):
                    return
        envelope.unfitted_items.append(item)
