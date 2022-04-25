#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from datetime import datetime
from ezdxf import acis


def test_new_acis_tree():
    atree = acis.new_tree()
    assert atree.header is not None


def test_default_header():
    header = acis.AcisHeader()
    assert header.version == 400
    assert header.acis_version == "ACIS 4.00 NT"
    assert header.n_entities == 0
    assert header.n_records == 0
    assert isinstance(header.creation_date, datetime)


HEADER_400 = """400 0 1 0 
18 ezdxf ACIS Builder 12 ACIS 4.00 NT 24 Sat Jan  1 10:00:00 2022 
1 9.9999999999999995e-007 1e-010"""

HEADER_20800 = """20800 0 1 0 
@18 ezdxf ACIS Builder @14 ACIS 208.00 NT @24 Sat Jan  1 10:00:00 2022 
1 9.9999999999999995e-007 1e-010"""


def test_dump_header_string_400():
    header = acis.AcisHeader()
    header.creation_date = datetime(2022, 1, 1, 10, 00)
    header.n_entities = 1
    assert header.dumps() == HEADER_400


def test_dump_header_string_20800():
    header = acis.AcisHeader()
    header.set_version(20800)
    header.creation_date = datetime(2022, 1, 1, 10, 00)
    header.n_entities = 1
    assert header.dumps() == HEADER_20800


@pytest.mark.parametrize(
    "s",
    [
        "18 ezdxf ACIS Builder 14 ACIS 208.00 NT 24 Sat Jan  1 10:00:00 2022 ",
        "@18 ezdxf ACIS Builder @14 ACIS 208.00 NT @24 Sat Jan  1 10:00:00 2022 ",
    ],
)
def test_parse_header_str(s):
    tokens = list(acis._parse_header_str(s))
    assert tokens == [
        "ezdxf ACIS Builder",
        "ACIS 208.00 NT",
        "Sat Jan  1 10:00:00 2022",
    ]


@pytest.mark.parametrize("hdr,ver", [(HEADER_400, 400), (HEADER_20800, 20800)])
def test_parse_sat_header(hdr, ver):
    header, data = acis.parse_sat_header(hdr.split("\n"))
    assert len(data) == 0
    assert header.version == ver
    assert header.product_id == "ezdxf ACIS Builder"
    assert header.n_entities == 1
    assert header.creation_date == datetime(2022, 1, 1, 10, 00)


class TestMergeRecordStrings:
    @pytest.mark.parametrize(
        "data",
        [
            ["test 1 2 3 #", "End-of-ACIS-data", "test 4 5 6"],
            ["test 4 5 6 #", "Begin-of-ACIS-History-Data", "test 4 5 6"],
        ],
    )
    def test_end_of_records_detection(self, data):
        assert len(list(acis._merge_record_strings(data))) == 1

    @pytest.mark.parametrize(
        "data",
        [
            ["test 1 2 3 #", "test 1 2 3 #"],
            ["test 4 5 6 ", "1 2 3 #", "test 1 2 3 #"],
            ["test 4 5 6 #", "test 1 2 3 ", "4 5 6 #"],
        ],
    )
    def test_merge_records(self, data):
        assert len(list(acis._merge_record_strings(data))) == 2


class TestParseRecords:
    def test_simple_case(self):
        records = acis.parse_records(["test 1 2 3 #", "test 4 5 6 #"])
        assert len(records) == 2
        assert records[0].num == 0
        assert records[0].tokens == ["test", "1", "2", "3"]
        assert records[1].num == 1
        assert records[1].tokens == ["test", "4", "5", "6"]

    def test_numbered_records(self):
        records = acis.parse_records(["2= test 1 2 3 #", " 4= test 4 5 6 #"])
        assert len(records) == 2
        assert records[0].num == 2
        assert records[0].tokens == ["test", "1", "2", "3"]
        assert records[1].num == 4
        assert records[1].tokens == ["test", "4", "5", "6"]

    @pytest.mark.parametrize("data", [
        ["sentinel 7 #", "test 1 2 3 4 5 6 #", "sentinel 8 #"],
        ["sentinel 7 #", "test 1 2 3", " 4 5 6 #", "sentinel 8 #"],
        ["sentinel 7 #", "test", "1", "2", "3", "4", "5", "6", "#", "sentinel 8 #"],
    ])
    def test_merged_records(self, data):
        records = acis.parse_records(data)
        assert records[0].tokens == ["sentinel", "7"]
        assert records[1].tokens == ["test", "1", "2", "3", "4", "5", "6"]
        assert records[2].tokens == ["sentinel", "8"]


if __name__ == "__main__":
    pytest.main([__file__])
