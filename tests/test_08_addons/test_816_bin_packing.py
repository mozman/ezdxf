#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pytest
import itertools
import random
from ezdxf.addons import binpacking as bp


def test_single_bin_single_item():

    packer = bp.Packer()
    box = packer.add_bin("B0", 1, 1, 1)
    packer.add_item("I0", 1, 1, 1, 1)
    packer.pack()
    assert len(box.items) == 1
    assert len(packer.unfitted_items) == 0


@pytest.mark.parametrize(
    "w,h,d",
    [
        (3, 1, 1),
        (1, 3, 1),
        (1, 1, 3),
    ],
)
def test_single_bin_multiple_items(w, h, d):
    packer = bp.Packer()
    box = packer.add_bin("B0", w, h, d)
    for index in range(max(w, h, d)):
        packer.add_item(f"I{index}", 1, 1, 1, 1)
    packer.pack()
    assert len(box.items) == 3
    assert len(packer.unfitted_items) == 0


def test_single_bin_different_sized_items():
    packer = bp.Packer()
    box = packer.add_bin("B0", 3, 3, 1)
    packer.add_item("I0", 1, 1, 1, 1)
    packer.add_item("I1", 2, 1, 1, 1)
    packer.add_item("I2", 3, 1, 1, 1)
    packer.pack()
    assert len(box.items) == 3
    assert len(packer.unfitted_items) == 0


def test_empty_packer():
    packer = bp.Packer()
    assert packer.get_capacity() == 0.0
    assert packer.get_total_volume() == 0.0
    assert packer.get_total_weight() == 0.0
    assert packer.get_fill_ratio() == 0.0
    assert len(packer.unfitted_items) == 0


def test_empty_box():
    box = bp.Box("box", 1, 1, 1)
    assert box.get_capacity() == 1.0
    assert box.get_fill_ratio() == 0.0


def test_cannot_create_zero_sized_box():
    with pytest.raises(ValueError):
        bp.Box("box", 0, 2, 3)
    with pytest.raises(ValueError):
        bp.Box("box", 1, 0, 3)
    with pytest.raises(ValueError):
        bp.Box("box", 1, 2, 0)


def test_forced_zero_sized_box():
    box = bp.Box("box", 1, 2, 3)
    box.width = 0
    assert box.get_capacity() == 0.0
    assert box.get_fill_ratio() == 0.0


SMALL_ENVELOPE = ("small-envelope", 11.5, 6.125, 0.25, 10)
LARGE_ENVELOPE = ("large-envelope", 15.0, 12.0, 0.75, 15)
SMALL_BOX = ("small-box", 8.625, 5.375, 1.625, 70.0)
MEDIUM_BOX = ("medium-box", 11.0, 8.5, 5.5, 70.0)
MEDIUM_BOX2 = ("medium-box-2", 13.625, 11.875, 3.375, 70.0)
LARGE_BOX = ("large-box", 12.0, 12.0, 5.5, 70.0)
LARGE_BOX2 = ("large-box-2", 23.6875, 11.75, 3.0, 70.0)

ALL_BINS = [
    SMALL_ENVELOPE,
    LARGE_ENVELOPE,
    SMALL_BOX,
    MEDIUM_BOX,
    MEDIUM_BOX2,
    LARGE_BOX,
    LARGE_BOX2,
]


@pytest.fixture
def packer():
    packer = bp.Packer()
    packer.add_item("50g [powder 1]", 3.9370, 1.9685, 1.9685, 1)
    packer.add_item("50g [powder 2]", 3.9370, 1.9685, 1.9685, 2)
    packer.add_item("50g [powder 3]", 3.9370, 1.9685, 1.9685, 3)
    packer.add_item("250g [powder 4]", 7.8740, 3.9370, 1.9685, 4)
    packer.add_item("250g [powder 5]", 7.8740, 3.9370, 1.9685, 5)
    packer.add_item("250g [powder 6]", 7.8740, 3.9370, 1.9685, 6)
    packer.add_item("250g [powder 7]", 7.8740, 3.9370, 1.9685, 7)
    packer.add_item("250g [powder 8]", 7.8740, 3.9370, 1.9685, 8)
    packer.add_item("250g [powder 9]", 7.8740, 3.9370, 1.9685, 9)
    return packer


def pack(packer, box, pick):
    packer.add_bin(*box)
    packer.pack(pick)
    return packer.bins[0]


