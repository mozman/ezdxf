#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
# Test only basic features of Cython implementation,
# Full testing and compatibility check with Python implementation
# is located in test suite 605.

import pytest

matrix44 = pytest.importorskip('ezdxf.acc.matrix44')
Matrix44 = matrix44.Matrix44


def test_default_constructor():
    m = Matrix44()
    assert m[0, 0] == 1.0
    assert m[1, 1] == 1.0
    assert m[2, 2] == 1.0
    assert m[3, 3] == 1.0


def test_16_numbers_constructor():
    m = Matrix44(range(16))
    assert m[3, 3] == 15


def test_numbers_constructor_invalid_number_count_error():
    with pytest.raises(ValueError):
        Matrix44(range(15))
    with pytest.raises(ValueError):
        Matrix44(range(17))


def test_4_rows_constructor():
    m = Matrix44(
        (0, 0, 0, 0),
        (1, 1, 1, 1),
        (2, 2, 2, 2),
        (3, 3, 3, 3)
    )
    assert m[0, 0] == 0
    assert m[3, 3] == 3


def test_rows_constructor_invalid_number_count():
    with pytest.raises(ValueError):
        Matrix44(
            (0, 0, 0, 0),
            (1, 1, 1, 1),
            (2, 2, 2, 2),
            (3, 3, 3)
        )
    with pytest.raises(ValueError):
        Matrix44(
            (0, 0, 0, 0),
            (1, 1, 1, 1),
            (2, 2, 2, 2),
            (3, 3, 3, 3, 3)
        )


def test_get_item_index_error():
    with pytest.raises(IndexError):
        _ = Matrix44()[(-1, -1)]
    with pytest.raises(IndexError):
        _ = Matrix44()[(0, 4)]
    with pytest.raises(IndexError):
        _ = Matrix44()[(1, -1)]
    with pytest.raises(IndexError):
        _ = Matrix44()[4, 4]


def test_get_item_does_not_support_slicing():
    with pytest.raises(TypeError):
        _ = Matrix44()[:]


def test_set_item():
    m = Matrix44()
    m[0, 0] = 17
    assert m[0, 0] == 17


def test_set_item_index_error():
    with pytest.raises(IndexError):
        Matrix44()[-1, -1] = 0
    with pytest.raises(IndexError):
        Matrix44()[4, 4] = 0


def test_set_item_does_not_support_slicing():
    with pytest.raises(TypeError):
        Matrix44()[:] = (1, 2)


def test_set_row_4_values():
    m = Matrix44()
    m.set_row(0, (2, 3, 4, 5))
    assert m.get_row(0) == (2, 3, 4, 5)


def test_set_row_1_value():
    m = Matrix44()
    m.set_row(1, (2,))
    assert m.get_row(1) == (2, 1, 0, 0)


def test_get_row_index_error():
    with pytest.raises(IndexError):
        Matrix44().get_row(-1)
    with pytest.raises(IndexError):
        Matrix44().get_row(4)


def test_set_row_index_error():
    with pytest.raises(IndexError):
        Matrix44().set_row(-1, (0,))
    with pytest.raises(IndexError):
        Matrix44().set_row(4, (0,))


def test_set_col_4_values():
    m = Matrix44()
    m.set_col(0, (2, 3, 4, 5))
    assert m.get_col(0) == (2, 3, 4, 5)


def test_set_col_1_value():
    m = Matrix44()
    m.set_col(1, (2,))
    assert m.get_col(1) == (2, 1, 0, 0)


def test_get_col_index_error():
    with pytest.raises(IndexError):
        Matrix44().get_col(-1)
    with pytest.raises(IndexError):
        Matrix44().get_col(4)


def test_set_col_index_error():
    with pytest.raises(IndexError):
        Matrix44().set_col(-1, (0,))
    with pytest.raises(IndexError):
        Matrix44().set_col(4, (0,))


def test_copy():
    m1 = Matrix44(range(16))
    m2 = m1.copy()
    assert m2.get_row(0) == (0, 1, 2, 3)
    m1.set_row(0, (20, 30, 40, 50))
    assert m1.get_row(0) == (20, 30, 40, 50)
    assert m2.get_row(0) == (0, 1, 2, 3)


def test_get_origin():
    m = Matrix44()
    m.set_row(3, (7, 8, 9))
    assert m.origin == (7, 8, 9)


if __name__ == '__main__':
    pytest.main([__file__])
