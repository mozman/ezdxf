#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.acis import load


def test_load_any_format(any_cube):
    bodies = load(any_cube)
    assert len(bodies) == 1


@pytest.fixture(scope="module")
def body(any_cube):
    return load(any_cube)[0]


class TestBody:
    def test_type_type(self, body):
        assert body.type == "body"

    def test_has_transform_attribute(self, body):
        assert body.transform.is_null_ptr is False

    def test_transform_attribute_was_loaded(self, body):
        m = body.transform.matrix
        assert m.get_row(3) == (388.5, 388.5, 388.5, 1.0)

    def test_has_lump_attribute(self, body):
        assert body.lump.is_null_ptr is False

    def test_has_wire_attribute(self, body):
        assert body.wire.is_null_ptr is True


class TestLump:
    def test_root_lump(self, body):
        assert body.lump.is_null_ptr is False

    def test_lump_type(self, body):
        assert body.lump.type == "lump"

    def test_back_pointer_to_body(self, body):
        assert body.lump.body is body

    def test_has_no_next_lump(self, body):
        assert body.lump.next_lump.is_null_ptr is True

    def test_has_attribute_to_first_shell(self, body):
        assert body.lump.shell.is_null_ptr is False


if __name__ == "__main__":
    pytest.main([__file__])
