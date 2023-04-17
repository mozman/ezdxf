# Copyright (c) 2023, Manfred Moitzi
# License: MIT License

import pytest
import pickle
from math import radians

# Import from 'ezdxf.math._matrix33' to test Python implementation
from ezdxf.math._matrix33 import Matrix33
from ezdxf.acc import USE_C_EXT

m33_classes = [Matrix33]

if USE_C_EXT:
    from ezdxf.acc.matrix33 import Matrix33 as CMatrix33
    m33_classes.append(CMatrix33)


@pytest.fixture(params=m33_classes)
def m33(request):
    return request.param


class TestMatrix33:
    def test_default_constructor(self, m33):
        matrix = m33((1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0))

        assert matrix.isclose(m33())

    def test_iter(self, m33):
        values = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        matrix = m33(values)
        for v1, m1 in zip(values, matrix):
            assert v1 == m1

    def test_invalid_number_constructor(self, m33):
        pytest.raises(ValueError, m33, range(17))
        pytest.raises(ValueError, m33, range(15))

    def test_translate(self, m33):
        t = m33.translate(10, 20)
        v = t.transform((1, 1))
        assert v.isclose((11, 21)) is True

    def test_scale(self, m33):
        t = m33.scale(10, 20)
        v = t.transform((3, 4))
        assert v.isclose((30, 80)) is True

    def test_rotate(self, m33):
        t = m33.rotate(radians(30))
        v = t.transform((4, 1))
        assert v.isclose((2.964101615137755, 2.8660254037844384)) is True

    def test_chain(self, m33):
        s = m33.scale(10, 20)
        t = m33.translate(10, 20)

        c = m33.chain(s, t)
        v = c.transform((4, 1))
        assert v.isclose((50, 40)) is True

    def test_transform_direction(self, m33):
        s = m33.scale(10, 20)
        t = m33.translate(10, 20)

        c = m33.chain(s, t)
        v = c.transform_direction((4, 1))
        assert v.isclose((40, 20)) is True

    def test_transform_vertices(self, m33):
        s = m33.scale(10, 20)
        t = m33.translate(10, 20)

        c = s @ t
        v = list(c.transform_vertices([(4, 1), (5, 0)]))
        assert v[0].isclose((50, 40)) is True
        assert v[1].isclose((60, 20)) is True

    def test_multiply(self, m33):
        m1 = m33(range(9))
        m2 = m33(range(9))
        res = m1 @ m2
        expected = m33((15.0, 18.0, 21.0, 42.0, 54.0, 66.0, 69.0, 90.0, 111.0))
        assert expected.isclose(res)
        # __matmul__()
        res = m1 @ m2
        assert expected.isclose(res)


    def test_supports_pickle_protocol(self, m33):
        matrix = m33((0.1, 1, 2, 3, 4, 5, 6, 7, 8))
        pickled_matrix = pickle.loads(pickle.dumps(matrix))
        assert matrix.isclose(pickled_matrix)
