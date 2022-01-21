#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.addons import dnapacking as dp
from ezdxf.addons import binpacking as bp


class TestFloatDNA:
    def test_init_value(self):
        dna = dp.FloatDNA([1.0] * 20)
        assert all(v == 1.0 for v in dna) is True

    @pytest.mark.parametrize("value", [-0.1, 1.1])
    def test_init_value_is_valid(self, value):
        with pytest.raises(ValueError):
            dp.FloatDNA([value] * 20)

    def test_iter(self):
        dna = dp.FloatDNA([1.0] * 20)
        assert len(list(dna)) == 20

    def test_reset_data(self):
        dna = dp.FloatDNA([0.0] * 20)
        dna.reset([0.5] * 20)
        assert len(dna) == 20
        assert dna[7] == 0.5

    @pytest.mark.parametrize(
        "values",
        [
            [0, 0, -1],
            [2, 2, 2, 2, 2],
        ],
    )
    def test_reset_data_checks_validity(self, values):
        dna = dp.FloatDNA([])
        with pytest.raises(ValueError):
            dna.reset(values)

    def test_new_random_gene(self):
        dna = dp.FloatDNA.random(20)
        assert len(dna) == 20
        assert len(set(dna)) > 10

    def test_subscription_setter(self):
        dna = dp.FloatDNA([0.0] * 20)
        dna[-3:] = [0.1, 0.2, 0.3]
        assert len(dna) == 20
        assert dna[-3:] == pytest.approx([0.1, 0.2, 0.3])
        assert sum(dna) == pytest.approx(0.6)

    def test_mutate_flip(self):
        dna1 = dp.FloatDNA([0.0] * 20)
        dna2 = dna1.copy()
        assert dna1 == dna2
        dna1.mutate(0.7, dp.MutationType.FLIP)
        assert dna1 != dna2

    def test_mutate_swap(self):
        dna1 = dp.FloatDNA.random(20)
        dna2 = dna1.copy()
        assert dna1 == dna2
        dna1.mutate(0.7, dp.MutationType.SWAP)
        assert dna1 != dna2


class TestBitDNA:
    def test_init_value(self):
        dna = dp.BitDNA([1] * 20)
        assert all(v is True for v in dna) is True

    def test_reset_data(self):
        dna = dp.BitDNA([1] * 20)
        dna.reset([False] * 20)
        assert len(dna) == 20
        assert dna[7] is False

    def test_new_random_gene(self):
        dna = dp.BitDNA.random(20)
        assert len(dna) == 20
        assert len(set(dna)) == 2

    def test_subscription_setter(self):
        dna = dp.BitDNA([1] * 20)
        dna[-3:] = [False, False, False]
        assert len(dna) == 20
        assert dna[-4:] == [True, False, False, False]

    def test_mutate_flip(self):
        dna1 = dp.BitDNA([1] * 20)
        dna2 = dna1.copy()
        assert dna1 == dna2
        dna1.mutate(0.7, dp.MutationType.FLIP)
        assert dna1 != dna2


def test_single_point_crossover():
    dna1 = dp.BitDNA([False] * 20)
    dna2 = dp.BitDNA([True] * 20)
    dp.recombine_dna_1pcx(dna1, dna2, 7)
    assert list(dna1[0:7]) == [False] * 7
    assert list(dna1[7:]) == [True] * 13
    assert list(dna2[0:7]) == [True] * 7
    assert list(dna2[7:]) == [False] * 13


def test_two_point_crossover():
    dna1 = dp.BitDNA([False] * 20)
    dna2 = dp.BitDNA([True] * 20)
    dp.recombine_dna_2pcx(dna1, dna2, 7, 11)
    assert list(dna1[0:7]) == [False] * 7
    assert list(dna1[7:11]) == [True] * 4
    assert list(dna1[11:]) == [False] * 9
    assert list(dna2[0:7]) == [True] * 7
    assert list(dna2[7:11]) == [False] * 4
    assert list(dna2[11:]) == [True] * 9


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


class TestGeneticDriver:
    def test_init(self, packer):
        driver = dp.GeneticDriver(packer, 100)
        assert driver.is_executed is False

    def test_init_invalid_packer(self, packer):
        """Packer is already packed."""
        pack(packer, SMALL_BOX, bp.PickStrategy.SMALLER_FIRST)
        with pytest.raises(ValueError):
            dp.GeneticDriver(packer, 100)

    def test_init_invalid_max_runs(self, packer):
        with pytest.raises(ValueError):
            dp.GeneticDriver(packer, 0)

    def test_can_only_run_once(self, packer):
        driver = dp.GeneticDriver(packer, 100)
        driver.execute()
        assert driver.is_executed is True
        with pytest.raises(TypeError):
            driver.execute()

    def test_execution(self, packer):
        packer.add_bin(*MEDIUM_BOX)
        driver = dp.GeneticDriver(packer, 10)
        driver.add_random_dna(20)
        driver.execute()
        assert driver.generation == 10
        assert driver.best_fitness > 0.1
        assert len(driver.best_packer.bins[0].items) > 1


if __name__ == "__main__":
    pytest.main([__file__])