class TestExampleSmallerFirst:
    @staticmethod
    def pack(packer, box):
        return pack(packer, box, bp.PickStrategy.SMALLER_FIRST)

    @pytest.mark.parametrize("box", [SMALL_ENVELOPE, LARGE_ENVELOPE, SMALL_BOX])
    def test_small_bins(self, packer, box):
        b0 = self.pack(packer, box)
        assert len(b0.items) == 0
        assert b0.get_total_weight() == 0
        assert b0.get_total_volume() == 0.0
        assert b0.get_fill_ratio() == 0.0

    def test_medium_box(self, packer):
        b0 = self.pack(packer, MEDIUM_BOX)
        assert len(b0.items) == 6
        assert b0.get_total_weight() == 21
        assert b0.get_total_volume() == pytest.approx(228.83766732374997)
        assert b0.get_fill_ratio() == pytest.approx(0.44499303320126393)

    def test_medium_box2(self, packer):
        b0 = self.pack(packer, MEDIUM_BOX2)
        assert len(b0.items) == 6
        assert b0.get_total_weight() == 21
        assert b0.get_total_volume() == pytest.approx(228.83766732374997)
        assert b0.get_fill_ratio() == pytest.approx(0.4190671376138204)

    def test_large_box(self, packer):
        b0 = self.pack(packer, LARGE_BOX)
        assert len(b0.items) == 9
        assert b0.get_total_weight() == 45
        assert b0.get_total_volume() == pytest.approx(411.90780118274995)
        assert b0.get_fill_ratio() == pytest.approx(0.5200856075539773)

    def test_large_box2(self, packer):
        b0 = self.pack(packer, LARGE_BOX2)
        assert len(b0.items) == 9
        assert b0.get_total_weight() == 45
        assert b0.get_total_volume() == pytest.approx(411.90780118274995)
        assert b0.get_fill_ratio() == pytest.approx(0.4933119870449671)


class TestExampleBiggerFirst:
    @staticmethod
    def pack(packer, box):
        return pack(packer, box, bp.PickStrategy.BIGGER_FIRST)

    @pytest.mark.parametrize("box", [SMALL_ENVELOPE, LARGE_ENVELOPE, SMALL_BOX])
    def test_small_bins(self, packer, box):
        b0 = self.pack(packer, box)
        assert len(b0.items) == 0
        assert b0.get_total_weight() == 0
        assert b0.get_total_volume() == 0.0
        assert b0.get_fill_ratio() == 0.0

    def test_medium_box(self, packer):
        b0 = self.pack(packer, MEDIUM_BOX)
        assert len(b0.items) == 5
        assert b0.get_total_weight() == 30
        assert b0.get_total_volume() == pytest.approx(305.116889765)
        assert b0.get_fill_ratio() == pytest.approx(0.593324044268352)

    def test_medium_box2(self, packer):
        b0 = self.pack(packer, MEDIUM_BOX2)
        assert len(b0.items) == 6
        assert b0.get_total_weight() == 25
        assert b0.get_total_volume() == pytest.approx(274.6052007884999)
        assert b0.get_fill_ratio() == pytest.approx(0.5028805651365844)

    def test_large_box(self, packer):
        b0 = self.pack(packer, LARGE_BOX)
        assert len(b0.items) == 9
        assert b0.get_total_weight() == 45
        assert b0.get_total_volume() == pytest.approx(411.90780118274995)
        assert b0.get_fill_ratio() == pytest.approx(0.5200856075539773)

    def test_large_box2(self, packer):
        b0 = self.pack(packer, LARGE_BOX2)
        assert len(b0.items) == 9
        assert b0.get_total_weight() == 45
        assert b0.get_total_volume() == pytest.approx(411.90780118274995)
        assert b0.get_fill_ratio() == pytest.approx(0.4933119870449671)


@pytest.mark.parametrize(
    "item",
    [
        bp.Item([1, 2, 3], 1, 2, 3, 4),
        bp.FlatItem([1, 2, 3], 1, 2, 4),
    ],
)
def test_copy_item(item):
    assert item.bbox is not None  # trigger bounding box update
    item2 = item.copy()
    assert item.payload is item2.payload, "should reference the same object"
    assert item.get_dimension() == item2.get_dimension()
    assert item.position == item2.position
    assert item.weight == item2.weight
    assert item.bbox is item2.bbox


class TestItemTransformation:
    """Transformation of the source entity located with the minimum extension
    corner of its bounding box in (0, 0, 0) in width (x), height (y) and depth (z)
    orientation to the final location including the required rotation.
    """

    @pytest.fixture
    def item(self):
        i = bp.Item("box", 2, 3, 4)
        i.position = (3, 2, 1)  # target location
        return i

    def test_whd_rotation(self, item: bp.Item):
        item.rotation_type = bp.RotationType.WHD  # width, height, depth
        m = item.get_transformation()
        assert m.transform((0, 0, 0)).isclose((3, 2, 1))

    def test_hwd_rotation(self, item: bp.Item):
        item.rotation_type = bp.RotationType.HWD  # height, width, depth
        m = item.get_transformation()
        assert m.transform((0, 0, 0)).isclose((6, 2, 1))

    def test_hdw_rotation(self, item: bp.Item):
        item.rotation_type = bp.RotationType.HDW  # height, depth, width
        m = item.get_transformation()
        assert m.transform((0, 0, 0)).isclose((6, 6, 1))

    def test_dhw_rotation(self, item: bp.Item):
        item.rotation_type = bp.RotationType.DHW  # depth, height, width
        m = item.get_transformation()
        assert m.transform((0, 0, 0)).isclose((7, 2, 1))

    def test_dwh_rotation(self, item: bp.Item):
        item.rotation_type = bp.RotationType.DWH  # depth, width, height
        m = item.get_transformation()
        assert m.transform((0, 0, 0)).isclose((3, 2, 1))

    def test_wdh_rotation(self, item: bp.Item):
        item.rotation_type = bp.RotationType.WDH  # width, depth, height
        m = item.get_transformation()
        assert m.transform((0, 0, 0)).isclose((3, 6, 1))


