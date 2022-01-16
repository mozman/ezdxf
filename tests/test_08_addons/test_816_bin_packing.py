#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pytest

from ezdxf.addons import binpacking


def test_single_bin_single_item():

    packer = binpacking.Packer()
    box = packer.add_bin("B0", 1, 1, 1)
    packer.add_item("I0", 1, 1, 1, 1)
    packer.pack()
    assert len(box.items) == 1
    assert len(box.unfitted_items) == 0


@pytest.mark.parametrize(
    "w,h,d",
    [
        (3, 1, 1),
        (1, 3, 1),
        (1, 1, 3),
    ],
)
def test_single_bin_multiple_items(w, h, d):
    packer = binpacking.Packer()
    box = packer.add_bin("B0", w, h, d)
    for index in range(max(w, h, d)):
        packer.add_item(f"I{index}", 1, 1, 1, 1)
    packer.pack()
    assert len(box.items) == 3
    assert len(box.unfitted_items) == 0


def test_single_bin_different_sized_items():
    packer = binpacking.Packer()
    box = packer.add_bin("B0", 3, 3, 1)
    packer.add_item("I0", 1, 1, 1, 1)
    packer.add_item("I1", 2, 1, 1, 1)
    packer.add_item("I2", 3, 1, 1, 1)
    packer.pack()
    assert len(box.items) == 3
    assert len(box.unfitted_items) == 0


@pytest.fixture
def packer():
    packer = binpacking.Packer()
    packer.add_bin("small-envelope", 11.5, 6.125, 0.25, 10)
    packer.add_bin("large-envelope", 15.0, 12.0, 0.75, 15)
    packer.add_bin("small-box", 8.625, 5.375, 1.625, 70.0)
    packer.add_bin("medium-box", 11.0, 8.5, 5.5, 70.0)
    packer.add_bin("medium-2-box", 13.625, 11.875, 3.375, 70.0)
    packer.add_bin("large-box", 12.0, 12.0, 5.5, 70.0)
    packer.add_bin("large-2-box", 23.6875, 11.75, 3.0, 70.0)

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


def test_example_smaller_first(packer):
    packer.pack(pick=binpacking.PickStrategy.SMALLER_FIRST)
    b0, b1, b2, b3, b4, b5, b6 = packer.bins
    assert len(b0.items) == 0
    assert b0.get_total_weight() == 0
    assert b0.get_total_volume() == 0.0
    assert b0.get_fill_ratio() == 0.0

    assert len(b1.items) == 0
    assert b1.get_total_weight() == 0

    assert len(b2.items) == 0
    assert b2.get_total_weight() == 0

    assert len(b3.items) == 6
    assert b3.get_total_weight() == 21
    assert b3.get_total_volume() == pytest.approx(228.83766732374997)
    assert b3.get_fill_ratio() == pytest.approx(0.44499303320126393)

    assert len(b4.items) == 6
    assert b4.get_total_weight() == 21
    assert b4.get_total_volume() == pytest.approx(228.83766732374997)
    assert b4.get_fill_ratio() == pytest.approx(0.4190671376138204)

    assert len(b5.items) == 9
    assert b5.get_total_weight() == 45
    assert b5.get_total_volume() == pytest.approx(411.90780118274995)
    assert b5.get_fill_ratio() == pytest.approx(0.5200856075539773)

    assert len(b6.items) == 9
    assert b6.get_total_weight() == 45
    assert b6.get_total_volume() == pytest.approx(411.90780118274995)
    assert b6.get_fill_ratio() == pytest.approx(0.4933119870449671)


def test_example_bigger_first(packer):
    packer.pack(pick=binpacking.PickStrategy.BIGGER_FIRST)
    b0, b1, b2, b3, b4, b5, b6 = packer.bins
    assert len(b0.items) == 9
    assert b0.get_total_weight() == 45
    assert b0.get_total_volume() == pytest.approx(411.90780118274995)
    assert b0.get_fill_ratio() == pytest.approx(0.4933119870449671)

    assert len(b1.items) == 9
    assert b1.get_total_weight() == 45
    assert b1.get_total_volume() == pytest.approx(411.90780118274995)
    assert b1.get_fill_ratio() == pytest.approx(0.5200856075539773)

    assert len(b2.items) == 6
    assert b2.get_total_weight() == 25
    assert b2.get_total_volume() == pytest.approx(274.6052007884999)
    assert b2.get_fill_ratio() == pytest.approx(0.5028805651365844)

    assert len(b3.items) == 5
    assert b3.get_total_weight() == 30
    assert b3.get_total_volume() == pytest.approx(305.116889765)
    assert b3.get_fill_ratio() == pytest.approx(0.593324044268352)

    assert len(b4.items) == 0
    assert b4.get_total_weight() == 0

    assert len(b5.items) == 0
    assert b5.get_total_weight() == 0

    assert len(b6.items) == 0
    assert b6.get_total_weight() == 0


@pytest.mark.parametrize(
    "item",
    [
        binpacking.Item([1, 2, 3], 1, 2, 3, 4),
        binpacking.FlatItem([1, 2, 3], 1, 2, 4),
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


def test_copy_box():
    box = binpacking.Box("NAME", 1, 2, 3, 4)
    box.items = [1, 2, 3]
    box.unfitted_items = [4, 5, 6]
    box2 = box.copy()

    assert box.name == box2.name
    assert box.width == box2.width
    assert box.height == box2.height
    assert box.max_weight == box2.max_weight
    assert box.items is not box2.items, "expected shallow copy"
    assert (
        box.unfitted_items is not box2.unfitted_items
    ), "expected shallow copy"


def test_copy_packer(packer):
    packer2 = packer.copy()
    assert packer.bins is not packer2.bins, "expected shallow copy"
    assert len(packer.bins) == len(packer2.bins)
    assert packer.items is not packer2.items, "expected shallow copy"
    assert len(packer.items) == len(packer2.items)


def test_can_not_copy_packed_packer(packer):
    packer.pack(pick=binpacking.PickStrategy.BIGGER_FIRST)
    with pytest.raises(TypeError):
        packer.copy()


def test_random_shuffle_interface(packer):
    best = packer.shuffle_pack(2)
    assert best.get_fill_ratio() > 0.0


if __name__ == "__main__":
    pytest.main([__file__])
