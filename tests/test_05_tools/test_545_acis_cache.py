# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
import pytest

import ezdxf
from ezdxf.acis import api as acis


def test_create_a_new_cache():
    cache = acis.AcisCache()

    assert len(cache) == 0


def test_get_bodies_from_sat_data(cube_sat: str):
    cache = acis.AcisCache()
    bodies = cache.get_bodies(cube_sat)

    assert len(bodies) == 1
    assert isinstance(bodies[0], acis.Body)
    assert len(cache) == 1

def test_empty_data_does_not_create_cache_entries():
    cache = acis.AcisCache()
    bodies = cache.get_bodies([])

    assert len(bodies) == 0
    assert len(cache) == 0


def test_get_bodies_from_sab_data(cube_sab: bytes):
    cache = acis.AcisCache()
    bodies = cache.get_bodies(cube_sab)

    assert len(bodies) == 1
    assert isinstance(bodies[0], acis.Body)
    assert len(cache) == 1


def test_add_only_unique_entries(cube_sat: str):
    cache = acis.AcisCache()
    cache.get_bodies(cube_sat)
    cache.get_bodies(cube_sat)

    assert len(cache) == 1, "should not create duplicate entries"


hash_data = acis.AcisCache.hash_data


class TestHashData:
    def test_empty_string(self):
        if ezdxf.PYPY:
            assert hash_data("") != 0
        else:
            assert hash_data("") == 0

    def test_string(self):
        h = hash_data("abc")
        assert isinstance(h, int)
        assert h != 0
        assert h == hash_data("abc")

    def test_strings(self):
        data = ["abc", "def"]
        h = hash_data(data)
        assert isinstance(h, int)
        assert h != 0
        assert h == hash_data(("abc", "def"))

    def test_empty_string_list(self):
        data = []
        h = hash_data(data)
        assert isinstance(h, int)
        assert h != 0
        assert h == hash_data(data)

        # surprise?
        assert hash(tuple()) == hash(tuple())
        assert id(tuple()) == id(tuple())

    def test_empty_bytes(self):
        if ezdxf.PYPY:
            assert hash_data(b"") != 0
        else:
            assert hash_data(b"") == 0

    def test_bytes(self):
        data = b"\x07\x08\x09"
        h = hash_data(data)
        assert isinstance(h, int)
        assert h != 0
        assert h == hash_data(b"\x07\x08\x09")

    def test_bytearray(self):
        data = bytearray([7, 8, 9])
        h = hash_data(data)
        assert isinstance(h, int)
        assert h != 0
        assert h == hash_data(b"\x07\x08\x09")


if __name__ == "__main__":
    pytest.main([__file__])
