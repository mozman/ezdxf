#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from datetime import datetime
from ezdxf._acis import sab

T = sab.Tags


def test_decode_header(cube_sab):
    decoder = sab.Decoder(cube_sab)
    header = decoder.read_header()
    assert header.version == 21800
    assert header.n_records == 0
    assert header.n_entities == 2
    assert header.flags == 12
    assert header.product_id == "Open Design Alliance ACIS Builder"
    assert header.acis_version == "ACIS 218.00 NT"
    assert header.creation_date == datetime(2022, 5, 2, 5, 33, 25)
    assert header.units_in_mm == 1.0


def test_decode_first_record(cube_sab):
    decoder = sab.Decoder(cube_sab)
    _ = decoder.read_header()
    record = decoder.read_record()
    assert record == [
        (T.ENTITY_TYPE, "asmheader"),
        (T.POINTER, -1),
        (T.INT, -1),
        (T.STR, "208.0.4.7009"),
    ]


def test_decode_all_records(cube_sab):
    decoder = sab.Decoder(cube_sab)
    _ = decoder.read_header()
    records = list(decoder.read_records())
    assert len(records) == 116
    assert records[-1][0].value == "End-of-ASM-data"


def test_parse_sab(cube_sab):
    builder = sab.parse_sab(cube_sab)
    assert builder.header.version == 21800
    assert len(builder.entities) == 116
    assert builder.entities[0].name == "asmheader"
    assert builder.entities[-1].name == "End-of-ASM-data"


class TestSabEntity:
    @pytest.fixture(scope="class")
    def builder(self, cube_sab):
        return sab.parse_sab(cube_sab)

    @pytest.fixture(scope="class")
    def body(self, builder):
        return builder.bodies[0]

    def test_get_pointer_at_index(self, body):
        assert body.name == "body"
        assert body.attributes.is_null_ptr is False


if __name__ == "__main__":
    pytest.main([__file__])
