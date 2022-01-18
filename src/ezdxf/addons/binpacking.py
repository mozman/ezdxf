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
#   - utilizing ezdxf.math.BoundingBox for intersection checks
#   - removed non-distributing mode; copy packer and use different bins for each copy
# - additions:
#   - Item.get_transformation()
#   - shuffle_pack()
#   - AbstractPacker.schematic_pack() interface for genetic algorithms
#   - DXF exporter for debugging

from typing import (
    Tuple,
    List,
    Iterable,
    TYPE_CHECKING,
    Iterator,
    TypeVar,
    Sequence,
    Optional,
    Callable,
)
import array
from enum import Enum, auto
import copy
import itertools
import math
import random
import time


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
    "shuffle_pack",
    "export_dxf",
]

UNLIMITED_WEIGHT = 1e99
T = TypeVar("T")
PI_2 = math.pi / 2


class RotationType(Enum):
    """Rotation type of an item:

        - W = width
        - H = height
        - D = depth

    """
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
    """ Order of how to pick items for placement. """
    SMALLER_FIRST = auto()
    BIGGER_FIRST = auto()
    SHUFFLE = auto()


START_POSITION: Tuple[float, float, float] = (0, 0, 0)


class Item:
    """3D container item. """
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
        self._bbox: Optional[AbstractBoundingBox] = None

    def __str__(self):
        return (
            f"{str(self.payload)}({self.width}x{self.height}x{self.depth}, "
            f"weight: {self.weight}) pos({str(self.position)}) "
            f"rt({self.rotation_type}) vol({self.get_volume()})"
        )

    def copy(self):
        """Returns a copy, all copies have a reference to the same payload
        object.
        """
        return copy.copy(self)  # shallow copy

    @property
    def bbox(self) -> AbstractBoundingBox:
        if self._bbox is None:
            self._update_bbox()
        return self._bbox  # type: ignore

    def _update_bbox(self) -> None:
        v1 = Vec3(self._position)
        self._bbox = BoundingBox([v1, v1 + Vec3(self.get_dimension())])

    def _taint(self):
        self._bbox = None

    @property
    def rotation_type(self) -> RotationType:
        return self._rotation_type

    @rotation_type.setter
    def rotation_type(self, value: RotationType) -> None:
        self._rotation_type = value
        self._taint()

    @property
    def position(self) -> Tuple[float, float, float]:
        """Returns the position of then lower left corner of the item in the
        container, the lower left corner is the origin (0, 0, 0).
        """
        return self._position

    @position.setter
    def position(self, value: Tuple[float, float, float]) -> None:
        self._position = value
        self._taint()

    def get_volume(self) -> float:
        """Returns the volume of the item. """
        return self.width * self.height * self.depth

    def get_dimension(self) -> Tuple[float, float, float]:
        """Returns the item dimension according the :attr:`rotation_type`. """
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
        if rt == RotationType.WHD:  # width, height, depth
            return Matrix44.translate(x, y, z)
        if rt == RotationType.HWD:  # height, width, depth
            return Matrix44.z_rotate(PI_2) @ Matrix44.translate(
                x + self.height, y, z
            )
        if rt == RotationType.HDW:  # height, depth, width
            return Matrix44.xyz_rotate(PI_2, 0, PI_2) @ Matrix44.translate(
                x + self.height, y + self.depth, z
            )
        if rt == RotationType.DHW:  # depth, height, width
            return Matrix44.y_rotate(-PI_2) @ Matrix44.translate(
                x + self.depth, y, z
            )
        if rt == RotationType.DWH:  # depth, width, height
            return Matrix44.xyz_rotate(0, PI_2, PI_2) @ Matrix44.translate(
                x, y, z
            )
        if rt == RotationType.WDH:  # width, depth, height
            return Matrix44.x_rotate(PI_2) @ Matrix44.translate(
                x, y + self.depth, z
            )
        raise TypeError(rt)


