#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pytest

from ezdxf.addons import binpacking


def test_single_bin_single_item():

    packer = binpacking.Packer()
    box = packer.add_box("B0", 1, 1, 1)
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
    box = packer.add_box("B0", w, h, d)
    for index in range(max(w, h, d)):
        packer.add_item(f"I{index}", 1, 1, 1, 1)
    packer.pack()
    assert len(box.items) == 3
    assert len(box.unfitted_items) == 0


def test_single_bin_different_sized_items():
    packer = binpacking.Packer()
    box = packer.add_box("B0", 3, 3, 1)
    packer.add_item("I0", 1, 1, 1, 1)
    packer.add_item("I1", 2, 1, 1, 1)
    packer.add_item("I2", 3, 1, 1, 1)
    packer.pack()
    assert len(box.items) == 3
    assert len(box.unfitted_items) == 0


@pytest.fixture
def packer():
    packer = binpacking.Packer()
    packer.add_box("small-envelope", 11.5, 6.125, 0.25, 10)
    packer.add_box("large-envelope", 15.0, 12.0, 0.75, 15)
    packer.add_box("small-box", 8.625, 5.375, 1.625, 70.0)
    packer.add_box("medium-box", 11.0, 8.5, 5.5, 70.0)
    packer.add_box("medium-2-box", 13.625, 11.875, 3.375, 70.0)
    packer.add_box("large-box", 12.0, 12.0, 5.5, 70.0)
    packer.add_box("large-2-box", 23.6875, 11.75, 3.0, 70.0)

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
    packer.pack(pick_strategy=binpacking.PickStrategy.SMALLER_FIRST)
    b0, b1, b2, b3, b4, b5, b6 = packer.bins
    assert len(b0.items) == 0
    assert b0.get_total_weight() == 0

    assert len(b1.items) == 0
    assert b1.get_total_weight() == 0

    assert len(b2.items) == 0
    assert b2.get_total_weight() == 0

    assert len(b3.items) == 6
    assert b3.get_total_weight() == 21

    assert len(b4.items) == 6
    assert b4.get_total_weight() == 21

    assert len(b5.items) == 9
    assert b5.get_total_weight() == 45

    assert len(b6.items) == 9
    assert b6.get_total_weight() == 45


def test_example_bigger_first(packer):
    packer.pack(pick_strategy=binpacking.PickStrategy.BIGGER_FIRST)
    b0, b1, b2, b3, b4, b5, b6 = packer.bins
    assert len(b0.items) == 9
    assert b0.get_total_weight() == 45

    assert len(b1.items) == 9
    assert b1.get_total_weight() == 45

    assert len(b2.items) == 6
    assert b2.get_total_weight() == 25

    assert len(b3.items) == 5
    assert b3.get_total_weight() == 30

    assert len(b4.items) == 0
    assert b4.get_total_weight() == 0

    assert len(b5.items) == 0
    assert b5.get_total_weight() == 0

    assert len(b6.items) == 0
    assert b6.get_total_weight() == 0


if __name__ == "__main__":
    pytest.main([__file__])
