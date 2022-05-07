#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.acis import load


def test_load_any_format(any_cube):
    bodies = load(any_cube)
    assert len(bodies) == 1


class TestBody:
    @pytest.fixture(scope="class")
    def body(self, any_cube):
        return load(any_cube)[0]

    def test_has_transform_attribute(self, body):
        assert body.transform.is_null_ptr is False

    def test_transformation_attribute_loaded(self, body):
        m = body.transform.matrix
        assert m.get_row(3) == (388.5, 388.5, 388.5, 1.0)


if __name__ == "__main__":
    pytest.main([__file__])