class FlatItem(Item):
    """2D container item, inherited from :class:`Item`. Has a default depth of
    1.0.
    """
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

    def copy(self):
        """Returns a copy. """
        box = copy.copy(self)  # shallow copy
        box.items = list(self.items)
        return box

    def reset(self):
        """Reset the container to empty state. """
        self.items.clear()

    @property
    def is_empty(self) -> bool:
        return not len(self.items)

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
                self.items.append(item)
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
    """ 3D container inherited from :class:`Bin`. """
    pass


class Envelope(Bin):
    """ 2D container inherited from :class:`Bin`. """
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


class AbstractPacker:
    def __init__(self):
        self.bins: List[Bin] = []
        self.items: List[Item] = []
        self._init_state = True

    def copy(self):
        """Copy packer in init state to apply different pack strategies."""
        if self.is_packed:
            raise TypeError("cannot copy packed state")
        if not all(box.is_empty for box in self.bins):
            raise TypeError("bins contain data in unpacked state")
        packer = self.__class__()
        packer.bins = [box.copy() for box in self.bins]
        packer.items = [item.copy() for item in self.items]
        return packer

    @property
    def is_packed(self) -> bool:
        """Returns ``True`` if packer is packed, each packer can only be used
        once.
        """
        return not self._init_state

    @property
    def unfitted_items(self) -> List[Item]:  # just an alias
        """Returns the unfitted items. """
        return self.items

    def __str__(self) -> str:
        fill = ""
        if self.is_packed:
            fill = f", fill ratio: {self.get_fill_ratio()}"
        return f"{self.__class__.__name__}, {len(self.bins)} bins{fill}"

    def append_bin(self, box: Bin) -> None:
        """Append a container. """
        if self.is_packed:
            raise TypeError("cannot append bins to packed state")
        if not box.is_empty:
            raise TypeError("cannot append bins with content")
        self.bins.append(box)

    def append_item(self, item: Item) -> None:
        """Append a item. """
        if self.is_packed:
            raise TypeError("cannot append items to packed state")
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

    def pack(self, pick=PickStrategy.BIGGER_FIRST) -> None:
        """Pack items into bins. Distributes all items across all bins."""
        PICK_STRATEGY[pick](self.bins, self.items)
        # items are removed from self.items while packing!
        self._pack(self.bins, list(self.items))
        # unfitted items remain in self.items

    def _pack(self, bins: Iterable[Bin], items: Iterable[Item]) -> None:
        """Pack items into bins, removes packed items from self.items!"""
        self._init_state = False
        for box in bins:
            for item in items:
                if self.pack_to_bin(box, item):
                    self.items.remove(item)
        # unfitted items remain in self.items

    def schematic_pack(
        self, item_schema: Iterator[float], bin_schema: Iterator[float] = None
    ) -> None:
        # fixed ascending base order
        _smaller_first(self.bins, self.items)
        if bin_schema is None:
            bin_schema = itertools.repeat(1.0)  # bigger first
        self._pack(
            # schematic picker uses a shallow copy of the input data!
            schematic_picker(self.bins, bin_schema),
            schematic_picker(self.items, item_schema),
        )
        # unfitted items remain in self.items

    def pack_to_bin(self, box: Bin, item: Item) -> bool:
        if not box.items:
            return box.put_item(item, START_POSITION)

        for axis in self._axis():
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
        return False

    @staticmethod
    def _axis() -> Iterable[Axis]:
        return Axis


def shuffle_pack(packer: AbstractPacker, attempts: int) -> AbstractPacker:
    """Random shuffle packing. Returns a new packer with the best packing result,
    the input packer is unchanged.
    """
    if attempts < 1:
        raise ValueError("expected attempts >= 1")
    best_ratio = 0.0
    best_packer = packer
    for _ in range(attempts):
        new_packer = packer.copy()
        new_packer.pack(PickStrategy.SHUFFLE)
        new_ratio = new_packer.get_fill_ratio()
        if new_ratio > best_ratio:
            best_ratio = new_ratio
            best_packer = new_packer
    return best_packer


