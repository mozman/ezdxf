# Source package: "py3dbp" hosted on PyPI
# (c) Enzo Ruiz Pelaez
# https://github.com/enzoruiz/3dbinpacking
# License: MIT License
# Credits:
# - https://github.com/enzoruiz/3dbinpacking/blob/master/erick_dube_507-034.pdf
# - https://github.com/gedex/bp3d - implementation in Go
# - https://github.com/bom-d-van/binpacking - implementation in Go
#
# ezdxf add-on:
# License: MIT License
# (c) 2022, Manfred Moitzi:
# - refactoring
# - type annotations
# - adaptations:
#   - removing Decimal class usage
#   - utilizing ezdxf.math.BondingBox
#   - fixed shared state error
#   - removed non-distributing mode
# - additions:
#   - Item.get_transformation()
#   - AbstractPacker.shuffle_pack()
#   - AbstractPacker.pack_by_order(): inter face for genetic algorithm
#   - DXF exporter for debugging

from typing import Tuple, List, Iterable, TYPE_CHECKING, Iterator
import abc
from enum import Enum, auto
import copy
import itertools
import math
import random

from ezdxf.enums import TextEntityAlignment

from ezdxf.math import (
    Vec2,
    Vec3,
    Vertex,
    BoundingBox,
    BoundingBox2d,
    AbstractBoundingBox,
    Matrix44,
)

if TYPE_CHECKING:
    from ezdxf.eztypes import GenericLayoutType

__all__ = [
    "Item",
    "FlatItem",
    "Box",  # contains Item
    "Envelope",  # contains FlatItem
    "AbstractPacker",
    "Packer",
    "FlatPacker",
    "RotationType",
    "PickStrategy",
    "export_dxf",
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
    SHUFFLE = auto()


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
        self._tainted_bbox = True

    def copy(self):
        # All copies have a reference to the same payload
        return copy.copy(self)  # shallow copy

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
        if self._tainted_bbox:
            self._update_bbox()
            self._tainted_bbox = False
        return self._bbox

    @property
    def rotation_type(self) -> RotationType:
        return self._rotation_type

    @rotation_type.setter
    def rotation_type(self, value: RotationType) -> None:
        self._rotation_type = value
        self._tainted_bbox = True

    @property
    def position(self) -> Tuple[float, float, float]:
        return self._position

    @position.setter
    def position(self, value: Tuple[float, float, float]) -> None:
        self._position = value
        self._tainted_bbox = True

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

    def get_transformation(self) -> Matrix44:
        """Returns the transformation matrix to transform the source entity
        located with the minimum extension corner of its bounding box in
        (0, 0, 0) to the final location including the required rotation.
        """
        x, y, z = self.position
        rt = self.rotation_type
        if rt == RotationType.WHD:
            return Matrix44.translate(x, y, z)
        elif rt == RotationType.HWD:
            # height, width, depth orientation
            return Matrix44.z_rotate(math.pi / 2) @ Matrix44.translate(
                x + self.height, y, 0
            )
        raise NotImplementedError(f"rotation {str(rt)} not supported yet")


class FlatItem(Item):
    def __init__(
        self,
        payload,
        width: float,
        height: float,
        weight: float = 0.0,
    ):
        super().__init__(payload, width, height, 1.0, weight)

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

    def copy(self):
        box = copy.copy(self)  # shallow copy
        box.items = list(self.items)
        box.unfitted_items = list(self.unfitted_items)
        return box

    def __str__(self) -> str:
        return (
            f"{str(self.name)}({self.width:.3f}x{self.height:.3f}x{self.depth:.3f}, "
            f"max_weight:{self.max_weight}) "
            f"vol({self.get_capacity():.3f})"
        )

    def put_item(self, item: Item, pivot: Tuple[float, float, float]) -> bool:
        valid_item_position = item.position
        item.position = pivot
        x, y, z = pivot

        # Try all possible rotations:
        for rotation_type in self.rotations():
            item.rotation_type = rotation_type
            w, h, d = item.get_dimension()
            if self.width < x + w or self.height < y + h or self.depth < z + d:
                continue
            # new item fits inside the box at he current location and rotation:
            item_bbox = item.bbox
            if (
                not any(item_bbox.intersect(i.bbox) for i in self.items)
                and self.get_total_weight() + item.weight <= self.max_weight
            ):
                self.items.append(item.copy())
                return True

        item.position = valid_item_position
        return False

    def get_capacity(self) -> float:
        """Returns the maximum fill volume of the bin."""
        return self.width * self.height * self.depth

    def get_total_weight(self) -> float:
        """Returns the total weight of all fitted items."""
        return sum(item.weight for item in self.items)

    def get_total_volume(self) -> float:
        """Returns the total volume of all fitted items."""
        return sum(item.get_volume() for item in self.items)

    def get_fill_ratio(self) -> float:
        """Return the fill ratio."""
        return self.get_total_volume() / self.get_capacity()

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
            f"area({self.get_capacity():.3f})"
        )

    def rotations(self) -> Iterable[RotationType]:
        return RotationType.WHD, RotationType.HWD


