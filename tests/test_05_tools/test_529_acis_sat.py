#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pytest
from datetime import datetime
from ezdxf import acis
from ezdxf.acis import sat
from ezdxf.acis import parsing

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


def test_build_entities():
    data = PRISM.splitlines()
    records = sat.parse_records(data[3:])
    entities = sat.build_entities(records, 700)
    assert len(entities) == 113
    assert entities[0].name == "body"
    assert entities[112].name == "straight-curve"


class TestAcisBuilder:
    @pytest.fixture(scope="class")
    def builder(self):
        return acis.parse_sat(PRISM)

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

    def test_dump_sat_recreates_the_source_structure(self, builder):
        lines = builder.dump_sat()
        assert len(lines) == 117
        assert lines == PRISM.splitlines()

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
        assert face is sat.NULL_PTR

    def test_find_all(self, builder):
        coedge = builder.entities[10]
        assert len(coedge.find_all("coedge")) == 3


def test_build_str_records():
    a = sat.new_sat_entity("test1", data=[sat.NULL_PTR, 1])
    b = sat.new_sat_entity("test2", id=7, data=[a, 2.0])
    c = sat.new_sat_entity("test3", data=[a, b])
    entities = [a, b, c]
    s = list(sat.build_str_records(entities, 700))
    assert s[0] == "test1 $-1 -1 $-1 1 #"
    assert s[1] == "test2 $-1 7 $0 2.0 #"
    assert s[2] == "test3 $-1 -1 $0 $1 #"


