#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.addons import binpacking as bp


class TestGene:
    def test_init_default(self):
        dna = bp.DNA(20)
        assert len(dna) == 20
        assert all(v == 0.0 for v in dna) is True

    def test_init_value(self):
        dna = bp.DNA(20, 1.0)
        assert all(v == 1.0 for v in dna) is True

    @pytest.mark.parametrize("value", [-0.1, 1.1])
    def test_init_value_is_valid(self, value):
        with pytest.raises(ValueError):
            bp.DNA(20, value)

    def test_iter(self):
        dna = bp.DNA(20)
        assert len(list(dna)) == 20

    def test_reset_data(self):
        dna = bp.DNA(20)
        dna.reset([0.5] * 20)
        assert len(dna) == 20
        assert dna[7] == 0.5

    @pytest.mark.parametrize(
        "values",
        [
            [0, 0, 0],
            [2, 2, 2, 2, 2],
        ],
    )
    def test_reset_data_checks_validity(self, values):
        dna = bp.DNA(5)
        with pytest.raises(ValueError):
            dna.reset(values)

    def test_new_random_gene(self):
        dna = bp.DNA.random(20)
        assert len(dna) == 20
        assert len(set(dna)) > 10

    def test_replace_tail(self):
        dna = bp.DNA(20)
        dna.replace_tail([0.1, 0.2, 0.3])
        assert len(dna) == 20
        assert dna[-3:] == pytest.approx([0.1, 0.2, 0.3])
        assert sum(dna) == pytest.approx(0.6)

    def test_mutate(self):
        dna1 = bp.DNA(20)
        dna2 = dna1.copy()
        assert dna1 == dna2
        dna1.mutate(0.7)
        assert dna1 != dna2


def test_recombine_genes():
    dna1 = bp.DNA(20, 0.0)
    dna2 = bp.DNA(20, 1.0)
    bp.recombine_dna(dna1, dna2, 7)
    assert list(dna1[0:7]) == [0.0] * 7
    assert list(dna1[7:]) == [1.0] * 13
    assert list(dna2[0:7]) == [1.0] * 7
    assert list(dna2[7:]) == [0.0] * 13


if __name__ == "__main__":
    pytest.main([__file__])