def _smaller_first(bins: List, items: List) -> None:
    # SMALLER_FIRST is often very bad! Especially for many in small
    # amounts increasing sizes.
    bins.sort(key=lambda b: b.get_capacity())
    items.sort(key=lambda i: i.get_volume())


def _bigger_first(bins: List, items: List) -> None:
    # BIGGER_FIRST is the best strategy
    bins.sort(key=lambda b: b.get_capacity(), reverse=True)
    items.sort(key=lambda i: i.get_volume(), reverse=True)


def _shuffle(bins: List, items: List) -> None:
    # Better as SMALLER_FIRST
    random.shuffle(bins)
    random.shuffle(items)


PICK_STRATEGY = {
    PickStrategy.SMALLER_FIRST: _smaller_first,
    PickStrategy.BIGGER_FIRST: _bigger_first,
    PickStrategy.SHUFFLE: _shuffle,
}


class AbstractPacker(abc.ABC):
    def __init__(self):
        self.bins: List[Bin] = []
        self.items: List[Item] = []
        self._init_state = True

    def copy(self):
        """Copy packer in init state to apply different pack strategies."""
        if self._init_state is False:
            raise TypeError("cannot copy packed state")
        packer = self.__class__()
        packer.bins = [box.copy() for box in self.bins]
        packer.items = [item.copy() for item in self.items]
        return packer

    @property
    def is_packed(self) -> bool:
        return not self._init_state

    def __str__(self) -> str:
        fill = ""
        if self.is_packed:
            fill = f", fill ratio: {self.get_fill_ratio()}"
        return f"{self.__class__.__name__}, {len(self.bins)} bins{fill}"

    def append_bin(self, bin_: Bin) -> None:
        self.bins.append(bin_)

    def append_item(self, item: Item) -> None:
        self.items.append(item)

    def get_fill_ratio(self) -> float:
        """Return the fill ratio of all bins."""
        total_capacity = self.get_capacity()
        if total_capacity == 0.0:
            return 0.0
        return self.get_total_volume() / total_capacity

    def get_capacity(self) -> float:
        """Returns the maximum fill volume of all bins."""
        return sum(box.get_capacity() for box in self.bins)

    def get_total_weight(self) -> float:
        """Returns the total weight of all fitted items in all bins."""
        return sum(box.get_total_weight() for box in self.bins)

    def get_total_volume(self) -> float:
        """Returns the total volume of all fitted items in all bins."""
        return sum(box.get_total_volume() for box in self.bins)

    def pack(
        self,
        pick=PickStrategy.BIGGER_FIRST,
    ):
        """Pack items into bins. Distributes all items across all bins."""
        self._init_state = False
        PICK_STRATEGY[pick](self.bins, self.items)

        for box in self.bins:
            for item in list(self.items):  # shallow copy because: remove()!
                if self.pack_to_bin(box, item):
                    self.items.remove(item)
        # unfitted items remain in items

    def shuffle_pack(self, attempts: int) -> "AbstractPacker":
        """Random shuffle packing. Returns a new packer, the current packer is
        unchanged.
        """
        best_ratio = 0.0
        best_packer = None
        for _ in range(attempts):
            packer = self.copy()
            packer.pack(PickStrategy.SHUFFLE)
            new_ratio = packer.get_fill_ratio()
            if new_ratio > best_ratio:
                best_ratio = new_ratio
                best_packer = packer
        if best_packer is None:
            return self
        return best_packer

    def schematic_pack(
        self, item_schema: Iterator[float], bin_schema: Iterator[float] = None
    ) -> None:
        # interface for genetic algorithm
        self._init_state = False
        bins = list(self.bins)
        items = list(self.items)
        # fixed ascending base order
        _smaller_first(bins, items)
        if bin_schema is None:
            bin_schema = itertools.repeat(1.0)  # bigger first
        for box in schematic_picker(bins, bin_schema):
            for item in schematic_picker(items, item_schema):
                if self.pack_to_bin(box, item):
                    self.items.remove(item)
        # unfitted items remain in items

    @staticmethod
    @abc.abstractmethod
    def pack_to_bin(box: Bin, item: Item) -> bool:
        ...


def schematic_picker(items: List, schema: Iterator[float]) -> Iterator:
    """Yields all items in the order defined by the schema.

    The pick values have to be in the range [0, 1] and determine the
    location from where to pick the next item as: len(items) * pick_value.
    Each picked item will be removed from the items list.

    """
    while len(items):
        try:
            value = next(schema)
        except StopIteration:
            raise ValueError("not enough pick values")
        if 0.0 <= value <= 1.0:
            pos = round(value * (len(items) - 1))
        else:
            raise ValueError("pick values have to be in range [0, 1]")
        item = items.pop(pos)
        yield item