class TestFindMultipleEntities:
    @pytest.fixture
    def entity(self):
        n = sat.NULL_PTR
        a1 = sat.new_sat_entity("entity1")
        a2 = sat.new_sat_entity("entity1")
        b1 = sat.new_sat_entity("entity2")
        b2 = sat.new_sat_entity("entity2")
        c = sat.new_sat_entity("entity3")
        return sat.new_sat_entity(
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
    @pytest.fixture
    def entity(self):
        n = sat.NULL_PTR
        a = sat.new_sat_entity("entity1")
        b = sat.new_sat_entity("entity2")
        c = sat.new_sat_entity("entity3")
        return sat.new_sat_entity(
            "entity", data=[n, a, b, "1", c, n, "1.0"]
        )

    def test_parse_integers(self):
        data = [sat.NULL_PTR, "1", "2", sat.NULL_PTR]
        assert sat.parse_values([], "i") == []
        assert sat.parse_values(data, "i") == [1]
        assert sat.parse_values(data, "i;i") == [1, 2]
        assert sat.parse_values(data, "i;i;i") == [1, 2]

    def test_parse_floats(self):
        data = [sat.NULL_PTR, "1.0", "2.0", sat.NULL_PTR]
        assert sat.parse_values([], "f") == []
        assert sat.parse_values(data, "f") == [1.0]
        assert sat.parse_values(data, "f;f") == [1.0, 2.0]
        assert sat.parse_values(data, "f;f;f") == [1.0, 2.0]

    def test_parse_constant_strings(self):
        data = [sat.NULL_PTR, "1.0", "forward", sat.NULL_PTR]
        assert sat.parse_values([], "s") == []
        assert sat.parse_values(data, "s") == ["1.0"]
        assert sat.parse_values(data, "s;s") == ["1.0", "forward"]
        assert sat.parse_values(data, "s;s;s") == ["1.0", "forward"]

    def test_parse_user_strings(self):
        data = [sat.NULL_PTR, "@4", "usr1", "@4", "usr2", sat.NULL_PTR]
        assert sat.parse_values([], "@") == []
        assert sat.parse_values(data, "@") == ["usr1"]
        assert sat.parse_values(data, "@;@") == ["usr1", "usr2"]
        assert sat.parse_values(data, "@;@;@") == ["usr1", "usr2"]

    def test_parse_mixed_values(self):
        data = ["1.0", "@4", "usr1", "forward"]
        assert sat.parse_values(data, "f;@;s") == [1.0, "usr1", "forward"]

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


def test_parse_body_polygon_faces():
    builder = acis.parse_sat(PRISM)
    lumps = list(parsing.body_planar_polygon_faces(builder.bodies[0]))
    assert len(lumps) == 1
    faces = lumps[0]
    assert len(faces) == 10


def test_body_to_mesh():
    builder = acis.parse_sat(PRISM)
    meshes = acis.body_to_mesh(builder.bodies[0])
    assert len(meshes) == 1
    mesh = meshes[0]
    assert len(mesh.faces) == 10
    assert len(mesh.vertices) == 8


PRISM = """700 0 1 0 
@33 Open Design Alliance ACIS Builder @12 ACIS 32.0 NT @24 Sat Apr 23 14:32:04 2022 
1 9.9999999999999995e-007 1e-010 
body $-1 -1 $-1 $1 $-1 $-1 #
lump $-1 -1 $-1 $-1 $2 $0 #
shell $-1 -1 $-1 $-1 $-1 $3 $-1 $1 #
face $-1 -1 $-1 $4 $5 $2 $-1 $6 forward single #
face $-1 -1 $-1 $7 $8 $2 $-1 $9 forward single #
loop $-1 -1 $-1 $-1 $10 $3 #
plane-surface $-1 -1 $-1 -1.8993435776584597 -0.34550616434713 2 -0.21225108629643399 -0.6119059387325364 0.76191902359098318 -0.058576759801332381 -0.77031527097506436 -0.63496704364383372 forward_v I I I I #
face $-1 -1 $-1 $11 $12 $2 $-1 $13 forward single #
loop $-1 -1 $-1 $-1 $14 $4 #
plane-surface $-1 -1 $-1 -4.7139395277244951 -1.8595248078233979 0 -0.9152049609788877 0.19252196236278163 -0.3540270800484287 0.35569002591177251 -0.027047586873346612 -0.93421252052796389 forward_v I I I I #
coedge $-1 -1 $-1 $15 $16 $17 $18 reversed $5 $-1 #
face $-1 -1 $-1 $19 $20 $2 $-1 $21 forward single #
loop $-1 -1 $-1 $-1 $22 $7 #
plane-surface $-1 -1 $-1 -1.7432419444535392 2.2983491971566998 2 0.9973445351432173 -0.058886394872714735 -0.042851729473322366 0.042734476776907795 -0.0032496398237411763 0.99908118005276214 forward_v I I I I #
coedge $-1 -1 $-1 $23 $24 $25 $26 forward $8 $-1 #
coedge $-1 -1 $-1 $16 $10 $27 $28 forward $5 $-1 #
coedge $-1 -1 $-1 $10 $15 $29 $30 reversed $5 $-1 #
coedge $-1 -1 $-1 $31 $25 $10 $18 forward $20 $-1 #
edge $-1 -1 $-1 $32 0 $33 3.7701727831654939 $17 $34 forward @7 unknown #
face $-1 -1 $-1 $35 $36 $2 $-1 $37 forward single #
loop $-1 -1 $-1 $-1 $31 $11 #
plane-surface $-1 -1 $-1 -1.8993435776584597 -0.34550616434713 2 0.35424919523921139 -0.91480990045388144 0.19398544714470417 -0.016229036731927417 -0.21342038839667235 -0.97682565291016354 forward_v I I I I #
coedge $-1 -1 $-1 $29 $38 $39 $40 reversed $12 $-1 #
coedge $-1 -1 $-1 $24 $14 $41 $42 reversed $8 $-1 #
coedge $-1 -1 $-1 $14 $23 $43 $44 forward $8 $-1 #
coedge $-1 -1 $-1 $17 $31 $14 $26 reversed $20 $-1 #
edge $-1 -1 $-1 $32 0 $45 2.1386001334682128 $14 $46 forward @7 unknown #
coedge $-1 -1 $-1 $47 $48 $15 $28 reversed $49 $-1 #
edge $-1 -1 $-1 $32 0 $50 2.7374750783627975 $15 $51 forward @7 unknown #
coedge $-1 -1 $-1 $38 $22 $16 $30 forward $12 $-1 #
edge $-1 -1 $-1 $33 0 $50 3.140963148546323 $29 $52 forward @7 unknown #
coedge $-1 -1 $-1 $25 $17 $53 $54 reversed $20 $-1 #
vertex $-1 -1 $-1 $26 $55 #
vertex $-1 -1 $-1 $54 $56 #
straight-curve $-1 -1 $-1 -4.7139395277244951 -1.8595248078233979 0 0.74654296021490529 0.40157805240031325 0.53047966632467436 I I #
face $-1 -1 $-1 $57 $49 $2 $-1 $58 forward single #
loop $-1 -1 $-1 $-1 $59 $19 #
plane-surface $-1 -1 $-1 -4.7139395277244951 1.8182590221721908 2 -0.90029791640739398 -0.20794591431152187 0.38239006058428165 -0.39665189696405329 0.030162433186344435 -0.91747343299906914 forward_v I I I I #
coedge $-1 -1 $-1 $22 $29 $60 $61 forward $12 $-1 #
coedge $-1 -1 $-1 $62 $53 $22 $40 forward $63 $-1 #
edge $-1 -1 $-1 $33 0 $64 2.6484597207512501 $39 $65 forward @7 unknown #
coedge $-1 -1 $-1 $53 $62 $23 $42 forward $63 $-1 #
edge $-1 -1 $-1 $66 0 $45 3.6197563775917776 $41 $67 forward @7 unknown #
coedge $-1 -1 $-1 $59 $68 $24 $44 reversed $36 $-1 #
edge $-1 -1 $-1 $66 0 $32 4.1864177885367599 $24 $69 forward @7 unknown #
vertex $-1 -1 $-1 $54 $70 #
straight-curve $-1 -1 $-1 -4.7139395277244951 -1.8595248078233979 0 -0.34842491355310223 0.063383917862424019 0.93519118824544256 I I #
coedge $-1 -1 $-1 $71 $27 $68 $72 reversed $49 $-1 #
coedge $-1 -1 $-1 $27 $71 $73 $74 reversed $49 $-1 #
loop $-1 -1 $-1 $-1 $27 $35 #
vertex $-1 -1 $-1 $30 $75 #
straight-curve $-1 -1 $-1 -4.7139395277244951 -1.8595248078233979 0 0.94477707880540274 -0.32771370335085087 0 I I #
straight-curve $-1 -1 $-1 -1.8993435776584597 -0.34550616434713 2 -0.072682241539031203 -0.76763929572147338 -0.6367473623259875 I I #
coedge $-1 -1 $-1 $39 $41 $31 $54 forward $63 $-1 #
edge $-1 -1 $-1 $45 0 $33 3.8173156952508518 $53 $76 forward @7 unknown #
point $-1 -1 $-1 -4.7139395277244951 -1.8595248078233979 0 #
point $-1 -1 $-1 -1.8993435776584597 -0.34550616434713 2 #
face $-1 -1 $-1 $77 $78 $2 $-1 $79 forward single #
plane-surface $-1 -1 $-1 -2.1276358198862995 -2.7566329035843307 0 0 0 -1 0.075823670745747404 0.99712124185308604 0 forward_v I I I I #
coedge $-1 -1 $-1 $68 $43 $80 $81 reversed $36 $-1 #
coedge $-1 -1 $-1 $73 $82 $38 $61 reversed $83 $-1 #
edge $-1 -1 $-1 $50 0 $64 5.4498259321085127 $38 $84 forward @7 unknown #
coedge $-1 -1 $-1 $41 $39 $85 $86 reversed $63 $-1 #
loop $-1 -1 $-1 $-1 $53 $87 #
vertex $-1 -1 $-1 $86 $88 #
straight-curve $-1 -1 $-1 -1.8993435776584597 -0.34550616434713 2 0.058940535127580275 0.99826149546041998 0 I I #
vertex $-1 -1 $-1 $86 $89 #
straight-curve $-1 -1 $-1 -4.7139395277244951 1.8182590221721908 2 -0.20585406555013996 -0.97858270151095494 0 I I #
coedge $-1 -1 $-1 $43 $59 $47 $72 forward $36 $-1 #
straight-curve $-1 -1 $-1 -4.7139395277244951 1.8182590221721908 2 1.3877787807814457e-017 -0.87850377477042252 -0.47773540554800709 I I #
point $-1 -1 $-1 -5.4590810943528094 -1.7239719526230797 2 #
coedge $-1 -1 $-1 $48 $47 $90 $91 reversed $49 $-1 #
edge $-1 -1 $-1 $92 0 $32 2.567633724072949 $68 $93 forward @7 unknown #
coedge $-1 -1 $-1 $82 $60 $48 $74 forward $83 $-1 #
edge $-1 -1 $-1 $50 0 $94 4.9460245004234666 $73 $95 forward @7 unknown #
point $-1 -1 $-1 -2.1276358198862995 -2.7566329035843307 0 #
straight-curve $-1 -1 $-1 -5.4590810943528094 -1.7239719526230797 2 0.93252374204288202 0.36110866858376633 0 I I #
face $-1 -1 $-1 $87 $83 $2 $-1 $96 forward single #
loop $-1 -1 $-1 $-1 $97 $57 #
plane-surface $-1 -1 $-1 -4.7139395277244951 1.8182590221721908 2 -0.26318198707465013 0.86293276999111279 -0.43137254914389711 0.03462186912272304 0.45529583038369054 0.88966681011133308 forward_v I I I I #
coedge $-1 -1 $-1 $97 $90 $59 $81 forward $78 $-1 #
edge $-1 -1 $-1 $92 0 $66 2.3910080886789973 $80 $98 forward @7 unknown #
coedge $-1 -1 $-1 $60 $73 $99 $100 reversed $83 $-1 #
loop $-1 -1 $-1 $-1 $60 $77 #
straight-curve $-1 -1 $-1 -2.1276358198862995 -2.7566329035843307 0 0.070533239083480248 0.9275492765665786 0.36698419819552092 I I #
coedge $-1 -1 $-1 $99 $101 $62 $86 forward $102 $-1 #
edge $-1 -1 $-1 $66 0 $64 3.0092408855670816 $85 $103 forward @7 unknown #
face $-1 -1 $-1 $104 $63 $2 $-1 $105 forward single #
point $-1 -1 $-1 -1.7432419444535392 2.2983491971566998 2 #
point $-1 -1 $-1 -4.7139395277244951 1.8182590221721908 2 #
coedge $-1 -1 $-1 $80 $97 $71 $91 forward $78 $-1 #
edge $-1 -1 $-1 $94 0 $92 4.6883381143041722 $90 $106 forward @7 unknown #
vertex $-1 -1 $-1 $91 $107 #
straight-curve $-1 -1 $-1 -5.2917840802536293 0.64224229047115067 0 0.22504944810139033 -0.9743473435635055 0 I I #
vertex $-1 -1 $-1 $100 $108 #
straight-curve $-1 -1 $-1 -2.1276358198862995 -2.7566329035843307 0 0.26693459672279263 0.96371464711938482 0 I I #
plane-surface $-1 -1 $-1 -1.7432419444535392 2.2983491971566998 2 0.86559381815832204 -0.23975658922117712 0.43961815236762641 -0.44509782675002491 0.033846386626385921 0.89484207921551284 forward_v I I I I #
coedge $-1 -1 $-1 $90 $80 $101 $109 reversed $78 $-1 #
straight-curve $-1 -1 $-1 -5.2917840802536293 0.64224229047115067 0 0.24167402664387749 0.4918497504334145 0.83646726645118774 I I #
coedge $-1 -1 $-1 $101 $85 $82 $100 forward $102 $-1 #
edge $-1 -1 $-1 $64 0 $94 2.2268911813042807 $99 $110 forward @7 unknown #
coedge $-1 -1 $-1 $85 $99 $97 $109 forward $102 $-1 #
loop $-1 -1 $-1 $-1 $85 $104 #
straight-curve $-1 -1 $-1 -4.7139395277244951 1.8182590221721908 2 0.98719168595608686 0.1595386322467959 0 I I #
face $-1 -1 $-1 $-1 $102 $2 $-1 $111 forward single #
plane-surface $-1 -1 $-1 -5.4590810943528094 -1.7239719526230797 2 0 0 1 -0.075823670745747404 -0.99712124185308604 0 forward_v I I I I #
straight-curve $-1 -1 $-1 -0.80737076448470901 2.0099233524851008 0 -0.95650381999688194 -0.2917198010615189 0 I I #
point $-1 -1 $-1 -5.2917840802536293 0.64224229047115067 0 #
point $-1 -1 $-1 -0.80737076448470901 2.0099233524851008 0 #
edge $-1 -1 $-1 $94 0 $66 4.3929505707935217 $101 $112 forward @7 unknown #
straight-curve $-1 -1 $-1 -1.7432419444535392 2.2983491971566998 2 0.42025905344000414 -0.12951950552997801 -0.89811303614243443 I I #
plane-surface $-1 -1 $-1 -4.7139395277244951 1.8182590221721908 2 -0.15590940046942497 0.96473475883710602 -0.21208277614359863 0.016518332808874978 0.21722478431515085 0.97598183270000038 forward_v I I I I #
straight-curve $-1 -1 $-1 -0.80737076448470901 2.0099233524851008 0 -0.88928129289971092 -0.043629976532672143 0.45527486999215883 I I #
End-of-ACIS-data 
"""
if __name__ == "__main__":
    pytest.main([__file__])