def test_copy_box():
    box = bp.Box("NAME", 1, 2, 3, 4)
    box.items = [1, 2, 3]
    box.unfitted_items = [4, 5, 6]
    box2 = box.copy()

    assert box.name == box2.name
    assert box.width == box2.width
    assert box.height == box2.height
    assert box.max_weight == box2.max_weight
    assert box.items is not box2.items, "expected shallow copy"


def test_copy_packer(packer):
    packer2 = packer.copy()
    assert packer.bins is not packer2.bins, "expected shallow copy"
    assert len(packer.bins) == len(packer2.bins)
    assert packer.items is not packer2.items, "expected shallow copy"
    assert len(packer.items) == len(packer2.items)


def test_cannot_copy_packed_packer(packer):
    packer.pack(pick=bp.PickStrategy.BIGGER_FIRST)
    with pytest.raises(TypeError):
        packer.copy()


def test_cannot_copy_packer_with_non_empty_bins(packer):
    box = bp.Bin(*LARGE_BOX)
    packer.append_bin(box)
    box.items.append(0)  # type: ignore
    with pytest.raises(TypeError):
        packer.copy()


def test_cannot_append_bins_to_packed_packer(packer):
    packer.pack(pick=bp.PickStrategy.BIGGER_FIRST)
    with pytest.raises(TypeError):
        packer.append_bin(bp.Bin(*LARGE_BOX))


def test_cannot_append_non_empty_bins(packer):
    box = bp.Bin(*LARGE_BOX)
    box.items.append(0)  # type: ignore
    with pytest.raises(TypeError):
        packer.append_bin(box)


def test_cannot_append_items_to_packed_packer(packer):
    packer.pack(pick=bp.PickStrategy.BIGGER_FIRST)
    with pytest.raises(TypeError):
        packer.append_item(bp.Item(0, 0, 0, 0))


def test_random_shuffle_interface(packer):
    packer.add_bin(*LARGE_BOX2)
    best = bp.shuffle_pack(packer, 2)
    assert best.get_fill_ratio() > 0.0


def test_random_shuffle_raise_exception_for_invalid_attempts(packer):
    with pytest.raises(ValueError):
        bp.shuffle_pack(packer, 0)


class TestSchematicPicker:
    @pytest.fixture
    def items(self):
        return [0, 1, 2, 3, 4]

    @staticmethod
    def get_picked_items(items, order):
        return list(bp.schematic_picker(items, order))

    def test_pick_from_front(self, items):
        picked_items = self.get_picked_items(items, itertools.repeat(0))
        assert picked_items == [0, 1, 2, 3, 4]

    def test_pick_from_back(self, items):
        picked_items = self.get_picked_items(items, itertools.repeat(1))
        assert picked_items == [4, 3, 2, 1, 0]

    def test_random_pick(self, items):
        picked_items = self.get_picked_items(
            items, (random.random() for _ in range(5))
        )
        assert set(picked_items) == {4, 3, 2, 1, 0}

    @pytest.mark.parametrize(
        "value",
        [
            1.1,  # upper limit is 1.0
            -0.1,  # lower limit 0.0
        ],
    )
    def test_invalid_pick_values(self, items, value):
        with pytest.raises(ValueError):
            self.get_picked_items(items, itertools.repeat(value))

    def test_not_enough_pick_values(self, items):
        with pytest.raises(ValueError):
            self.get_picked_items(items, iter([1, 1, 1]))


class TestGeneticDriver:
    def test_init(self, packer):
        driver = bp.GeneticDriver(packer, 100)
        assert driver.is_executed is False

    def test_init_invalid_packer(self, packer):
        """Packer is already packed."""
        pack(packer, SMALL_BOX, bp.PickStrategy.SMALLER_FIRST)
        with pytest.raises(ValueError):
            bp.GeneticDriver(packer, 100)

    def test_init_invalid_max_runs(self, packer):
        with pytest.raises(ValueError):
            bp.GeneticDriver(packer, 0)

    @pytest.mark.parametrize("fitness", [-0.1, 1.1])
    def test_set_invalid_max_fitness(self, packer, fitness):
        gd = bp.GeneticDriver(packer, 100)
        with pytest.raises(ValueError):
            gd.max_fitness = fitness

    def test_can_only_run_once(self, packer):
        driver = bp.GeneticDriver(packer, 100)
        driver.execute()
        assert driver.is_executed is True
        with pytest.raises(TypeError):
            driver.execute()

    def test_execution(self, packer):
        packer.add_bin(*MEDIUM_BOX)
        driver = bp.GeneticDriver(packer, 10)
        driver.add_random_dna(20)
        driver.execute()
        assert driver.generation == 10
        assert driver.best_fitness > 0.1
        assert len(driver.best_packer.bins[0].items) > 1


if __name__ == "__main__":
    pytest.main([__file__])
