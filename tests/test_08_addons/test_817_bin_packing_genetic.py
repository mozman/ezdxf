#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.addons import binpacking


class TestGene:
    def test_init_default(self):
        g = binpacking.Gene(20)
        assert len(g) == 20
        assert all(v == 0.0 for v in g) is True

    def test_init_value(self):
        g = binpacking.Gene(20, 1.0)
        assert all(v == 1.0 for v in g) is True

    @pytest.mark.parametrize("value", [-0.1, 1.1])
    def test_init_value_is_valid(self, value):
        with pytest.raises(ValueError):
            binpacking.Gene(20, value)

    def test_iter(self):
        g = binpacking.Gene(20)
        assert len(list(g)) == 20

    def test_reset_data(self):
        g = binpacking.Gene(20)
        g.reset([0.5] * 20)
        assert len(g) == 20
        assert g[7] == 0.5

    @pytest.mark.parametrize(
        "values",
        [
            [0, 0, 0],
            [2, 2, 2, 2, 2],
        ],
    )
    def test_reset_data_checks_validity(self, values):
        g = binpacking.Gene(5)
        with pytest.raises(ValueError):
            g.reset(values)

    def test_new_random_gene(self):
        g = binpacking.Gene.random(20)
        assert len(g) == 20
        assert len(set(g)) > 10

    def test_replace_tail(self):
        g = binpacking.Gene(20)
        g.replace_tail([0.1, 0.2, 0.3])
        assert len(g) == 20
        assert g[-3:] == pytest.approx([0.1, 0.2, 0.3])
        assert sum(g) == pytest.approx(0.6)

    def test_mutate(self):
        g1 = binpacking.Gene(20)
        g2 = g1.copy()
        assert g1 == g2
        g1.mutate(0.7)
        assert g1 != g2


def test_recombine_genes():
    g1 = binpacking.Gene(20, 0.0)
    g2 = binpacking.Gene(20, 1.0)
    binpacking.recombine_genes(g1, g2, 7)
    assert list(g1[0:7]) == [0.0] * 7
    assert list(g1[7:]) == [1.0] * 13
    assert list(g2[0:7]) == [1.0] * 7
    assert list(g2[7:]) == [0.0] * 13


if __name__ == "__main__":
    pytest.main([__file__])
