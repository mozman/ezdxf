#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pytest
from datetime import datetime
from ezdxf.acis import sat, hdr, const
from ezdxf.version import __version__


def test_default_header():
    header = hdr.AcisHeader()
    assert header.version == const.MIN_EXPORT_VERSION
    assert header.n_entities == 0
    assert header.n_records == 0
    assert isinstance(header.creation_date, datetime)


LEN = len(__version__) + 20

HEADER_400 = f"""400 0 1 0 
{LEN} ezdxf v{__version__} ACIS Builder 12 ACIS 4.00 NT 24 Sat Jan  1 10:00:00 2022 
1 9.9999999999999995e-007 1e-010 """

HEADER_700 = f"""700 0 1 0 
@{LEN} ezdxf v{__version__} ACIS Builder @12 ACIS 32.0 NT @24 Sat Jan  1 10:00:00 2022 
1 9.9999999999999995e-007 1e-010 """

HEADER_21800 = f"""21800 0 1 0 
@{LEN} ezdxf v{__version__} ACIS Builder @14 ACIS 218.00 NT @24 Sat Jan  1 10:00:00 2022 
1 9.9999999999999995e-007 1e-010 """


@pytest.mark.parametrize(
    "ver,s",
    [
        (400, HEADER_400),
        (700, HEADER_700),
        (21800, HEADER_21800),
    ],
)
def test_dump_header_string(ver, s):
    header = hdr.AcisHeader()
    header.set_version(ver)
    header.creation_date = datetime(2022, 1, 1, 10, 00)
    header.n_entities = 1
    data = header.dumps()

    assert "\n".join(header.dumps()) == s


@pytest.mark.parametrize(
    "s",
    [
        "18 ezdxf ACIS Builder 14 ACIS 208.00 NT 24 Sat Jan  1 10:00:00 2022 ",
        "@18 ezdxf ACIS Builder @14 ACIS 208.00 NT @24 Sat Jan  1 10:00:00 2022 ",
    ],
)
def test_parse_header_str(s):
    tokens = list(sat.parse_header_str(s))
    assert tokens == [
        "ezdxf ACIS Builder",
        "ACIS 208.00 NT",
        "Sat Jan  1 10:00:00 2022",
    ]


@pytest.mark.parametrize("hdr,ver", [(HEADER_400, 400), (HEADER_21800, 21800)])
def test_parse_sat_header(hdr, ver):
    header, data = sat.parse_header(hdr.split("\n"))
    assert len(data) == 0
    assert header.version == ver
    assert header.product_id == f"ezdxf v{__version__} ACIS Builder"
    assert header.n_entities == 1
    assert header.creation_date == datetime(2022, 1, 1, 10, 00)


class TestMergeRecordStrings:
    @pytest.mark.parametrize(
        "data",
        [
            ["test 1 2 3 #", "End-of-ACIS-data", "test 4 5 6"],
            ["test 4 5 6 #", "Begin-of-ACIS-History-data", "test 4 5 6"],
        ],
    )
    def test_end_of_records_detection(self, data):
        assert len(list(sat.merge_record_strings(data))) == 1

    @pytest.mark.parametrize(
        "data",
        [
            ["test 1 2 3 #", "test 1 2 3 #"],
            ["test 4 5 6 ", "1 2 3 #", "test 1 2 3 #"],
            ["test 4 5 6 #", "test 1 2 3 ", "4 5 6 #"],
        ],
    )
    def test_merge_records(self, data):
        assert len(list(sat.merge_record_strings(data))) == 2

    def test_weird_placement_of_record_terminator(self):
        """This example was found in a SAT exported by BricsCAD."""
        data = [
            "eye_refinement ... end_fields #",
            "integer_attrib-name_attrib-gen-attrib ... #torus-surface ...",
            "I I I I #",
        ]
        records = list(sat.merge_record_strings(data))
        assert records[0] == "eye_refinement ... end_fields"
        assert records[1] == "integer_attrib-name_attrib-gen-attrib ..."
        assert records[2] == "torus-surface ... I I I I"


class TestParseRecords:
    def test_simple_case(self):
        records = sat.parse_records(["test 1 2 3 #", "test 4 5 6 #"])
        assert len(records) == 2
        assert records[0] == ["test", "1", "2", "3"]
        assert records[1] == ["test", "4", "5", "6"]

    def test_sequence_numbers(self):
        records = sat.parse_records(["-0 test 1 2 3 #", " -1 test 4 5 6 #"])
        assert len(records) == 2
        assert records[0] == ["test", "1", "2", "3"]
        assert records[1] == ["test", "4", "5", "6"]

    def test_non_continuous_sequence_numbers_raises_exception(self):
        with pytest.raises(sat.ParsingError):
            sat.parse_records(["-0 test 1 2 3 #", " -2 test 4 5 6 #"])

    @pytest.mark.parametrize(
        "data",
        [
            ["sentinel 7 #", "test 1 2 3 4 5 6 #", "sentinel 8 #"],
            ["sentinel 7 #", "test 1 2 3", " 4 5 6 #", "sentinel 8 #"],
            [
                "sentinel 7 #",
                "test",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "#",
                "sentinel 8 #",
            ],
        ],
    )
    def test_merged_records(self, data):
        records = sat.parse_records(data)
        assert records[0] == ["sentinel", "7"]
        assert records[1] == ["test", "1", "2", "3", "4", "5", "6"]
        assert records[2] == ["sentinel", "8"]


def test_build_entities(prism_sat):
    data = prism_sat.splitlines()
    records = sat.parse_records(data[3:])
    entities = sat.build_entities(records, 700)
    assert len(entities) == 113
    assert entities[0].name == "body"
    assert entities[112].name == "straight-curve"


class TestAcisBuilder:
    @pytest.fixture(scope="class")
    def builder(self, prism_sat):
        return sat.parse_sat(prism_sat)

    def test_parsing_result(self, builder):
        assert builder.header.version == 700
        assert len(builder.bodies) == 1
        assert len(builder.entities) == 113

    def test_body_entity(self, builder):
        body = builder.bodies[0]
        assert body.name == "body"
        assert len(body.data) == 4
        assert body.data[1].name == "lump", "string ptr should be resolved"

    def test_ptr_resolving(self, builder):
        assert builder.entities[0].name == "body"
        assert builder.entities[112].name == "straight-curve"

    def test_attr_ptr_is_reset(self, builder):
        assert all(e.attr_ptr == "$-1" for e in builder.entities)

    def test_dump_sat_recreates_the_source_structure(self, builder, prism_sat):
        lines = builder.dump_sat()
        assert len(lines) == 117
        assert lines == prism_sat.splitlines()


def test_build_str_records():
    a = sat.new_entity("test1", data=[sat.NULL_PTR, 1])
    b = sat.new_entity("test2", id=7, data=[a, 2.0])
    c = sat.new_entity("test3", data=[a, b])
    entities = [a, b, c]
    s = list(sat.build_str_records(entities, 700))
    assert s[0] == "test1 $-1 -1 $-1 1 #"
    assert s[1] == "test2 $-1 7 $0 2.0 #"
    assert s[2] == "test3 $-1 -1 $0 $1 #"


if __name__ == "__main__":
    pytest.main([__file__])