class Packer(AbstractPacker):
    """3D Packer."""

    def add_bin(
        self,
        name: str,
        width: float,
        height: float,
        depth: float,
        max_weight: float = UNLIMITED_WEIGHT,
    ) -> Box:
        box = Box(name, width, height, depth, max_weight)
        self.append_bin(box)
        return box

    def add_item(
        self,
        payload,
        width: float,
        height: float,
        depth: float,
        weight: float = 0.0,
    ) -> Item:
        item = Item(payload, width, height, depth, weight)
        self.append_item(item)
        return item

    @staticmethod
    def pack_to_bin(box: Bin, item: Item) -> bool:
        if not box.items:
            response = box.put_item(item, START_POSITION)
            if not response:
                box.unfitted_items.append(item)
            return response

        for axis in Axis:
            for placed_item in box.items:
                w, h, d = placed_item.get_dimension()
                x, y, z = placed_item.position
                if axis == Axis.WIDTH:
                    pivot = (x + w, y, z)  # new item right of the placed item
                elif axis == Axis.HEIGHT:
                    pivot = (x, y + h, z)  # new item above of the placed item
                elif axis == Axis.DEPTH:
                    pivot = (x, y, z + d)  # new item on top of the placed item
                else:
                    raise TypeError(axis)
                if box.put_item(item, pivot):
                    return True

        box.unfitted_items.append(item)
        return False


class FlatPacker(AbstractPacker):
    """2D Packer."""

    def add_bin(
        self,
        name: str,
        width: float,
        height: float,
        max_weight: float = UNLIMITED_WEIGHT,
    ) -> Envelope:
        envelope = Envelope(name, width, height, max_weight)
        self.append_bin(envelope)
        return envelope

    def add_item(
        self,
        payload,
        width: float,
        height: float,
        weight: float = 0.0,
    ) -> Item:
        item = FlatItem(payload, width, height, weight)
        self.append_item(item)
        return item

    @staticmethod
    def pack_to_bin(envelope: Bin, item: Item) -> bool:
        if not envelope.items:
            response = envelope.put_item(item, START_POSITION)
            if not response:
                envelope.unfitted_items.append(item)
            return response

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
                    return True
        envelope.unfitted_items.append(item)
        return False


def export_dxf(
    layout: "GenericLayoutType", bins: List[Bin], offset: Vertex = (1, 0, 0)
) -> None:
    from ezdxf import colors

    offset_vec = Vec3(offset)
    start = Vec3()
    index = 0
    rgb = (colors.RED, colors.GREEN, colors.BLUE, colors.MAGENTA, colors.CYAN)
    for box in bins:
        m = Matrix44.translate(start.x, start.y, start.z)
        _add_frame(layout, box, "FRAME", m)
        for item in box.items:
            _add_mesh(layout, item, "ITEMS", rgb[index], m)
            index += 1
            if index >= len(rgb):
                index = 0
        start += offset_vec


def _add_frame(layout: "GenericLayoutType", box: Bin, layer: str, m: Matrix44):
    def add_line(v1, v2):
        line = layout.add_line(v1, v2, dxfattribs=attribs)
        line.transform(m)

    attribs = {"layer": layer}
    x0, y0, z0 = (0.0, 0.0, 0.0)
    x1 = float(box.width)
    y1 = float(box.height)
    z1 = float(box.depth)
    corners = [
        (x0, y0),
        (x1, y0),
        (x1, y1),
        (x0, y1),
        (x0, y0),
    ]
    for (sx, sy), (ex, ey) in zip(corners, corners[1:]):
        add_line((sx, sy, z0), (ex, ey, z0))
        add_line((sx, sy, z1), (ex, ey, z1))
    for x, y in corners[:-1]:
        add_line((x, y, z0), (x, y, z1))

    text = layout.add_text(box.name, height=0.25, dxfattribs=attribs)
    text.set_placement((x0 + 0.25, y1 - 0.5, z1))
    text.transform(m)


def _add_mesh(
    layout: "GenericLayoutType", item: Item, layer: str, color: int, m: Matrix44
):
    from ezdxf.render.forms import cube

    attribs = {
        "layer": layer,
        "color": color,
    }
    mesh = cube(center=False)
    sx, sy, sz = item.get_dimension()
    mesh.scale(sx, sy, sz)
    x, y, z = item.position
    mesh.translate(x, y, z)
    mesh.render_polyface(layout, attribs, matrix=m)
    text = layout.add_text(
        str(item.payload), height=0.25, dxfattribs={"layer": "TEXT"}
    )
    if sy > sx:
        text.dxf.rotation = 90
        align = TextEntityAlignment.TOP_LEFT
    else:
        align = TextEntityAlignment.BOTTOM_LEFT
    text.set_placement((x + 0.25, y + 0.25, z + sz), align=align)
    text.transform(m)