def schematic_picker(
    items: Iterable[T], schema: Iterator[float]
) -> Iterator[T]:
    """Yields all `items` in the order defined by the pick schema.
    The pick values have to be in the range [0, 1] and determine the
    location from where to pick the next item. E.g. 0 picks from the front, 1
    picks from the end and 0.5 picks from the middle. For each item is a pick
    value from the `schema` required!

    Args:
        items: iterable of input data
        schema: iterator of pick values as float in range [0, 1]

    Raises:
        ValueError: invalid pick value or not enough pick values

    """
    items = list(items)
    while len(items):
        try:
            value = next(schema)
        except StopIteration:
            raise ValueError("not enough pick values")
        try:
            yield items.pop(round(abs(value) * (len(items) - 1)))
        except IndexError:
            raise ValueError("pick values have to be in range [0, 1]")


class Packer(AbstractPacker):
    """3D Packer inherited form :class:`AbstractPacker`. """

    def add_bin(
        self,
        name: str,
        width: float,
        height: float,
        depth: float,
        max_weight: float = UNLIMITED_WEIGHT,
    ) -> Box:
        """Add a 3D :class:`Box` container. """
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
        """Add a 3D :class:`Item` to pack. """
        item = Item(payload, width, height, depth, weight)
        self.append_item(item)
        return item


class FlatPacker(AbstractPacker):
    """2D Packer inherited form :class:`AbstractPacker`. All containers and
    items used by this packer must have a depth of 1."""

    def add_bin(
        self,
        name: str,
        width: float,
        height: float,
        max_weight: float = UNLIMITED_WEIGHT,
    ) -> Envelope:
        """Add a 2D :class:`Envelope` container. """
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
        """Add a 2D :class:`FlatItem` to pack. """
        item = FlatItem(payload, width, height, weight)
        self.append_item(item)
        return item

    @staticmethod
    def _axis() -> Iterable[Axis]:
        return Axis.WIDTH, Axis.HEIGHT


def _to_list(values) -> List[float]:
    return array.array("f", values)  # type: ignore


class DNA:
    __slots__ = ("_length", "_data", "fitness")

    def __init__(self, length: int, value: float = 0.0):
        self._length = int(length)
        if 0.0 <= value <= 1.0:
            self._data: List[float] = _to_list(
                itertools.repeat(value, self._length)
            )
        else:
            raise ValueError("data value out of range")
        self.fitness: Optional[float] = None

    @classmethod
    def random(cls, length: int) -> "DNA":
        dna = cls(length)
        dna.reset(random.random() for _ in range(length))
        return dna

    def _check_valid_data(self):
        if len(self._data) != self._length:
            raise ValueError("invalid data count")
        if not all(0.0 <= v <= 1.0 for v in self._data):
            raise ValueError("data value out of range")

    def copy(self):
        return copy.deepcopy(self)

    def taint(self):
        self.fitness = None

    def __eq__(self, other):
        assert isinstance(other, DNA)
        return self._data == other._data

    def __str__(self):
        fitness = ", fitness=None"
        if fitness is None:
            fitness = ", fitness=None"
        else:
            fitness = f", fitness={self.fitness:.4f}"
        return f"{str([round(v, 4) for v in self._data])}{fitness}"

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        return self._data.__getitem__(item)

    def __iter__(self):
        return iter(self._data)

    def reset(self, values: Iterable[float]):
        self._data = _to_list(values)
        self._check_valid_data()
        self.taint()

    def mutate(self, rate: float):
        for index in range(self._length):
            if random.random() < rate:
                self.mutate_at(index)

    def mutate_at(self, index):
        self._data[index] = 1.0 - self._data[index]  # flip pick location
        self.taint()

    def replace_tail(self, part: Sequence) -> None:
        self._data[-len(part) :] = _to_list(part)
        self._check_valid_data()
        self.taint()


