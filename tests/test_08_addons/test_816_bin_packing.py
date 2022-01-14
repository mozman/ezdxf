#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pytest

from ezdxf.addons.binpacking import Bin3d, Item, Packer3d
UNLIMITED = 1_000_000


def test_single_bin_single_item():
    bin0 = Bin3d("B0", 1, 1, 1, UNLIMITED)
    packer = Packer3d()
    packer.add_bin(bin0)
    packer.add_item(Item("I0", 1, 1, 1, 1))
    packer.pack()
    assert len(bin0.items) == 1
    assert len(bin0.unfitted_items) == 0


@pytest.mark.parametrize("w,h,d", [
    (3, 1, 1),
    (1, 3, 1),
    (1, 1, 3),
])
def test_single_bin_multiple_items(w, h, d):
    bin0 = Bin3d("B0", w, h, d, UNLIMITED)
    packer = Packer3d()
    packer.add_bin(bin0)
    for index in range(max(w, h, d)):
        packer.add_item(Item(f"I{index}", 1, 1, 1, 1))
    packer.pack()
    assert len(bin0.items) == 3
    assert len(bin0.unfitted_items) == 0


def test_single_bin_different_sized_items():
    bin0 = Bin3d("B0", 3, 3, 1, UNLIMITED)
    packer = Packer3d()
    packer.add_bin(bin0)
    packer.add_item(Item("I0", 1, 1, 1, 1))
    packer.add_item(Item("I1", 2, 1, 1, 1))
    packer.add_item(Item("I2", 3, 1, 1, 1))
    packer.pack()
    assert len(bin0.items) == 3
    assert len(bin0.unfitted_items) == 0


if __name__ == '__main__':
    pytest.main([__file__])


def test_example():
    packer = Packer3d()
    packer.add_bin(Bin3d("small-envelope", 11.5, 6.125, 0.25, 10))
    packer.add_bin(Bin3d("large-envelope", 15.0, 12.0, 0.75, 15))
    packer.add_bin(Bin3d("small-box", 8.625, 5.375, 1.625, 70.0))
    packer.add_bin(Bin3d("medium-box", 11.0, 8.5, 5.5, 70.0))
    packer.add_bin(Bin3d("medium-2-box", 13.625, 11.875, 3.375, 70.0))
    packer.add_bin(Bin3d("large-box", 12.0, 12.0, 5.5, 70.0))
    packer.add_bin(Bin3d("large-2-box", 23.6875, 11.75, 3.0, 70.0))

    packer.add_item(Item("50g [powder 1]", 3.9370, 1.9685, 1.9685, 1))
    packer.add_item(Item("50g [powder 2]", 3.9370, 1.9685, 1.9685, 2))
    packer.add_item(Item("50g [powder 3]", 3.9370, 1.9685, 1.9685, 3))
    packer.add_item(Item("250g [powder 4]", 7.8740, 3.9370, 1.9685, 4))
    packer.add_item(Item("250g [powder 5]", 7.8740, 3.9370, 1.9685, 5))
    packer.add_item(Item("250g [powder 6]", 7.8740, 3.9370, 1.9685, 6))
    packer.add_item(Item("250g [powder 7]", 7.8740, 3.9370, 1.9685, 7))
    packer.add_item(Item("250g [powder 8]", 7.8740, 3.9370, 1.9685, 8))
    packer.add_item(Item("250g [powder 9]", 7.8740, 3.9370, 1.9685, 9))

    packer.pack(bigger_first=False)
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


if __name__ == '__main__':
    pytest.main([__file__])
