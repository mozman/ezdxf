#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pytest
from datetime import datetime
from ezdxf import acis
from ezdxf.acis import sat
from ezdxf.acis import parsing
from ezdxf.math import Vec3


def test_default_header():
    header = acis.AcisHeader()
    assert header.version == 400
    assert header.acis_version == "ACIS 4.00 NT"
    assert header.n_entities == 0
    assert header.n_records == 0
    assert isinstance(header.creation_date, datetime)


HEADER_400 = """400 0 1 0 
18 ezdxf ACIS Builder 12 ACIS 4.00 NT 24 Sat Jan  1 10:00:00 2022 
1 9.9999999999999995e-007 1e-010 """

HEADER_700 = """700 0 1 0 
@18 ezdxf ACIS Builder @12 ACIS 32.0 NT @24 Sat Jan  1 10:00:00 2022 
1 9.9999999999999995e-007 1e-010 """

HEADER_20800 = """20800 0 1 0 
@18 ezdxf ACIS Builder @14 ACIS 208.00 NT @24 Sat Jan  1 10:00:00 2022 
1 9.9999999999999995e-007 1e-010 """


@pytest.mark.parametrize(
    "ver,s",
    [
        (400, HEADER_400),
        (700, HEADER_700),
        (20800, HEADER_20800),
    ],
)
def test_dump_header_string(ver, s):
    header = acis.AcisHeader()
    header.set_version(ver)
    header.creation_date = datetime(2022, 1, 1, 10, 00)
    header.n_entities = 1
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


@pytest.mark.parametrize("hdr,ver", [(HEADER_400, 400), (HEADER_20800, 20800)])
def test_parse_sat_header(hdr, ver):
    header, data = sat.parse_header(hdr.split("\n"))
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
            ["test 4 5 6 #", "Begin-of-ACIS-History-data", "test 4 5 6"],
        ],
    )
    def test_end_of_records_detection(self, data):
        x = list(sat.merge_record_strings(data))
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
        return acis.parse_sat(prism_sat)

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

    def test_query_entities(self, builder):
        points = list(builder.query(lambda e: e.name == "point"))
        assert len(points) == 8

    def test_find_entities_in_nodes(self, builder):
        body = builder.bodies[0]
        face = body.find_first("lump").find_first("shell").find_first("face")
        assert face.name == "face"

    def test_find_entities_in_path(self, builder):
        body = builder.bodies[0]
        face = body.find_path("lump/shell/face")
        assert face.name == "face"

    def test_find_in_invalid_path_return_null_pointer(self, builder):
        body = builder.bodies[0]
        face = body.find_path("lump/xxx/face")
        assert face.is_null_ptr is True

    def test_find_all(self, builder):
        coedge = builder.entities[10]
        assert len(coedge.find_all("coedge")) == 3


def test_build_str_records():
    a = sat.new_entity("test1", data=[sat.NULL_PTR, 1])
    b = sat.new_entity("test2", id=7, data=[a, 2.0])
    c = sat.new_entity("test3", data=[a, b])
    entities = [a, b, c]
    s = list(sat.build_str_records(entities, 700))
    assert s[0] == "test1 $-1 -1 $-1 1 #"
    assert s[1] == "test2 $-1 7 $0 2.0 #"
    assert s[2] == "test3 $-1 -1 $0 $1 #"


class TestFindMultipleEntities:
    @pytest.fixture
    def entity(self):
        n = sat.NULL_PTR
        a1 = sat.new_entity("entity1")
        a2 = sat.new_entity("entity1")
        b1 = sat.new_entity("entity2")
        b2 = sat.new_entity("entity2")
        c = sat.new_entity("entity3")
        return sat.new_entity(
            "entity", data=[n, a1, a2, "1", b1, b2, c, n, "1.0"]
        )

    def test_find_first_entity1_and_first_entity2(self, entity):
        result = entity.find_entities("entity1;entity2")
        assert result[0].name == "entity1"
        assert result[1].name == "entity2"

    def test_find_first_entity1_and_first_entity3(self, entity):
        result = entity.find_entities("entity1;entity3")
        assert result[0].name == "entity1"
        assert result[1].name == "entity3"

    def test_find_first_entity4_and_first_entity3(self, entity):
        result = entity.find_entities("entity4;entity3")
        assert result[0] is sat.NULL_PTR
        assert result[1].name == "entity3"

    def test_find_first_entity2_and_first_entity4(self, entity):
        result = entity.find_entities("entity2;entity4")
        assert result[0].name == "entity2"
        assert result[1] is sat.NULL_PTR


class TestParseValues:
    def test_parse_integers(self):
        data = [sat.NULL_PTR, "1", "2", sat.NULL_PTR]
        assert sat.parse_values([], "i") == []
        assert sat.parse_values(data, "i") == [1]
        assert sat.parse_values(data, "i;i") == [1, 2]
        assert sat.parse_values(data, "i;i;i") == [1, 2]

    def test_parse_vec3(self):
        data = [sat.NULL_PTR, "1.0", "2.0", "3.0", sat.NULL_PTR]
        assert sat.parse_values([], "v") == []
        assert sat.parse_values(data, "v") == [(1.0, 2.0, 3.0)]

    def test_parse_floats(self):
        data = [sat.NULL_PTR, "1.0", "2.0", sat.NULL_PTR]
        assert sat.parse_values([], "f") == []
        assert sat.parse_values(data, "f") == [1.0]
        assert sat.parse_values(data, "f;f") == [1.0, 2.0]
        assert sat.parse_values(data, "f;f;f") == [1.0, 2.0]

    def test_parse_constant_boolean_strings(self):
        data = [sat.NULL_PTR, "1.0", "forward", "double", sat.NULL_PTR]
        assert sat.parse_values([], "b") == []
        assert sat.parse_values(data, "?;b") == [True]
        assert sat.parse_values(data, "?;b;b") == [True, False]

    def test_parse_user_strings(self):
        data = [sat.NULL_PTR, "@4", "usr1", "@4", "usr2", sat.NULL_PTR]
        assert sat.parse_values([], "@") == []
        assert sat.parse_values(data, "@") == ["usr1"]
        assert sat.parse_values(data, "@;@") == ["usr1", "usr2"]
        assert sat.parse_values(data, "@;@;@") == ["usr1", "usr2"]

    def test_parse_mixed_values(self):
        data = ["1.0", "@4", "usr1", "forward"]
        assert sat.parse_values(data, "f;@;b") == [1.0, "usr1", True]

    def test_value_order_must_match(self):
        data = ["not_a_float", "1.0"]
        with pytest.raises(sat.ParsingError):
            sat.parse_values(data, "f;f")

    def test_skip_unknown_values(self):
        data = ["7", "not_a_float", "1.0"]
        assert sat.parse_values(data, "i;?;f") == [7, 1.0]

    def test_ignore_entities_between_values(self):
        data = ["7", sat.NULL_PTR, "1.0"]
        assert sat.parse_values(data, "i;f") == [7, 1.0]


def test_parse_body_polygon_faces(prism_sat):
    builder = acis.parse_sat(prism_sat)
    lumps = list(parsing.body_planar_polygon_faces(builder.bodies[0]))
    assert len(lumps) == 1
    faces = lumps[0]
    assert len(faces) == 10


def test_body_to_mesh(prism_sat):
    builder = acis.parse_sat(prism_sat)
    meshes = acis.body_to_mesh(builder.bodies[0])
    assert len(meshes) == 1
    mesh = meshes[0]
    assert len(mesh.faces) == 10
    assert len(mesh.vertices) == 8


if __name__ == "__main__":
    pytest.main([__file__])