def recombine_dna(dna1: DNA, dna2: DNA, index: int) -> None:
    part1 = dna1[index:]
    part2 = dna2[index:]
    dna1.replace_tail(part2)
    dna2.replace_tail(part1)


class GeneticDriver:
    def __init__(
        self,
        packer: AbstractPacker,
        max_generations: int,
        max_fitness: float,
        crossover_rate: float = 0.70,
        mutation_rate: float = 0.001,
    ):
        if max_fitness > 1.0 or max_fitness < 0.0:
            raise ValueError("max_fitness not in range [0, 1]")
        self._max_fitness = float(max_fitness)
        if max_generations < 1:
            raise ValueError("max_generations < 1")
        self._max_generations = int(max_generations)
        if packer.is_packed:
            raise ValueError("packer is already packed")
        self._packer = packer
        self._required_dna_length = len(packer.items)
        self._dna_strands: List[DNA] = []
        self._crossover_rate = float(crossover_rate)
        self._mutation_rate = float(mutation_rate)
        self.best_fitness: float = 0.0
        self.best_dna = DNA(0)
        self.best_packer = packer
        self.generation: int = 0

    @property
    def is_executed(self) -> bool:
        return bool(self.generation)

    def add_dna(self, dna: DNA):
        if not self.is_executed:
            if len(dna) != self._required_dna_length:
                raise ValueError(
                    f"invalid DNA length, requires {self._required_dna_length}"
                )
            self._dna_strands.append(dna)
        else:
            raise TypeError("already executed")

    def add_random_dna(self, count: int):
        for _ in range(count):
            self.add_dna(DNA.random(self._required_dna_length))

    def execute(
        self,
        feedback: Callable = None,
        interval: float = 1.0,
        max_time: float = 1e99,
    ) -> None:
        if self.is_executed:
            raise TypeError("can only run once")
        t0 = time.perf_counter()
        start_time = t0
        for self.generation in range(1, self._max_generations + 1):
            self._measure_fitness()
            if self.best_fitness >= self._max_fitness:
                break
            t1 = time.perf_counter()
            if start_time - t1 > max_time:
                break
            if feedback and t1 - t0 > interval:
                if feedback():  # stop if feedback() returns True
                    break
                t0 = t1
            self._selection()

    def _measure_fitness(self):
        for dna in self._dna_strands:
            if dna.fitness is not None:
                continue
            p0 = self._packer.copy()
            p0.schematic_pack(iter(dna))
            fill_ratio = p0.get_fill_ratio()
            dna.fitness = fill_ratio
            if fill_ratio > self.best_fitness:
                self.best_fitness = fill_ratio
                self.best_packer = p0
                self.best_dna = dna.copy()

    def _selection(self):
        wheel = self._make_wheel()
        dna_strands: List[DNA] = []
        count = len(self._dna_strands)
        while len(dna_strands) < count:
            dna1, dna2 = wheel.pick(2)
            dna1 = dna1.copy()
            dna2 = dna2.copy()
            if random.random() < self._crossover_rate:
                location = random.randrange(0, self._required_dna_length)
                recombine_dna(dna1, dna2, location)
            dna1.mutate(self._mutation_rate)
            dna2.mutate(self._mutation_rate)
            dna_strands.append(dna1)
            dna_strands.append(dna2)
        self._dna_strands = dna_strands

    def _make_wheel(self):
        wheel = WheelOfFortune()
        dna_strands = self._dna_strands
        sum_fitness = sum(dna.fitness for dna in dna_strands)
        if sum_fitness == 0.0:
            sum_fitness = 1.0
        for dna in dna_strands:
            wheel.add_dna(dna, dna.fitness / sum_fitness)
        return wheel


class WheelOfFortune:
    def __init__(self):
        self._dna_strands: List[DNA] = []
        self._weights: List[float] = []

    def add_dna(self, item: DNA, weight: float):
        self._dna_strands.append(item)
        self._weights.append(weight)

    def pick(self, count: int) -> Iterable[DNA]:
        return random.choices(self._dna_strands, self._weights, k=count)


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
